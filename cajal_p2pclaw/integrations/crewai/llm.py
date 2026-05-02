from crewai.llm import LLM as CrewLLM
import requests


class CAJALCrewAI(CrewLLM):
    """CrewAI integration for CAJAL-4B-P2PCLAW.

    Usage:
        from cajal_p2pclaw.integrations.crewai import CAJALCrewAI
        from crewai import Agent, Task, Crew

        llm = CAJALCrewAI(server_url="http://localhost:8000")

        researcher = Agent(
            role="P2P Researcher",
            goal="Analyze decentralized consensus mechanisms",
            backstory="Expert in distributed systems and cryptography",
            llm=llm,
        )

        task = Task(
            description="Explain Byzantine Fault Tolerance in 3 paragraphs",
            agent=researcher,
        )

        crew = Crew(agents=[researcher], tasks=[task])
        result = crew.kickoff()
    """

    def __init__(self, server_url: str = "http://localhost:8000", **kwargs):
        super().__init__(model="cajal-4b", **kwargs)
        self.server_url = server_url

    def call(self, prompt: str, **kwargs) -> str:
        res = requests.post(
            f"{self.server_url}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "model": "Agnuxo/CAJAL-4B-P2PCLAW",
                "max_new_tokens": 512,
                "temperature": 0.7,
            },
        )
        res.raise_for_status()
        return res.json()["response"]
