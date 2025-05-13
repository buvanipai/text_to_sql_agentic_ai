import sqlite3
from pathlib import Path
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import AssistantAgent

class SchemaAgent():
    """
    Loads a SQLite schema and uses an LLM to filter it down to only the relevant tables/columns for the user question.
    """
    
    def __init__(self, model="mistral", temperature=0.0):
        self.model_client = OllamaChatCompletionClient(
            model=model, 
            temperature=temperature,
            device="cuda",
            gpu_layers=12
        )
        
        system_prompt = ("""
        You are a Schema Summarizer.
        Given a natural language question and a database schema, identify which tables and columns are needed to answer the question.
        Respond with a concise bullet list of tables and columns as shown below:
        - table_name
            - column_name_1
            - column_name_2
        - table_name_2
            - column_name_3
        Strictly only give this and nothing else please.
        """)
        
        self.agent = AssistantAgent(
            name="SchemaAgent",
            model_client=self.model_client,
            system_message=system_prompt,
        )
        
    def _load_schema(self, db_path: Path) -> dict[str, list[str]]:
        """
        Return {table_name: [col1, col2, ...]} from the SQLite file.
        """
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        schema = {}
        
        for tbl in tables:
            cur.execute(f"PRAGMA table_info({tbl});")
            cols = [c[1] for c in cur.fetchall()]
            schema[tbl] = cols
        
        conn.close()
        return schema
    
    def _schema_to_text(self, schema: dict[str, list[str]]) -> str:
        """
        Convert the schema dictionary to bullet format.
        """
        lines = []
        for tbl, cols in schema.items():
            cols_str = "' ".join(cols)
            lines.append(f"- {tbl}({cols_str})")
        return "\n".join(lines)
    
    async def summarize(self, question: str, db_path: str) -> str:
        """
        Returns the LLM's schema summary for this question+DB.
        """
        db_file = Path(db_path)
        raw_schema = self._load_schema(db_file)
        schema_text = self._schema_to_text(raw_schema)
        
        user_message = (
            f"Question:\n{question}\n\n"
            f"Schema:\n{schema_text}\n\n"
            "Which tables and columns above are relevant and needed to answer the question?"
        )
        
        resp = await self.agent.run(task=user_message)
        
        for msg in resp.messages:
            if getattr(msg, "source", None) == self.agent.name:
                return msg.content.strip()
        return resp.messages[-1].content.strip()