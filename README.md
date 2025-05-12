# BIRD-SQL Mini-Dev Multi-Agent System

A multi-agent pipeline for converting natural language questions into executable SQL queries on the BIRD-SQL Mini-Dev benchmark using AutoGen and a locally hosted Mistral 7B model via Ollama.

---

## Overview

This repository implements a structured, four-agent system:

1. **SchemaAgent**: Summarizes and filters the database schema.
2. **PlannerAgent**: Breaks down the question into a step-by-step plan.
3. **SQLAgent**: Generates a valid SQLite query from the plan.
4. **VerifierAgent**: Executes and refines the query on SQLite.

The goal is to achieve **≥ 60% Execution Accuracy (EX)** on the 500-example Mini-Dev subset of BIRD-SQL.

---

## Installation & Setup

1. Clone this repository and enter the folder:

   ```bash
   git clone https://github.com/your-username/bird-sql-autogen.git
   cd bird-sql-autogen
   ```

2. Create and activate a Python virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Install the Ollama CLI (macOS):

   ```bash
   brew install ollama
   ```

5. Start the Ollama daemon:

   ```bash
   ollama serve &
   ```

6. Pull the Mistral model:

   ```bash
   ollama pull mistral
   ```

---

## Data Download

1. Fetch and extract the BIRD Mini-Dev dataset:

   ```bash
   python download_data.py
   ```

2. Verify the data structure:

   ```bash
   python verify_data.py
   ```

---

## Testing

Run unit tests for each agent:

```bash
python test_schema.py    # SchemaAgent
python test_planner.py   # PlannerAgent
python test_sql.py       # SQLAgent
python test_verifier.py  # VerifierAgent
```

Each script should complete without errors.

---

## Running the Full Pipeline

Process all 500 examples and generate `predictions.json`:

```bash
python run_pipeline.py
```

Progress is displayed with a tqdm bar.

For faster runs on larger models, you can use a cloud GPU instance. See **CLOUD\_SETUP\_README.md** for instructions.

---