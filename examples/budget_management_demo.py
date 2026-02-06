"""
Budget Management Demo

Demonstrates budget creation, monitoring, and enforcement
"""

import asyncio
from tealtiger import (
    BudgetManager,
    CostTracker,
    InMemoryCostStorage,
    BudgetConfig,
    CostTrackerConfig,
)


async def main():
    """Demonstrate budget management features."""
    print("=== Budget Management Demo ===\n")

    # Initialize components
    storage = InMemoryCostStorage()
    tracker = CostTracker(CostTrackerConfig(enabled=True))
    budget_manager = BudgetManager(storage)

    # 1. Create different types of budgets
    print("1. Creating budgets with different periods...")
    
    daily_budget = budget_manager.create_budget(
        BudgetConfig(
            name="Daily Budget",
            limit=10.0,
            period="daily",
            alert_thresholds=[50, 75, 90],
            action="alert",
            enabled=True,
        )
    )
    
    weekly_budget = budget_manager.create_budget(
        BudgetConfig(
            name="Weekly Budget",
            limit=50.0,
            period="weekly",
            alert_thresholds=[80, 100],
            action="block",
            enabled=True,
        )
    )
    
    monthly_budget = budget_manager.create_budget(
        BudgetConfig(
            name="Monthly Budget",
            limit=200.0,
            period="monthly",
            alert_thresholds=[90, 100],
            action="block",
            enabled=True,
        )
    )

    print(f"   ✓ Created daily budget: ${daily_budget.limit}/day")
    print(f"   ✓ Created weekly budget: ${weekly_budget.limit}/week")
    print(f"   ✓ Created monthly budget: ${monthly_budget.limit}/month\n")

    # 2. Simulate API usage
    print("2. Simulating API usage...")
    for i in range(10):
        cost = tracker.calculate_actual_cost(
            request_id=f"req-{i}",
            agent_id="demo-agent",
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

    # 3. Check budget status
    print("3. Checking budget status...")
    
    for budget in [daily_budget, weekly_budget, monthly_budget]:
        status = await budget_manager.get_budget_status(budget.id)
        if status:
            print(f"\n   {budget.name}:")
            print(f"     - Limit: ${status.limit:.2f}")
            print(f"     - Spent: ${status.current_spending:.4f}")
            print(f"     - Remaining: ${status.remaining:.4f}")
            print(f"     - Usage: {status.percentage_used:.1f}%")
            print(f"     - Exceeded: {'Yes' if status.is_exceeded else 'No'}")
            
            if status.active_alerts:
                print(f"     - Active alerts: {', '.join(str(a) + '%' for a in status.active_alerts)}")
    print()

    # 4. Test budget enforcement
    print("4. Testing budget enforcement...")
    
    # Try to make a request that would exceed budget
    estimate = tracker.estimate_cost(
        model="gpt-4",
        usage={
            "input_tokens": 10000,
            "output_tokens": 5000,
            "total_tokens": 15000,
        },
        provider="openai"
    )
    
    budget_check = await budget_manager.check_budget("demo-agent", estimate.estimated_cost)
    
    print(f"   Estimated cost: ${estimate.estimated_cost:.4f}")
    print(f"   Request allowed: {budget_check.allowed}")
    
    if not budget_check.allowed and budget_check.blocked_by:
        print(f"   Blocked by: {budget_check.blocked_by.name}")
        print(f"   Reason: {budget_check.blocked_by.action}")
    
    if budget_check.alerts:
        print(f"   Alerts generated: {len(budget_check.alerts)}")
        for alert in budget_check.alerts:
            print(f"     - {alert.severity.upper()}: {alert.message}")
    print()

    # 5. View all alerts
    print("5. Viewing all alerts...")
    
    all_budgets = budget_manager.get_all_budgets()
    total_alerts = 0
    
    for budget in all_budgets:
        alerts = budget_manager.get_alerts(budget.id)
        if alerts:
            print(f"\n   {budget.name} ({len(alerts)} alerts):")
            for alert in alerts:
                print(f"     - {alert.threshold}% threshold: {alert.message}")
                total_alerts += 1
    
    print(f"\n   Total alerts across all budgets: {total_alerts}\n")

    # 6. Update budget configuration
    print("6. Updating budget configuration...")
    
    updated_budget = budget_manager.update_budget(
        daily_budget.id,
        BudgetConfig(
            name="Daily Budget (Updated)",
            limit=15.0,  # Increased limit
            period="daily",
            alert_thresholds=[60, 80, 95],
            action="alert",
            enabled=True,
        )
    )
    
    print(f"   ✓ Updated daily budget limit: ${daily_budget.limit} → ${updated_budget.limit}\n")

    # 7. Agent-scoped budgets
    print("7. Creating agent-scoped budgets...")
    
    agent1_budget = budget_manager.create_budget(
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
    
    agent2_budget = budget_manager.create_budget(
        BudgetConfig(
            name="Agent 2 Budget",
            limit=8.0,
            period="daily",
            alert_thresholds=[80, 100],
            action="block",
            scope={"type": "agent", "id": "agent-2"},
            enabled=True,
        )
    )
    
    print(f"   ✓ Created budget for agent-1: ${agent1_budget.limit}/day")
    print(f"   ✓ Created budget for agent-2: ${agent2_budget.limit}/day\n")

    # 8. Test agent-scoped enforcement
    print("8. Testing agent-scoped enforcement...")
    
    # Agent 1 makes requests
    for i in range(3):
        cost = tracker.calculate_actual_cost(
            request_id=f"agent1-req-{i}",
            agent_id="agent-1",
            model="gpt-4",
            usage={"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
            provider="openai"
        )
        await storage.store(cost)
        await budget_manager.record_cost(cost)
    
    # Check agent 1 budget
    agent1_status = await budget_manager.get_budget_status(agent1_budget.id)
    print(f"   Agent 1: ${agent1_status.current_spending:.4f} spent ({agent1_status.percentage_used:.1f}%)")
    
    # Agent 2 makes requests
    cost = tracker.calculate_actual_cost(
        request_id="agent2-req-1",
        agent_id="agent-2",
        model="gpt-4",
        usage={"input_tokens": 500, "output_tokens": 250, "total_tokens": 750},
        provider="openai"
    )
    await storage.store(cost)
    await budget_manager.record_cost(cost)
    
    # Check agent 2 budget
    agent2_status = await budget_manager.get_budget_status(agent2_budget.id)
    print(f"   Agent 2: ${agent2_status.current_spending:.4f} spent ({agent2_status.percentage_used:.1f}%)")
    print()

    print("=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
