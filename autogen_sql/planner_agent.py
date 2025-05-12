from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient

class PlannerAgent:
    """
    Given a natural language question, a schema summary, and optional evidence,
    produce a step-by-step reasoning plan (chain-of-thought) for constructing the SQL.
    """
    
    def __init__(self, model: str = "mistral", temperature: float = 0.0):
        self.model_client = OllamaChatCompletionClient(model=model, temperature=temperature)
        
        system_prompt = (
            """
            You are a Planning Agent.
            Given a natural language question, a schema summary, and optional evidence,
            break down how to answer the question in clear, ordered steps.
            Be specific about which tables/columns to use, how to join or filter,
            and any aggregations or subqueries needed.
            Strictly only output the plan in a numbered list format (no explanation).
            """
        )
        
        self.agent = AssistantAgent(
            name="PlannerAgent",
            model_client=self.model_client,
            system_message=system_prompt,
        )
        
    async def plan(self, question: str, schema_summary: str, evidence: str = "") -> str:
        """
        Returns a multi-step plan for writing the SQL.
        """
        
        prompt = (
            f"Question:\n{question}\n\n"
            f"Schema Summary:\n{schema_summary}\n\n"
            f"Evidence (if any):\n{evidence or None}\n\n"
            "Please provide a numbered, step-by-step plan."
        )
        
        resp = await self.agent.run(task=prompt)
        
        for msg in resp.messages:
            if msg.source == self.agent.name:
                return msg.content.strip()
        return resp.messages[-1].content.strip()