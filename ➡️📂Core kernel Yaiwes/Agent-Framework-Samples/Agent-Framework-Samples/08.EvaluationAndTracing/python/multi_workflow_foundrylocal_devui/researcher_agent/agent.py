"""Research / expansion agent for FoundryLocal workflow.

Consumes the structured plan (topic + outline) from the planning agent
and produces a first full draft. This is analogous to the evangelist
agent in the ghmodel example but with a different upstream signal.
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
	from agent_framework_foundry_local import FoundryLocalClient  # type: ignore
except ImportError:  # pragma: no cover
	raise SystemExit("agent_framework_foundry_local package not found. Install project dependencies first.")

RESEARCHER_AGENT_NAME = "Researcher-Agent"
RESEARCHER_AGENT_INSTRUCTIONS = "You are my researcher, working with me to analyze some questions"

try:
	model_id = os.environ.get("FOUNDRYLOCAL_MODEL", "qwen2.5-1.5b-instruct-generic-cpu:4")
	client = FoundryLocalClient(model=model_id)
	researcher_agent = client.as_agent(
		name=RESEARCHER_AGENT_NAME,
		instructions=RESEARCHER_AGENT_INSTRUCTIONS,
	)
except Exception as e:  # pragma: no cover
	print(f"[researcher_agent] initialization warning: {e}")
	researcher_agent = None  # type: ignore

