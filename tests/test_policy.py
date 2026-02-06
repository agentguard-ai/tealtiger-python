"""Tests for policy utilities."""

from tealtiger import PolicyBuilder, PolicyTester


def test_policy_builder():
    """Test policy builder."""
    policy = (
        PolicyBuilder()
        .name("test-policy")
        .description("Test policy description")
        .add_rule(
            condition={"tool_name": "file-write"},
            action="deny",
            reason="File writes not allowed"
        )
        .build()
    )

    assert policy.name == "test-policy"
    assert policy.description == "Test policy description"
    assert len(policy.rules) == 1
    assert policy.rules[0]["action"] == "deny"


def test_policy_builder_chaining():
    """Test policy builder method chaining."""
    policy = (
        PolicyBuilder()
        .name("multi-rule-policy")
        .description("Policy with multiple rules")
        .add_rule(
            condition={"tool_name": "file-write"},
            action="deny",
            reason="No writes"
        )
        .add_rule(
            condition={"tool_name": "file-read"},
            action="allow",
            reason="Reads allowed"
        )
        .build()
    )

    assert len(policy.rules) == 2


def test_policy_tester():
    """Test policy tester."""
    tester = PolicyTester()
    policy = (
        PolicyBuilder()
        .name("test-policy")
        .description("Test")
        .add_rule(
            condition={"tool_name": "test"},
            action="allow",
            reason="Test"
        )
        .build()
    )

    result = tester.test_policy(
        policy=policy,
        request={"tool_name": "test", "parameters": {}}
    )

    assert result.decision is not None
    assert result.reason is not None

