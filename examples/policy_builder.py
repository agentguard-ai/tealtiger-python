"""Policy builder example for TealTiger Python SDK."""

from tealtiger import PolicyBuilder

# Build a policy using the fluent API
policy = (
    PolicyBuilder()
    .name("file-operations-policy")
    .description("Control file system operations")
    .add_rule(
        condition={"tool_name": "file-write"},
        action="deny",
        reason="File write operations are not allowed"
    )
    .add_rule(
        condition={"tool_name": "file-read"},
        action="allow",
        reason="File read operations are permitted"
    )
    .add_rule(
        condition={"tool_name": "file-delete"},
        action="deny",
        reason="File delete operations are not allowed"
    )
    .build()
)

print(f"Policy created: {policy.name}")
print(f"Description: {policy.description}")
print(f"Number of rules: {len(policy.rules)}")
print(f"\nRules:")
for i, rule in enumerate(policy.rules, 1):
    print(f"  {i}. {rule['action'].upper()}: {rule['reason']}")
