# Copyright (c) Microsoft. All rights reserved.
"""Foundry-based weather agent for Agent Framework Debug UI.

This agent uses Azure AI Foundry with Azure CLI authentication.
"""

import asyncio
import os
from typing import Annotated

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from pydantic import Field
from dotenv import load_dotenv  # 📁 Secure configuration loading

load_dotenv()  # 📁 Load environment variables from .env file


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    temperature = 22
    return f"The weather in {location} is {conditions[0]} with a high of {temperature}°C."


def get_forecast(
    location: Annotated[str, Field(description="The location to get the forecast for.")],
    days: Annotated[int, Field(description="Number of days for forecast")] = 3,
) -> str:
    """Get weather forecast for multiple days."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    forecast: list[str] = []

    for day in range(1, days + 1):
        condition = conditions[day % len(conditions)]
        temp = 18 + day
        forecast.append(f"Day {day}: {condition}, {temp}°C")

    return f"Weather forecast for {location}:\n" + "\n".join(forecast)


async def _foundry_setup():
    """Setup Foundry agent with hosted tools."""
    credential = AzureCliCredential()
    client = FoundryChatClient(credential=credential)
    
    agent = Agent(
        client=client,
        name="FoundryWeatherAgent",
        instructions="""You are a weather assistant using Azure AI Foundry models. You can provide
current weather information and forecasts for any location. Always be helpful
and provide detailed weather information when asked.""",
        tools=[get_weather, get_forecast],
    )
    
    return agent


def main():
    """Launch the Foundry weather agent in DevUI."""
    import logging

    from agent_framework.devui import serve

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Foundry Weather Agent")
    logger.info("Available at: http://localhost:8090")
    logger.info("Entity ID: agent_FoundryWeatherAgent")

    # Setup agent synchronously
    agent = asyncio.run(_foundry_setup())

    # Launch server with the agent
    serve(entities=[agent], port=8090, auto_open=True)


if __name__ == "__main__":
    main()