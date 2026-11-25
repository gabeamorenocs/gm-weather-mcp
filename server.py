"""Weather MCP server (stdio)."""

from typing import Any
from mcp.server.mcpserver import MCPServer

from weather import current_weather, forecast

mcp = MCPServer("weather")


@mcp.tool()
async def get_current_weather(location: str, units: str = "imperial") -> dict[str, Any]:
    """Get the current weather for a location.

    `location` is a city name, e.g. "Paris" or "Austin, TX".
    `units` is "imperial" (°F / mph) or "metric" (°C / km·h).
    """
    return await current_weather(location, units)


@mcp.tool()
async def get_forecast(location: str, days: int = 5, units: str = "imperial") -> dict[str, Any]:
    """Get a daily weather forecast for a location.

    `days` is 1-16 (default 5).
    `units` is "imperial" or "metric".
    """
    return await forecast(location, days, units)


if __name__ == "__main__":
    mcp.run()
