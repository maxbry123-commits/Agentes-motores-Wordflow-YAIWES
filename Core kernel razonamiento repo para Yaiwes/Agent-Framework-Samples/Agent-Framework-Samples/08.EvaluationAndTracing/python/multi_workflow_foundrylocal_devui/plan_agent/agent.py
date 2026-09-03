"""Planning agent for the FoundryLocal workflow.

Parallels the evangelist/content generation agent in the GitHub Models
example but is focused purely on generating a structured plan that a
research agent can expand.
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
	from agent_framework_foundry_local import FoundryLocalClient  # type: ignore
except ImportError:  # pragma: no cover
	raise SystemExit("agent_framework_foundry_local package not found. Install project dependencies first.")

PLAN_AGENT_NAME = "Plan-Agent"
PLAN_AGENT_INSTRUCTIONS = """
You are my planner, working with me to create 1 sample based on the researcher's findings.
"""

try:
	model_id = os.environ.get("FOUNDRYLOCAL_MODEL", "qwen2.5-1.5b-instruct-generic-cpu:4")
	client = FoundryLocalClient(model=model_id)
	plan_agent = client.as_agent(
		name=PLAN_AGENT_NAME,
		instructions=PLAN_AGENT_INSTRUCTIONS,
	)
except Exception as e:  # pragma: no cover
	print(f"[plan_agent] initialization warning: {e}")
	plan_agent = None  # type: ignore

