"""Policy utilities for building and testing policies."""

from typing import Any, Dict

from tealtiger.types import Policy, PolicyTestResult


class PolicyBuilder:
    """Builder for creating security policies."""

    def __init__(self) -> None:
        """Initialize the policy builder."""
        self._policy: Dict[str, Any] = {
            "id": "",
            "name": "",
            "description": "",
            "rules": [],
            "enabled": True,
        }

    def name(self, name: str) -> "PolicyBuilder":
        """Set the policy name.

        Args:
            name: Policy name

        Returns:
            Self for chaining
        """
        self._policy["name"] = name
        return self

    def description(self, description: str) -> "PolicyBuilder":
        """Set the policy description.

        Args:
            description: Policy description

        Returns:
            Self for chaining
        """
        self._policy["description"] = description
        return self

    def add_rule(
        self,
        condition: Dict[str, Any],
        action: str,
        reason: str,
    ) -> "PolicyBuilder":
        """Add a rule to the policy.

        Args:
            condition: Rule condition
            action: Action to take (allow/deny/transform)
            reason: Reason for the action

        Returns:
            Self for chaining
        """
        self._policy["rules"].append(
            {
                "condition": condition,
                "action": action,
                "reason": reason,
            }
        )
        return self

    def build(self) -> Policy:
        """Build the policy.

        Returns:
            Constructed Policy object
        """
        # Generate ID if not set
        if not self._policy["id"]:
            self._policy["id"] = f"policy-{self._policy['name'].lower().replace(' ', '-')}"

        return Policy(**self._policy)


class PolicyTester:
    """Utility for testing policies."""

    def test_policy(
        self,
        policy: Policy,
        request: Dict[str, Any],
    ) -> PolicyTestResult:
        """Test a policy against a request.

        Args:
            policy: Policy to test
            request: Request to test against

        Returns:
            PolicyTestResult with decision and reasoning
        """
        # TODO: Implement policy testing logic
        return PolicyTestResult(
            decision="allow",
            reason="Policy testing not yet implemented",
            matched_rules=[],
        )
