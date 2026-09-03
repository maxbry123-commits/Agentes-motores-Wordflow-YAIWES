# Copyright (c) 2026 Yunjue Tech
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


class EventParser:
    """Parse graph stream events into frontend-friendly message payloads."""

    def __init__(self) -> None:
        self._last_tool_msg_id: Optional[str] = None

    def parse(self, msg_type: str, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        if msg_type == "custom":
            return self._parse_custom(event)
        if msg_type == "updates":
            return self._parse_updates(event)
        return []

    def _parse_custom(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        messages = event.get("messages") or []
        if not messages:
            return []

        msg = messages[-1]
        if isinstance(msg, HumanMessage):
            content = msg.content
            if isinstance(content, str) and "Recur limit exceeded" in content:
                return [
                    {
                        "role": "executor",
                        "message_type": "system",
                        "content": "Recur limit exceeded",
                    }
                ]
            if len(messages) > 1 and isinstance(messages[-2], HumanMessage):
                prev = messages[-2]
                content = f"{prev.content}\n\n{content}"
            return [
                {
                    "role": "executor",
                    "message_type": "human",
                    "content": content,
                }
            ]

        if isinstance(msg, AIMessage):
            payload: Dict[str, Any] = {
                "role": "executor",
                "message_type": "ai",
                "content": msg.content,
            }
            tool_calls = self._extract_tool_calls(msg)
            if tool_calls:
                payload["tool_calls"] = tool_calls
            return [payload]

        if isinstance(msg, ToolMessage):
            tool_msg_id = getattr(msg, "id", None)
            if tool_msg_id and tool_msg_id == self._last_tool_msg_id:
                return []
            self._last_tool_msg_id = tool_msg_id
            return [
                {
                    "role": "executor",
                    "message_type": "tool",
                    "content": msg.content,
                    "tool_message_id": tool_msg_id,
                    "tool_call_id": getattr(msg, "tool_call_id", None),
                }
            ]

        if isinstance(msg, dict) and "context_summary" in msg:
            return [
                {
                    "role": "executor",
                    "message_type": "context_summary",
                    "content": msg.get("context_summary", ""),
                }
            ]

        return [
            {
                "role": "executor",
                "message_type": "other",
                "content": str(msg),
            }
        ]

    def _parse_updates(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        if "manager" in event:
            state = event["manager"] or {}
            if "required_tool_names" not in state:
                print("[EventParser] Manager state update missing 'required_tool_names'. Skipping.")
                return []
            task_context = self._coerce_dict(state.get("task_execution_context", {}) or {})
            pending_tool_requests = state.get("pending_tool_requests", []) or []
            pending_tool_requests = [self._coerce_dict(req) for req in pending_tool_requests]
            return [
                {
                    "role": "manager",
                    "message_type": "state_update",
                    "pending_tool_requests": pending_tool_requests,
                    "required_tool_names": state.get("required_tool_names", []),
                    "tool_usage_guidance": state.get("tool_usage_guidance", "") or "",
                    "context_summary": task_context.get("context_summary", ""),
                }
            ]

        if "tool_developer" in event:
            state = event["tool_developer"] or {}
            pending_present = "pending_tool_requests" in state
            pending_tool_requests = None
            if pending_present:
                pending_tool_requests = state.get("pending_tool_requests", []) or []
                pending_tool_requests = [
                    self._coerce_dict(req) for req in pending_tool_requests
                ]

            payload = {
                "role": "tool_developer",
                "message_type": "state_update",
                "created_tools": self._extract_bound_tools(state),
            }
            if pending_present:
                payload["pending_tool_requests"] = pending_tool_requests

            return [payload]

        if "integrator" in event:
            state = event["integrator"] or {}
            payload = state.get("final_answer", "")
            final_answer = ""
            reasoning_summary = ""
            if payload:
                try:
                    parsed = json.loads(payload)
                except json.JSONDecodeError:
                    parsed = {"final_answer": payload}
                final_answer = parsed.get("final_answer", "")
                reasoning_summary = parsed.get("reasoning_summary", "")
            return [
                {
                    "role": "integrator",
                    "message_type": "final_answer",
                    "content": final_answer,
                    "reasoning_summary": reasoning_summary,
                }
            ]

        return []

    @staticmethod
    def _extract_tool_calls(msg: AIMessage) -> List[Dict[str, Any]]:
        tool_calls = []
        raw_tool_calls = msg.additional_kwargs.get("tool_calls", [])
        for tool_call in raw_tool_calls:
            function = tool_call.get("function", {}) if isinstance(tool_call, dict) else {}
            name = function.get("name")
            args_raw = function.get("arguments", {})
            if isinstance(args_raw, str):
                try:
                    args = json.loads(args_raw)
                except json.JSONDecodeError:
                    args = {"_raw": args_raw}
            else:
                args = args_raw
            tool_calls.append({"name": name, "arguments": args})
        return tool_calls

    def _extract_bound_tools(self, state: Any) -> List[Dict[str, str]]:
        task_context = self._get_state_value(state, "task_execution_context")
        if not task_context:
            return []

        bound_tools = None
        if isinstance(task_context, dict):
            bound_tools = task_context.get("bound_tools")
        else:
            bound_tools = getattr(task_context, "bound_tools", None)

        if not bound_tools:
            return []

        created_tools = []
        for tool in bound_tools:
            if tool is None:
                continue
            if isinstance(tool, dict):
                name = tool.get("name") or tool.get("tool_name")
                desc = tool.get("description") or ""
            else:
                name = getattr(tool, "name", None) or getattr(tool, "__name__", None)
                desc = getattr(tool, "description", None) or tool.__doc__ or ""

            if name is None:
                name = type(tool).__name__

            created_tools.append({"name": str(name), "description": str(desc).strip()})

        return created_tools

    @staticmethod
    def _get_state_value(state: Any, key: str) -> Any:
        if isinstance(state, dict):
            return state.get(key)
        return getattr(state, key, None)

    @staticmethod
    def _coerce_dict(value: Any) -> Dict[str, Any]:
        if hasattr(value, "model_dump") and callable(value.model_dump):
            return value.model_dump()
        if hasattr(value, "dict") and callable(value.dict):
            return value.dict()
        if isinstance(value, dict):
            return value
        return {}