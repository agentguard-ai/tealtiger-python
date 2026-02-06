"""
Cost Tracking Demo

Demonstrates how to use the cost tracking and budget management features
"""

import asyncio
from tealtiger import (
    CostTracker,
    BudgetManager,
    InMemoryCostStorage,
    CostTrackerConfig,
    BudgetConfig,
)


async def demonstrate_cost_tracking():
    """Demonstrate basic cost tracking functionality."""
    print("=== Cost Tracking Demo ===\n")

    # Initialize storage
    storage = InMemoryCostStorage()

    # Initialize cost tracker
    tracker_config = CostTrackerConfig(
        enabled=True,
        persist_records=True,
        enable_budgets=True,
        enable_alerts=True,
    )
    tracker = CostTracker(tracker_config)

    # 1. Estimate cost before making a request
    print("1. Estimating cost for GPT-4 request...")
    estimate = tracker.estimate_cost(
        model="gpt-4",
        usage={
            "input_tokens": 1000,
            "output_tokens": 500,
            "total_tokens": 1500,
        },
        provider="openai"
    )

    print(f"   Estimated cost: ${estimate.estimated_cost:.4f}")
    print(f"   Input cost: ${estimate.breakdown.input_cost:.4f}")
    print(f"   Output cost: ${estimate.breakdown.output_cost:.4f}\n")

    # 2. Calculate actual cost after request
    print("2. Calculating actual cost...")
    actual_cost = tracker.calculate_actual_cost(
        request_id="req-123",
        agent_id="agent-456",
        model="gpt-4",
        usage={
            "input_tokens": 1050,
            "output_tokens": 480,
            "total_tokens": 1530,
        },
        provider="openai"
    )

    print(f"   Actual cost: ${actual_cost.actual_cost:.4f}")
    print(f"   Cost record ID: {actual_cost.id}\n")

    # 3. Store the cost record
    await storage.store(actual_cost)
    print("3. Cost record stored successfully\n")

    # 4. Query costs by agent
    print("4. Querying costs by agent...")
    agent_costs = await storage.get_by_agent_id("agent-456")
    total_cost = sum(r.actual_cost for r in agent_costs)
    print(f"   Found {len(agent_costs)} cost records for agent-456")
    print(f"   Total cost: ${total_cost:.4f}\n")


async def demonstrate_budget_management():
    """Demonstrate budget management functionality."""
    print("=== Budget Management Demo ===\n")

    # Initialize storage and managers
    storage = InMemoryCostStorage()
    tracker = CostTracker(CostTrackerConfig(enabled=True))
    budget_manager = BudgetManager(storage)

    # 1. Create a daily budget
    print("1. Creating daily budget...")
    budget = budget_manager.create_budget(
        BudgetConfig(
            name="Daily GPT-4 Budget",
            limit=10.0,
            period="daily",
            alert_thresholds=[50, 75, 90, 100],
            action="alert",
            enabled=True,
        )
    )

    print(f"   Budget created: {budget.name}")
    print(f"   Limit: ${budget.limit}")
    print(f"   Period: {budget.period}")
    print(f"   Alert thresholds: {', '.join(str(t) + '%' for t in budget.alert_thresholds)}\n")

    # 2. Check budget before making a request
    print("2. Checking budget before request...")
    estimate = tracker.estimate_cost(
        model="gpt-4",
        usage={
            "input_tokens": 1000,
            "output_tokens": 500,
            "total_tokens": 1500,
        },
        provider="openai"
    )

    budget_check = await budget_manager.check_budget("agent-789", estimate.estimated_cost)

    if budget_check.allowed:
        print("   ✓ Request allowed - within budget")
    else:
        print("   ✗ Request blocked - budget exceeded")
        if budget_check.blocked_by:
            print(f"   Blocked by: {budget_check.blocked_by.name}")

    if budget_check.alerts:
        print(f"   ⚠ {len(budget_check.alerts)} alert(s) generated:")
        for alert in budget_check.alerts:
            print(f"     - {alert.severity.upper()}: {alert.message}")
    print()

    # 3. Simulate some spending
    print("3. Simulating API requests...")
    for i in range(5):
        cost = tracker.calculate_actual_cost(
            request_id=f"req-{i}",
            agent_id="agent-789",
            model="gpt-4",
            usage={
                "input_tokens": 1000,
                "output_tokens": 500,
                "total_tokens": 1500,
            },
            provider="openai"
        )

        await storage.store(cost)
        await budget_manager.record_cost(cost)
        print(f"   Request {i + 1}: ${cost.actual_cost:.4f}")
    print()

    # 4. Check budget status
    print("4. Checking budget status...")
    status = await budget_manager.get_budget_status(budget.id)

    if status:
        print(f"   Current spending: ${status.current_spending:.4f}")
        print(f"   Remaining: ${status.remaining:.4f}")
        print(f"   Percentage used: {status.percentage_used:.2f}%")
        print(f"   Is exceeded: {'Yes' if status.is_exceeded else 'No'}")
        
        if status.active_alerts:
            print(f"   Active alerts: {', '.join(str(a) + '%' for a in status.active_alerts)}")
    print()

    # 5. Get all alerts
    print("5. Checking alerts...")
    alerts = budget_manager.get_alerts(budget.id)
    print(f"   Total alerts: {len(alerts)}")
    
    for index, alert in enumerate(alerts, 1):
        print(f"   Alert {index}:")
        print(f"     - Threshold: {alert.threshold}%")
        print(f"     - Severity: {alert.severity}")
        print(f"     - Message: {alert.message}")
        print(f"     - Acknowledged: {'Yes' if alert.acknowledged else 'No'}")
    print()


async def demonstrate_agent_scoped_budgets():
    """Demonstrate agent-scoped budget isolation."""
    print("=== Agent-Scoped Budgets Demo ===\n")

    # Initialize storage and managers
    storage = InMemoryCostStorage()
    tracker = CostTracker(CostTrackerConfig(enabled=True))
    budget_manager = BudgetManager(storage)

    # 1. Create agent-specific budgets
    print("1. Creating agent-specific budgets...")
    
    budget1 = budget_manager.create_budget(
        BudgetConfig(
            name="Agent 1 Budget",
            limit=5.0,
            period="daily",
            alert_thresholds=[80, 100],
            action="block",
            scope={"type": "agent", "id": "agent-1"},
            enabled=True,
        )
    )

    budget2 = budget_manager.create_budget(
        BudgetConfig(
            name="Agent 2 Budget",
            limit=10.0,
            period="daily",
            alert_thresholds=[80, 100],
            action="block",
            scope={"type": "agent", "id": "agent-2"},
            enabled=True,
        )
    )

    print(f"   Created budget for agent-1: ${budget1.limit} limit")
    print(f"   Created budget for agent-2: ${budget2.limit} limit\n")

    # 2. Make requests for both agents
    print("2. Making requests for both agents...")
    
    # Agent 1 makes 3 requests
    for i in range(3):
        cost = tracker.calculate_actual_cost(
            request_id=f"agent1-req-{i}",
            agent_id="agent-1",
            model="gpt-4",
            usage={
                "input_tokens": 2000,
                "output_tokens": 1000,
                "total_tokens": 3000,
            },
            provider="openai"
        )
        await storage.store(cost)
        await budget_manager.record_cost(cost)
    print("   Agent 1: Made 3 requests")

    # Agent 2 makes 1 request
    cost2 = tracker.calculate_actual_cost(
        request_id="agent2-req-1",
        agent_id="agent-2",
        model="gpt-4",
        usage={
            "input_tokens": 1000,
            "output_tokens": 500,
            "total_tokens": 1500,
        },
        provider="openai"
    )
    await storage.store(cost2)
    await budget_manager.record_cost(cost2)
    print("   Agent 2: Made 1 request\n")

    # 3. Check budget status for each agent
    print("3. Checking budget status...")
    
    status1 = await budget_manager.get_budget_status(budget1.id)
    status2 = await budget_manager.get_budget_status(budget2.id)

    print("   Agent 1:")
    print(f"     - Spending: ${status1.current_spending:.4f}")
    print(f"     - Percentage: {status1.percentage_used:.2f}%")
    print(f"     - Exceeded: {'Yes' if status1.is_exceeded else 'No'}")

    print("   Agent 2:")
    print(f"     - Spending: ${status2.current_spending:.4f}")
    print(f"     - Percentage: {status2.percentage_used:.2f}%")
    print(f"     - Exceeded: {'Yes' if status2.is_exceeded else 'No'}")
    print()


async def demonstrate_multi_model_support():
    """Demonstrate cost comparison across different models."""
    print("=== Multi-Model Support Demo ===\n")

    tracker = CostTracker(CostTrackerConfig(enabled=True))

    print("1. Comparing costs across different models...\n")

    models = [
        {"name": "GPT-4", "model": "gpt-4", "provider": "openai"},
        {"name": "GPT-3.5 Turbo", "model": "gpt-3.5-turbo", "provider": "openai"},
        {"name": "Claude 3 Opus", "model": "claude-3-opus-20240229", "provider": "anthropic"},
        {"name": "Claude 3 Sonnet", "model": "claude-3-sonnet-20240229", "provider": "anthropic"},
    ]

    tokens = {
        "input_tokens": 1000,
        "output_tokens": 500,
        "total_tokens": 1500,
    }

    for model_info in models:
        estimate = tracker.estimate_cost(
            model=model_info["model"],
            usage=tokens,
            provider=model_info["provider"]
        )
        print(f"   {model_info['name']}:")
        print(f"     - Estimated cost: ${estimate.estimated_cost:.4f}")
        print(f"     - Input cost: ${estimate.breakdown.input_cost:.4f}")
        print(f"     - Output cost: ${estimate.breakdown.output_cost:.4f}")
        print()


async def demonstrate_custom_pricing():
    """Demonstrate custom pricing for models."""
    print("=== Custom Pricing Demo ===\n")

    tracker = CostTracker(CostTrackerConfig(enabled=True))

    print("1. Adding custom pricing for a model...")
    
    # Add custom pricing for a hypothetical model
    from tealtiger.cost.types import ModelPricing
    from datetime import datetime
    
    tracker.add_custom_pricing(
        "custom-model-v1",
        ModelPricing(
            model="custom-model-v1",
            provider="custom",
            input_cost_per_1k=0.01,
            output_cost_per_1k=0.02,
            last_updated=datetime.now().isoformat(),
        )
    )

    print("   Custom pricing added for custom-model-v1\n")

    # Estimate cost with custom pricing
    print("2. Estimating cost with custom pricing...")
    estimate = tracker.estimate_cost(
        model="custom-model-v1",
        usage={
            "input_tokens": 1000,
            "output_tokens": 500,
            "total_tokens": 1500,
        }
    )

    print(f"   Estimated cost: ${estimate.estimated_cost:.4f}")
    print(f"   Input cost: ${estimate.breakdown.input_cost:.4f}")
    print(f"   Output cost: ${estimate.breakdown.output_cost:.4f}\n")


async def main():
    """Run all demos."""
    try:
        await demonstrate_cost_tracking()
        await demonstrate_budget_management()
        await demonstrate_agent_scoped_budgets()
        await demonstrate_multi_model_support()
        await demonstrate_custom_pricing()

        print("=== Demo Complete ===")
    except Exception as error:
        print(f"Error running demo: {error}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
