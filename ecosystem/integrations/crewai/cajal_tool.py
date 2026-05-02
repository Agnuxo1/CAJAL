"""
CrewAI integration for CAJAL-4B.

Install:
    pip install crewai cajal-cli

Usage:
    from cajal_crewai import CajalTool
    tool = CajalTool()
    result = tool.run("Research P2PCLAW governance models")
"""

from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

import requests


class CajalInput(BaseModel):
    """Input schema for CAJAL tool."""

    query: str = Field(
        ...,
        description="The research question or task for CAJAL to process. "
        "Can be about P2P systems, cryptography, governance, "
        "consensus mechanisms, or any scientific topic.",
    )


class CajalTool(BaseTool):
    """CrewAI Tool for CAJAL-4B scientific intelligence.

    Use CAJAL as a specialized research agent within your CrewAI crew.
    CAJAL excels at analyzing distributed systems, cryptographic protocols,
    and governance models.

    Example:
        .. code-block:: python

            from crewai import Agent, Task, Crew
            from cajal_crewai import CajalTool

            cajal_tool = CajalTool()

            researcher = Agent(
                role="P2P Systems Researcher",
                goal="Analyze decentralized governance models",
                backstory="Expert in distributed systems and game theory",
                tools=[cajal_tool],
                verbose=True,
            )

            task = Task(
                description="Research Byzantine fault tolerance in P2P networks",
                agent=researcher,
                expected_output="A comprehensive analysis of BFT mechanisms",
            )

            crew = Crew(agents=[researcher], tasks=[task])
            result = crew.kickoff()
    """

    name: str = "cajal_scientific_research"
    description: str = (
        "CAJAL-4B: A distinguished scientist specialized in peer-to-peer "
        "network architectures, crypto-legal frameworks, game-theoretic "
        "consensus mechanisms, and distributed systems. Use for deep "
        "research, protocol analysis, and scientific paper generation."
    )
    args_schema: Type[BaseModel] = CajalInput

    model: str = "cajal-4b"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    system_prompt: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.system_prompt is None:
            self.system_prompt = (
                "You are CAJAL, a distinguished scientist at the P2PCLAW "
                "laboratory in Zurich. Provide rigorous, evidence-based "
                "analysis with citations to protocols and papers when relevant."
            )

    def _run(self, query: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query},
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": 0.9,
                "num_ctx": 4096,
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "No response from CAJAL")
        except requests.exceptions.ConnectionError:
            return (
                "[ERROR] Cannot connect to Ollama. "
                "Ensure Ollama is running with: ollama serve"
            )
        except Exception as e:
            return f"[ERROR] {str(e)}"


class CajalCodeReviewTool(CajalTool):
    """Specialized CAJAL tool for code review and security analysis.

    Use this tool when you need CAJAL to review code for:
    - Security vulnerabilities
    - P2P architecture best practices
    - Cryptographic implementation correctness
    - Smart contract auditing
    """

    name: str = "cajal_code_reviewer"
    description: str = (
        "CAJAL-4B Code Reviewer: Expert in analyzing code for P2P "
        "architecture patterns, security vulnerabilities, and "
        "decentralization potential. Specializes in smart contract "
        "auditing and consensus algorithm review."
    )

    system_prompt: Optional[str] = (
        "You are CAJAL, a security researcher at P2PCLAW. Review code "
        "for: 1) P2P architecture best practices, 2) Security "
        "vulnerabilities (reentrancy, overflow, access control), "
        "3) Decentralization potential, 4) Cryptographic correctness. "
        "Always begin with a 'Thinking Process' showing your analysis steps."
    )


class CajalPaperWriterTool(CajalTool):
    """Specialized CAJAL tool for scientific paper writing.

    Use this tool when you need CAJAL to:
    - Write paper abstracts
    - Generate literature reviews
    - Structure research papers
    - Format academic citations
    """

    name: str = "cajal_paper_writer"
    description: str = (
        "CAJAL-4B Scientific Paper Writer: Expert in writing "
        "high-quality academic papers on distributed systems, "
        "cryptography, and P2P governance. Generates structured "
        "papers with proper citations and academic tone."
    )

    system_prompt: Optional[str] = (
        "You are CAJAL, a prolific scientist at P2PCLAW. Write "
        "academic papers with: 1) Clear abstracts, 2) Structured "
        "sections (Intro, Related Work, Methodology, Results, "
        "Conclusion), 3) Proper citations to real protocols and "
        "papers, 4) Formal academic tone, 5) Precise technical "
        "terminology. Always begin with a 'Thinking Process'."
    )
