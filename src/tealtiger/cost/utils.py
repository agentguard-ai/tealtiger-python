"""Utility functions for cost tracking."""

import uuid


def generate_id() -> str:
    """Generate a unique ID for cost records, budgets, and alerts."""
    return str(uuid.uuid4())
