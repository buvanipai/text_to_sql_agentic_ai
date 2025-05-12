#!/usr/bin/env python3
import asyncio
from autogen_sql.planner_agent import PlannerAgent

async def main():
    # 1) Example inputs
    question = "What is the ratio of customers who pay in EUR against customers who pay in CZK?"
    schema_summary = (
        "- customers(CustomerID, Currency)\n"
        "- transactions_1k(CustomerID)"
    )
    # Mini-Dev often has no extra evidence for this db
    evidence = "None"

    # 2) Instantiate and run
    planner = PlannerAgent(model="mistral", temperature=0.0)
    plan = await planner.plan(question, schema_summary, evidence)

    # 3) Show the plan
    print("---- Generated Plan ----")
    print(plan)

if __name__ == "__main__":
    asyncio.run(main())