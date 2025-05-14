import json
import asyncio
from pathlib import Path
from tqdm import tqdm

from autogen_sql.schema_agent import SchemaAgent
from autogen_sql.planner_agent import PlannerAgent
from autogen_sql.sql_agent import SQLAgent
from autogen_sql.verifier_agent import VerifierAgent

BASE_DATA_DIR = Path("data/mini_dev_data/minidev/MINIDEV")
JSON_PATH = BASE_DATA_DIR / "mini_dev_sqlite.json"
DB_ROOT = BASE_DATA_DIR / "dev_databases"

async def process_example(ex, agents):
    schema_agent, planner_agent, sql_agent, verifier_agent = agents
    
    q = ex["question"]
    evidence = ex.get("evidence", "") or "None"
    db_id = ex["db_id"]
    
    db_file = DB_ROOT / db_id / f"{db_id}.sqlite"
    
    summary = await schema_agent.summarize(q, str(db_file))
    
    plan = await planner_agent.plan(q, summary, evidence)
    
    raw_sql = await sql_agent.generate(q, summary, plan)
    
    final_sql = await verifier_agent.verify(raw_sql, str(db_file), q, summary)
    
    return {
        "db_id": db_id,
        "question": q,
        "predicted_SQL": final_sql
    }
    
async def main():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"Could not find {JSON_PATH}")
    
    with open(JSON_PATH, "r") as f:
        examples = json.load(f)
    
    schema_agent = SchemaAgent(model="mistral")
    planner_agent = PlannerAgent(model="mistral")
    sql_agent = SQLAgent(model="mistral")
    verifier_agent = VerifierAgent(model="mistral")
    agents = (schema_agent, planner_agent, sql_agent, verifier_agent)
    
    results = []
    for ex in tqdm(examples, desc="Processing examples", unit="ex"):
        out = await process_example(ex, agents)
        results.append(out)
        
    out_path = Path("predictions.json")
    with out_path.open("w") as f:
        json.dump(results, f, indent=2)
    print(f"\n Wrote {len(results)} predictions to {out_path}")
    
    jl = Path("predictions.jsonl")
    with jl.open("w") as f_jl:
        for rec in results:
            f_jl.write(json.dumps(rec) + "\n")
    print(f"Wrote jsonl to {jl}")
    
    di = Path("predictions_dict.json")
    pred_map = { str(i): rec["predicted_SQL"] for i, rec in enumerate(results) }
    with di.open("w") as f_di:
        json.dump(pred_map, f_di, indent=2)
    print(f"Wrote evaluator-ready dict to {di}")
    
if __name__ == "__main__":
    asyncio.run(main())