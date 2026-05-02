"""
CAJAL CrewAI Integration
https://github.com/crewAIInc/crewAI

Installation:
    pip install cajal-p2pclaw crewai

Usage:
    from cajal_p2pclaw.crewai import CAJALAgent, PaperCrew
    crew = PaperCrew(topic="Quantum error correction")
    result = crew.run()
"""

from crewai import Agent, Task, Crew, Process
from typing import Optional, List
import requests

class CAJALAgent:
    """CAJAL-powered agent for CrewAI."""
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        model: str = "cajal",
        ollama_host: str = "http://localhost:11434",
        temperature: float = 0.3
    ):
        self.model = model
        self.ollama_host = ollama_host
        self.temperature = temperature
        
        self.agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=self._create_llm(),
            verbose=True
        )
    
    def _create_llm(self):
        """Create Ollama LLM configuration for CrewAI."""
        from langchain_ollama import OllamaLLM
        return OllamaLLM(
            model=self.model,
            base_url=self.ollama_host,
            temperature=self.temperature,
            num_ctx=32768
        )
    
    def create_task(self, description: str, expected_output: str, context: Optional[List[Task]] = None) -> Task:
        """Create a task for this agent."""
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
            context=context or []
        )


class PaperCrew:
    """A CrewAI crew configured for scientific paper generation."""
    
    def __init__(self, topic: str, model: str = "cajal"):
        self.topic = topic
        self.model = model
        self.crew = self._build_crew()
    
    def _build_crew(self) -> Crew:
        """Build a multi-agent crew for paper generation."""
        
        # 1. Research Agent - Literature review and reference finding
        researcher = CAJALAgent(
            role="Research Analyst",
            goal=f"Find and synthesize relevant academic literature on {self.topic}",
            backstory="You are an expert research analyst with deep knowledge of academic literature. You excel at finding relevant papers and synthesizing their contributions.",
            model=self.model
        )
        
        # 2. Methodology Agent - Methods section
        methodologist = CAJALAgent(
            role="Methodology Expert",
            goal=f"Design rigorous, reproducible methodology for research on {self.topic}",
            backstory="You are a methodology expert who designs bulletproof experimental procedures. Your methods sections are cited as exemplars in research methodology courses.",
            model=self.model
        )
        
        # 3. Writer Agent - Paper drafting
        writer = CAJALAgent(
            role="Scientific Writer",
            goal=f"Write a publication-ready paper on {self.topic}",
            backstory="You are an award-winning scientific writer who can turn complex research into clear, compelling papers. Your work has been published in top-tier venues.",
            model=self.model
        )
        
        # 4. Reviewer Agent - Quality assurance
        reviewer = CAJALAgent(
            role="Peer Reviewer",
            goal=f"Critically evaluate the paper on {self.topic} and suggest improvements",
            backstory="You are a seasoned peer reviewer for top-tier journals. You catch every flaw, demand rigor, and push for excellence.",
            model=self.model
        )
        
        # Define tasks with dependencies
        research_task = researcher.create_task(
            description=f"Research {self.topic}. Find 8-12 relevant papers. Summarize key contributions, methodologies, and gaps. Output a structured literature review.",
            expected_output="A structured literature review with 8-12 cited references, summarizing the state of the art and identifying research gaps."
        )
        
        methods_task = methodologist.create_task(
            description=f"Design methodology for {self.topic}. Specify: experimental setup, datasets, parameters, evaluation metrics, and reproducibility checklist.",
            expected_output="A detailed methodology section that another researcher could use to reproduce the work.",
            context=[research_task]
        )
        
        writing_task = writer.create_task(
            description=f"Write a complete scientific paper on {self.topic}. Use the literature review and methodology. Include: Abstract, Introduction, Related Work, Methodology, Results, Discussion, Conclusion, References.",
            expected_output="A complete, publication-ready scientific paper in markdown format with proper citations.",
            context=[research_task, methods_task]
        )
        
        review_task = reviewer.create_task(
            description=f"Review the paper on {self.topic}. Evaluate: structure, clarity, methodology soundness, citation quality, argument strength, and limitations. Provide specific improvement suggestions.",
            expected_output="A detailed peer review with scores and actionable improvement suggestions.",
            context=[writing_task]
        )
        
        return Crew(
            agents=[researcher.agent, methodologist.agent, writer.agent, reviewer.agent],
            tasks=[research_task, methods_task, writing_task, review_task],
            process=Process.sequential,
            verbose=True
        )
    
    def run(self) -> str:
        """Run the paper generation crew."""
        result = self.crew.kickoff()
        return result


# Standalone tool for CrewAI tools integration
cajal_tool = {
    "name": "cajal_paper_generator",
    "description": "Generate a scientific paper on any topic using local LLM. Returns a complete paper with abstract, introduction, methods, results, discussion, conclusion, and references.",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Research topic for the paper"
            },
            "format": {
                "type": "string",
                "enum": ["markdown", "latex", "pdf"],
                "default": "markdown",
                "description": "Output format"
            },
            "min_references": {
                "type": "integer",
                "default": 8,
                "description": "Minimum number of references"
            }
        },
        "required": ["topic"]
    }
}


if __name__ == "__main__":
    print("🧪 CAJAL CrewAI Integration Demo")
    print("=" * 50)
    
    # Create and run a paper crew
    crew = PaperCrew(topic="Federated learning for medical imaging privacy")
    result = crew.run()
    
    print("\n📄 Generated Paper:")
    print(result)
