"""Basic usage example for TealTiger Python SDK."""

from tealtiger import TealTiger

# Initialize the client
guard = TealTiger(
    api_key="your-api-key",
    ssa_url="http://localhost:3000"
)

# Synchronous execution
result = guard.execute_tool_sync(
    tool_name="web-search",
    parameters={"query": "AI agent security"},
    context={"session_id": "session-123", "user_id": "user-456"}
)

if result.success:
    print(f"Tool executed successfully!")
    print(f"Result: {result.data}")
    print(f"Security decision: {result.security_decision.allowed}")
else:
    print(f"Execution failed: {result.error}")
