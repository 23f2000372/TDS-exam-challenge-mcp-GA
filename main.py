import hashlib
import json
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI()

EMAIL = "23f@ds.study.iitm.ac.in"
PROTOCOL_VERSION = "2024-11-05"


def rpc_result(request_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def rpc_error(request_id: Any, code: int, message: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


@app.get("/")
async def health():
    return {"status": "ok", "mcp_endpoint": "/mcp"}


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
            status_code=400,
        )

    if not isinstance(body, dict):
        return JSONResponse(rpc_error(None, -32600, "Invalid Request"), status_code=400)

    method = body.get("method")
    request_id = body.get("id")
    params = body.get("params") or {}

    # Notifications have no id and must not return a JSON-RPC body.
    if method == "notifications/initialized" and "id" not in body:
        return Response(status_code=202)

    if method == "initialize":
        result = {
            "protocolVersion": params.get("protocolVersion", PROTOCOL_VERSION),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "exam-challenge-mcp", "version": "1.0.0"},
        }
        return JSONResponse(rpc_result(request_id, result))

    if method == "ping":
        return JSONResponse(rpc_result(request_id, {}))

    if method == "tools/list":
        result = {
            "tools": [
                {
                    "name": "solve_challenge",
                    "description": "Returns the required SHA-256 challenge digest using the per-call HTTP header.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    },
                }
            ]
        }
        return JSONResponse(rpc_result(request_id, result))

    if method == "tools/call":
        tool_name = params.get("name")
        if tool_name != "solve_challenge":
            return JSONResponse(rpc_error(request_id, -32602, "Unknown tool"))

        # IMPORTANT: use the raw HTTP header from this individual request.
        challenge = request.headers.get("x-exam-challenge")
        if challenge is None:
            return JSONResponse(rpc_error(request_id, -32602, "Missing X-Exam-Challenge header"))

        normalized_email = EMAIL.strip().lower()
        digest = hashlib.sha256(f"{challenge}:{normalized_email}".encode("utf-8")).hexdigest()[:16]

        result = {
            "content": [{"type": "text", "text": digest}],
            "isError": False,
        }
        return JSONResponse(rpc_result(request_id, result))

    if method and "id" not in body:
        # Accept other notifications without a response.
        return Response(status_code=202)

    return JSONResponse(rpc_error(request_id, -32601, f"Method not found: {method}"))


# Render supplies PORT. Keep the server publicly reachable on all interfaces.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
