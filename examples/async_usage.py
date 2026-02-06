"""Async usage example for TealTiger Python SDK."""

import asyncio

from tealtiger import TealTiger


async def main():
    """Main async function."""
    # Use async context manager
    async with TealTiger(
        api_key="your-api-key",
        ssa_url="http://localhost:3000"
    ) as guard:
        # Execute tool asynchronously
        result = await guard.execute_tool(
            tool_name="database-query",
            parameters={"query": "SELECT * FROM users LIMIT 10"},
            context={"session_id": "session-789"}
        )
        
        if result.success:
            print(f"Query executed successfully!")
            print(f"Result: {result.data}")
        else:
            print(f"Query failed: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
