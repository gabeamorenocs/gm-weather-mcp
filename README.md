# weather-mcp

An MCP server that fetches weather data from [Open-Meteo](https://open-meteo.com) — no API key required.

## Tools

- `get_current_weather(location)` — current conditions for a city (e.g. `"Paris"`, `"Austin, TX"`)
- `get_forecast(location, days=5)` — daily forecast, 1–16 days

Both tools geocode the location name, then call Open-Meteo.

## Install

```bash
pip install "mcp[cli]" httpx
```

## Run / test

```bash
mcp dev server.py
```

## Wire into Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/Users/gabrielmoreno/Documents/Claude Projects/11:24:2026/mcp1/server.py"]
    }
  }
}
```

Restart Claude Code. Tools appear as `mcp__weather__get_current_weather` and `mcp__weather__get_forecast`.
