# Copyright (c) 2026 Yunjue Tech
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from src.core import build_graph
from src.utils.event_parser import EventParser

GraphEvent = Tuple[str, Dict[str, Any]]
EventSource = Callable[["ChatRequest"], AsyncIterator[GraphEvent]]


def log(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}][backend] {message}", flush=True)


class ChatRequest(BaseModel):
    user_query: str = Field(..., description="User query content")
    thread_id: str = Field("chat", description="Thread/session id")
    dynamic_tools_dir: Optional[str] = Field(None, description="Private dynamic tools directory")
    dynamic_tools_public_dir: str = Field(
        "./output/dynamic_tools_public", description="Public dynamic tools directory"
    )


def _default_dynamic_tools_dir(thread_id: str) -> str:
    return f"./output/private_dynamic_tools/dynamic_tools_{thread_id}"


graph = build_graph().compile()
WEB_DEMO_DIR = Path(__file__).resolve().parent
FRONTEND_FILE = WEB_DEMO_DIR / "index.html"
ICONS_DIR = WEB_DEMO_DIR / "icons"


async def graph_event_stream(req: ChatRequest) -> AsyncIterator[GraphEvent]:
    initial_state = {"user_query": req.user_query}
    dynamic_tools_dir = req.dynamic_tools_dir or _default_dynamic_tools_dir(req.thread_id)
    config = {
        "configurable": {
            "thread_id": req.thread_id,
            "dynamic_tools_dir": dynamic_tools_dir,
            "dynamic_tools_public_dir": req.dynamic_tools_public_dir,
        }
    }
    async for msg_type, event in graph.astream(
        initial_state,
        config=config,
        stream_mode=["custom", "updates"],
    ):
        yield msg_type, event


def _resolve_private_tools_dir(req: ChatRequest) -> Path:
    return Path(req.dynamic_tools_dir or _default_dynamic_tools_dir(req.thread_id))


def _resolve_public_tools_dir(req: ChatRequest) -> Path:
    return Path(req.dynamic_tools_public_dir)


def _promote_private_tools_to_public(req: ChatRequest) -> int:
    private_dir = _resolve_private_tools_dir(req)
    public_dir = _resolve_public_tools_dir(req)
    if not private_dir.exists() or not private_dir.is_dir():
        log(f"No private tools directory to promote: {private_dir}")
        return 0

    public_dir.mkdir(parents=True, exist_ok=True)
    moved_count = 0
    for tool_file in private_dir.glob("*.py"):
        target_file = public_dir / tool_file.name
        if target_file.exists():
            target_file.unlink()
        shutil.move(str(tool_file), str(target_file))
        moved_count += 1

    log(
        f"Promoted private tools thread_id={req.thread_id} moved={moved_count} "
        f"from={private_dir} to={public_dir}"
    )
    return moved_count


def create_app(event_source: EventSource = graph_event_stream) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_class=FileResponse)
    async def frontend() -> FileResponse:
        log("GET / requested")
        if not FRONTEND_FILE.exists():
            log(f"frontend file not found: {FRONTEND_FILE}")
            raise HTTPException(status_code=404, detail="web_demo/index.html not found")
        log(f"serving frontend file: {FRONTEND_FILE}")
        return FileResponse(FRONTEND_FILE)

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> FileResponse:
        icon_file = ICONS_DIR / "yunjue.svg"
        if not icon_file.exists():
            raise HTTPException(status_code=404, detail="favicon not found")
        return FileResponse(icon_file, media_type="image/svg+xml")

    @app.get("/icons/{icon_name}")
    async def icon(icon_name: str) -> FileResponse:
        icon_file = (ICONS_DIR / icon_name).resolve()
        if icon_file.parent != ICONS_DIR.resolve():
            raise HTTPException(status_code=404, detail="icon not found")
        if not icon_file.exists() or not icon_file.is_file():
            raise HTTPException(status_code=404, detail="icon not found")
        return FileResponse(icon_file)

    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        log("GET /health")
        return {"status": "ok"}

    @app.post("/chat")
    async def chat(req: ChatRequest) -> JSONResponse:
        log(f"POST /chat thread_id={req.thread_id}")
        parser = EventParser()
        payloads = []
        event_count = 0
        async for msg_type, event in event_source(req):
            event_count += 1
            log(f"/chat step={event_count} msg_type={msg_type} event={event}")
            parsed_payloads = parser.parse(msg_type, event)
            if parsed_payloads:
                log(f"/chat step={event_count} parsed_payloads={parsed_payloads}")
            payloads.extend(parsed_payloads)
        log(f"POST /chat completed thread_id={req.thread_id} events={event_count} payloads={len(payloads)}")
        _promote_private_tools_to_public(req)
        return JSONResponse({"messages": payloads})

    @app.post("/chat/stream")
    async def chat_stream(req: ChatRequest) -> StreamingResponse:
        log(f"POST /chat/stream thread_id={req.thread_id}")
        parser = EventParser()

        async def event_generator() -> AsyncIterator[str]:
            event_count = 0
            payload_count = 0
            async for msg_type, event in event_source(req):
                event_count += 1
                payloads = parser.parse(msg_type, event)
                if payloads:
                    log(f"/chat/stream step={event_count} parsed_payloads={payloads}")

                for payload in payloads:
                    encoded = json.dumps(payload, ensure_ascii=False)
                    payload_count += 1
                    yield f"data: {encoded}\n\n"
            log(
                f"POST /chat/stream completed thread_id={req.thread_id} "
                f"events={event_count} payloads={payload_count}"
            )
            _promote_private_tools_to_public(req)

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return app


app = create_app()
