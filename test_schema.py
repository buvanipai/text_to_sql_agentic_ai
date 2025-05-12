import asyncio
from pathlib import Path
from autogen_sql.schema_agent import SchemaAgent

BASE_DATA_DIR = Path("data/mini_dev_data/minidev/MINIDEV")

async def test():
    db_folder = BASE_DATA_DIR / "dev_databases" / "debit_card_specializing"
    db_file = db_folder / "debit_card_specializing.sqlite"
    print(f"Using database file: {db_file}")
    
    agent = SchemaAgent(model="mistral", temperature=0.0)
    question = "What is the ratio of customers who pay in EUR against customers who pay in CZK?"
    summary = await agent.summarize(question, str(db_file))
    print("---- Schema Summary ----")
    print(summary)

if __name__ == "__main__":
    asyncio.run(test())
