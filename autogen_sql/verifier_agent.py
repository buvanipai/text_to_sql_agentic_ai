import sqlite3
import re
from pathlib import Path
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient

class VerifierAgent:
    """
    Runs a SQL query on the given SQLite DB. On error or empty result,
    uses an LLM to refine the SQL up to a max number of attempts.
    """
    
    def __init__(self, model: str = "mistral", temperature: float = 0.0, max_attempts: int =2):
        self.model_client = OllamaChatCompletionClient(
            model=model, 
            temperature=temperature,
            device="cuda",
            gpu_layers=12
        )
        system_prompt = (
            """
            You are a Verifier Agent. You are given a SQL query and an error message or empty result. 
            Please debug or refine the SQL so that it runs correctly on SQLite and answers the original question.
            Strictly output only the corrected SQL (no explanation).
            """
        )
        self.agent = AssistantAgent(
            name="VerifierAgent",
            model_client=self.model_client,
            system_message=system_prompt,
        )
        self.max_attempts = max_attempts
        
    async def verify(self, sql: str, db_path: str, question: str, schema_summary: str) -> str:
        """
        Returns a verified SQL query. If the query errors or returns zero rows,
        runs up to `max_attempts` of LLM-driven corrections.
        """
        
        db_file = Path(db_path)
        if not db_file.exists():
            print(f"DB file not found at {db_file}, returning original SQL")
            return sql.strip()
        
        current_sql = sql.strip()
        for attempt in range(1, self.max_attempts + 1):
            m = re.match(r"^```(?:sql)?\s*([\s\S]*?)\s*```$", current_sql)
            if m:
                current_sql = m.group(1).strip()
                
            try:
                conn = sqlite3.connect(db_file)
                cur = conn.cursor()
                cur.execute(current_sql)
                rows = cur.fetchall()
                conn.close()
            except Exception as e:
                error = str(e)
                if "division by zero" in error.lower():
                    return current_sql
                prompt = (
                    f"The following SQL failed with error:\n{error}\n\n"
                    f"SQL:\n{current_sql}\n\n"
                    "Please debug or refine the SQL so that it runs correctly on SQLite and answers the original question."
                )
                resp = await self.agent.run(task=prompt)
                corrected = None
                for msg in resp.messages:
                    if msg.source == self.agent.name:
                        corrected = msg.content.strip()
                        break
                else:
                    current_sql = re.sub(r"^```(?:sql)?\s*|```$", "", corrected).strip()
                continue
            
            if rows:
                return current_sql
            
            if not rows:
                prompt = (
                    """
                    The SQL ran successfully but returned no rows.
                    Given the question and schema context, refine the SQL so it return the expected results.\n\n
                    SQL:\n{current_sql}\n\n
                    """
                )
                resp = await self.agent.run(task=prompt)
                candidate = None
                for msg in resp.messages:
                    if msg.source == self.agent.name:
                        candidate = msg.content.strip()
                        break
                if candidate and candidate.upper().lstrip().startswith("SELECT"):
                    current_sql = re.sub(r"^```(?:sql)?\s*|```$", "", candidate).strip()
                    continue
                break
        return current_sql