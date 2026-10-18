# Exam Challenge MCP Server

A minimal JSON-RPC MCP server for the exam's `solve_challenge` tool.

## Deploy on Render

1. Push these files to a GitHub repository.
2. In Render, choose **New + → Web Service** and connect the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. After deployment, use `https://YOUR-SERVICE.onrender.com/mcp` as the public MCP endpoint.

The `/` route is only a health check. The MCP endpoint is `/mcp`.

## Behavior

- `initialize` advertises tools capability.
- `notifications/initialized` is accepted with HTTP 202 and no body.
- `tools/list` returns exactly one tool: `solve_challenge`.
- `tools/call` reads `X-Exam-Challenge` from that HTTP request's headers and returns the first 16 lowercase hex characters of SHA-256 of `challenge:23f@ds.study.iitm.ac.in`.

No signature verification is performed because the exam says it is optional.
