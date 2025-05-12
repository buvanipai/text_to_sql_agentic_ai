import json, sqlite3
from pathlib import Path

BASE_DATA_DIR = Path("data/mini_dev_data/minidev/MINIDEV")

def main():
    json_path = BASE_DATA_DIR / "dev_databases.json"
    if not json_path.exists():
        print(f"JSON not found at {json_path}.")
        return
    
    print(f"Found JSON at {json_path}.")
    
    with open(json_path, "r") as f:
        examples = json.load(f)
    print(f"Loaded {len(examples)} examples.")
    
    db_root = BASE_DATA_DIR / "dev_databases"
    ex = examples[0]
    db_file = db_root / ex["db_id"] / f"{ex['db_id']}.splite"
    
    if not db_file.exists():
        print(f"Could not find {db_file}.")
        return
    
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    print(f"Tables in {ex["db_id"]} -> {tables}")
    conn.close()
    
if __name__ == "__main__":
    main()