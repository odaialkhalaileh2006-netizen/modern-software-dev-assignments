import asyncio

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from server import mcp


def call(tool, args):
    async def run():
        async with Client(mcp) as client:
            return await client.call_tool(tool, args)
    return asyncio.run(run())


def test_tools_are_listed():
    async def run():
        async with Client(mcp) as client:
            return await client.list_tools()
    tools = asyncio.run(run())
    assert {t.name for t in tools} == {"list_events", "get_event", "create_event"}


def test_end_before_start_returns_structured_error():
    result = call("create_event", {"title": "t", "start": "2026-10-25T15:00:00", "end": "2026-10-25T14:00:00"})
    assert result.data["retryable"] is False
    assert "error" in result.data


def test_days_ahead_above_limit_is_rejected():
    with pytest.raises(ToolError):
        call("list_events", {"days_ahead": 500})