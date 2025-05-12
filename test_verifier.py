#!/usr/bin/env python3
import asyncio
from pathlib import Path
from autogen_sql.verifier_agent import VerifierAgent

async def main():
    # 1. Use the SQL from Step 4:
    sql = """
    SELECT 
        (SELECT COUNT(*) FROM customers WHERE Currency = 'EUR') * 1.0 /
        (SELECT COUNT(*) FROM customers WHERE Currency = 'CZK') AS ratio;
    """
    # 2. Point to your DB
    db_file = Path("data/mini_dev_data/minidev/MINIDEV/dev_databases") / "debit_card_specializing" / "debit_card_specializing.sqlite"
    print("Using:", db_file)
    question = "What is the ratio of customers who pay in EUR against customers who pay in CZK?"
    schema_summary = (
        "- customers(CustomerID, Currency)\n"
        "- transactions_1k(CustomerID)"
    )

    # 3. Run verifier
    verifier = VerifierAgent(model="mistral", temperature=0.0)
    final_sql = await verifier.verify(sql, str(db_file), question, schema_summary)
    print("\n---- Verified SQL ----")
    print(final_sql)

if __name__ == "__main__":
    asyncio.run(main())
