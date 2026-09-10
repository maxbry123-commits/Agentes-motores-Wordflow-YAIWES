"""Conditional Workflow for Content Review with Azure AI Foundry Agents"""

import os
from dataclasses import dataclass

from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

from agent_framework import (
    Agent,
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    Message,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from agent_framework.foundry import FoundryChatClient

from evangelist_agent import EVANGELIST_NAME, EVANGELIST_INSTRUCTIONS
from contentreview_agent import ReviewAgent, REVIEWER_NAME, REVIEWER_INSTRUCTIONS
from publisher_agent import PUBLISHER_NAME, PUBLISHER_INSTRUCTIONS

# Load environment variables
load_dotenv()


@dataclass
class ReviewResult:
    """Data class to hold review results"""
    review_result: str
    reason: str
    draft_content: str


@executor(id="to_reviewer_result")
async def to_reviewer_result(
    response: AgentExecutorResponse, 
    ctx: WorkflowContext[ReviewResult]
) -> None:
    """Convert reviewer agent response to structured format"""
    response_text = response.agent_response.text.strip()
    print(f"🔍 [Workflow] Raw response from reviewer agent: {response_text}")
    
    parsed = ReviewAgent.model_validate_json(response_text)
    await ctx.send_message(
        ReviewResult(
            review_result=parsed.review_result,
            reason=parsed.reason,
            draft_content=parsed.draft_content,
        )
    )


def select_targets(review: ReviewResult, target_ids: list[str]) -> list[str]:
    """
    Select workflow path based on review result
    
    Args:
        review: The review result containing decision
        target_ids: List of [handle_review_id, save_draft_id]
    
    Returns:
        List containing the selected target executor ID
    """
    handle_review_id, save_draft_id = target_ids
    if review.review_result == "Yes":
        print(f"✅ [Workflow] Review passed - routing to save_draft")
        return [save_draft_id]
    else:
        print(f"❌ [Workflow] Review failed - routing to handle_review")
        return [handle_review_id]


@executor(id="handle_review")
async def handle_review(review: ReviewResult, ctx: WorkflowContext[str]) -> None:
    """Handle review failures"""
    if review.review_result == "No":
        message = f"Review failed: {review.reason}, please revise the draft."
        print(f"⚠️ [Workflow] {message}")
        await ctx.yield_output(message)
    else:
        await ctx.send_message(
            AgentExecutorRequest(
                messages=[Message("user", contents=review.draft_content)], 
                should_respond=True
            )
        )


@executor(id="save_draft")
async def save_draft(review: ReviewResult, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    """Save draft content by sending to publisher agent"""
    # Only called for approved drafts by selection_func
    await ctx.send_message(
        AgentExecutorRequest(
            messages=[Message("user", contents=review.draft_content)], 
            should_respond=True
        )
    )


# Keep credential and client alive — they must not be closed while DevUI serves.
# main.py runs create_workflow() and uvicorn in a single asyncio.run(),
# so the references here keep the HTTP sessions alive for the entire process.
_credential = None
_client = None


async def create_workflow():
    """Create the conditional workflow with Azure AI Foundry agents.

    The credential and client are stored as module globals so they
    remain alive for the duration of the process. main.py ensures that
    create_workflow() and uvicorn run in the same event loop.
    """
    global _credential, _client

    _credential = AzureCliCredential()
    _client = FoundryChatClient(credential=_credential)

    # Create web search tool and code interpreter tool
    web_search_tool = FoundryChatClient.get_web_search_tool()
    code_interpreter_tool = FoundryChatClient.get_code_interpreter_tool()

    # Create evangelist agent with web search tool
    evangelist_agent_obj = Agent(
        client=_client,
        name=EVANGELIST_NAME,
        instructions=EVANGELIST_INSTRUCTIONS,
        tools=[web_search_tool],
    )
    evangelist_executor = AgentExecutor(evangelist_agent_obj, id="evangelist_agent")
    
    # Create reviewer agent (no tools needed)
    reviewer_agent_obj = Agent(
        client=_client,
        name=REVIEWER_NAME,
        instructions=REVIEWER_INSTRUCTIONS,
    )
    reviewer_executor = AgentExecutor(reviewer_agent_obj, id="reviewer_agent")
    
    # Create publisher agent with code interpreter tool
    publisher_agent_obj = Agent(
        client=_client,
        name=PUBLISHER_NAME,
        instructions=PUBLISHER_INSTRUCTIONS,
        tools=[code_interpreter_tool],
    )
    publisher_executor = AgentExecutor(publisher_agent_obj, id="publisher_agent")

    # Build the conditional workflow
    workflow = (
        WorkflowBuilder(start_executor=evangelist_executor)
        .add_edge(evangelist_executor, reviewer_executor)
        .add_edge(reviewer_executor, to_reviewer_result)
        .add_multi_selection_edge_group(
            to_reviewer_result,
            [handle_review, save_draft],
            selection_func=select_targets,
        )
        .add_edge(save_draft, publisher_executor)
        .build()
    )
    
    return workflow

