"""Local HTTP server that exposes the weather tools as JSON and serves the UI.

Run:   python http_server.py        (listens on http://127.0.0.1:8787)
       python http_server.py 9000   (custom port)
"""

import asyncio
import json
import sys
from pathlib import Path
from aiohttp import web

from weather import current_weather, forecast

HERE = Path(__file__).parent


async def api_current(request: web.Request) -> web.Response:
    location = request.query.get("location", "").strip()
    units = request.query.get("units", "imperial")
    if not location:
        return web.json_response({"error": "missing location"}, status=400)
    try:
        return web.json_response(await current_weather(location, units))
    except ValueError as e:
        return web.json_response({"error": str(e)}, status=404)
    except Exception as e:
        return web.json_response({"error": f"{type(e).__name__}: {e}"}, status=502)


async def api_forecast(request: web.Request) -> web.Response:
    location = request.query.get("location", "").strip()
    units = request.query.get("units", "imperial")
    try:
        days = int(request.query.get("days", "5"))
    except ValueError:
        days = 5
    if not location:
        return web.json_response({"error": "missing location"}, status=400)
    try:
        return web.json_response(await forecast(location, days, units))
    except ValueError as e:
        return web.json_response({"error": str(e)}, status=404)
    except Exception as e:
        return web.json_response({"error": f"{type(e).__name__}: {e}"}, status=502)


async def index(request: web.Request) -> web.Response:
    return web.FileResponse(HERE / "weather.html")


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    app = web.Application()
    app.add_routes([
        web.get("/", index),
        web.get("/api/current", api_current),
        web.get("/api/forecast", api_forecast),
    ])
    print(f"Weatherly running at http://127.0.0.1:{port}", flush=True)
    web.run_app(app, host="127.0.0.1", port=port, print=None)


if __name__ == "__main__":
    main()
