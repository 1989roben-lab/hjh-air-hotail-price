#!/usr/bin/env python3
"""Small, dependency-free client for PriceWin's public Streamable HTTP MCP."""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = "https://mcp.price.win/mcp"
HEADERS = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json",
    "MCP-Protocol-Version": "2025-06-18",
    "User-Agent": "hjh-jipiaojiudian-price/1.0",
}


def request(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode("utf-8")
    req = Request(ENDPOINT, payload, HEADERS, method="POST")
    with urlopen(req, timeout=60) as response:
        body = response.read().decode("utf-8")
        if "text/event-stream" not in response.headers.get("Content-Type", ""):
            return json.loads(body)
        for line in body.splitlines():
            if line.startswith("data: "):
                message = json.loads(line[6:])
                if "result" in message or "error" in message:
                    return message
    raise ValueError("MCP server returned no result")


def main():
    parser = argparse.ArgumentParser(description="Call the public PriceWin MCP without a login or API key")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ping", help="Check whether the MCP endpoint responds")
    call = sub.add_parser("call", help="Call a PriceWin MCP tool")
    call.add_argument("tool")
    call.add_argument("arguments", help="JSON object of tool arguments")
    args = parser.parse_args()
    try:
        if args.command == "ping":
            result = request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "hjh-jipiaojiudian-price", "version": "1.0"}})
        else:
            arguments = json.loads(args.arguments)
            if not isinstance(arguments, dict):
                raise ValueError("arguments must be a JSON object")
            result = request("tools/call", {"name": args.tool, "arguments": arguments})
        if "error" in result or result.get("result", {}).get("isError"):
            print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        data = result.get("result", {}).get("structuredContent", result.get("result", {}))
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    except (HTTPError, URLError, ValueError, TimeoutError) as exc:
        print(f"PriceWin MCP request failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
