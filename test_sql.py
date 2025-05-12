#!/usr/bin/env python3
import asyncio
from autogen_sql.sql_agent import SQLAgent

async def main():
    question = "What is the ratio of customers who pay in EUR against customers who pay in CZK?"
    schema_summary = (
        "- customers(CustomerID, Currency)\n"
        "- transactions_1k(CustomerID)"
    )
    plan = (
        "1. Count customers in `customers` where Currency = 'EUR'.\n"
        "2. Count customers in `customers` where Currency = 'CZK'.\n"
        "3. Compute ratio: EUR_count / CZK_count."
    )

    agent = SQLAgent(model="mistral", temperature=0.0)
    sql = await agent.generate(question, schema_summary, plan)

    print("---- Generated SQL ----")
    print(sql)

if __name__ == "__main__":
    asyncio.run(main())