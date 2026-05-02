"""
CAJAL AutoGen Integration
https://github.com/microsoft/autogen

Installation:
    pip install cajal-p2pclaw pyautogen

Usage:
    from cajal_p2pclaw.autogen import CAJALClient, create_paper_agents
    result = create_paper_agents("Quantum machine learning")
"""

import autogen
from typing import Dict, List, Optional

class CAJALClient:
    """CAJAL configuration for AutoGen."""
    
    def __init__(
        self,
        model: str = "cajal",
        ollama_host: str = "http://localhost:11434",
        temperature: float = 0.3,
        max_tokens: int = 8192
    ):
        self.config = {
            "model": model,
            "base_url": ollama_host,
            "api_type": "ollama",
            "temperature": temperature,
            "max_tokens": max_tokens,
            "num_ctx": 32768
        }
    
    def get_config_list(self) -> List[Dict]:
        """Return AutoGen-compatible config list."""
        return [self.config]


def create_paper_agents(
    topic: str,
    model: str = "cajal",
    ollama_host: str = "http://localhost:11434"
) -> Dict:
    """Create a multi-agent setup for paper generation in AutoGen."""
    
    client = CAJALClient(model=model, ollama_host=ollama_host)
    config_list = client.get_config_list()
    
    # LLM config
    llm_config = {
        "config_list": config_list,
        "timeout": 300,
        "cache_seed": 42
    }
    
    # System prompt template
    CAJAL_SYSTEM = """You are CAJAL (Cognitive Academic Journal Authoring Layer), a specialized scientific paper authoring assistant.

Generate publication-ready scientific papers with:
- Formal academic tone
- Proper structure (Abstract → Introduction → Methods → Results → Discussion → Conclusion → References)
- Real citations where possible
- Reproducible methodology
- Quantitative, evidence-based claims

Always use markdown formatting with clear section headers."""
    
    # Create agents
    researcher = autogen.AssistantAgent(
        name="researcher",
        system_message=f"{CAJAL_SYSTEM}\n\nYou are a Research Analyst. Your job is to find and synthesize relevant academic literature. Focus on identifying key papers, methodologies, and research gaps related to the given topic.",
        llm_config=llm_config
    )
    
    methodologist = autogen.AssistantAgent(
        name="methodologist",
        system_message=f"{CAJAL_SYSTEM}\n\nYou are a Methodology Expert. Your job is to design rigorous, reproducible experimental procedures. Specify datasets, parameters, evaluation metrics, and ensure another researcher could reproduce the work.",
        llm_config=llm_config
    )
    
    writer = autogen.AssistantAgent(
        name="writer",
        system_message=f"{CAJAL_SYSTEM}\n\nYou are a Scientific Writer. Your job is to write clear, compelling scientific papers. You excel at turning complex research into accessible yet rigorous prose. Always include proper citations.",
        llm_config=llm_config
    )
    
    reviewer = autogen.AssistantAgent(
        name="reviewer",
        system_message=f"{CAJAL_SYSTEM}\n\nYou are a Peer Reviewer. Your job is to critically evaluate scientific papers. Check for: structural integrity, methodological soundness, citation quality, argument strength, and identify limitations. Be thorough and constructive.",
        llm_config=llm_config
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={
            "work_dir": "paper_output",
            "use_docker": False
        }
    )
    
    # Group chat for collaborative paper writing
    groupchat = autogen.GroupChat(
        agents=[user_proxy, researcher, methodologist, writer, reviewer],
        messages=[],
        max_round=20
    )
    
    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config
    )
    
    return {
        "user_proxy": user_proxy,
        "researcher": researcher,
        "methodologist": methodologist,
        "writer": writer,
        "reviewer": reviewer,
        "manager": manager,
        "groupchat": groupchat
    }


def generate_paper(topic: str, model: str = "cajal") -> str:
    """One-shot paper generation using AutoGen multi-agent setup."""
    
    agents = create_paper_agents(topic, model)
    
    # Initiate the conversation
    agents["user_proxy"].initiate_chat(
        agents["manager"],
        message=f"""Generate a complete scientific paper on: {topic}

Process:
1. Researcher: Find and synthesize relevant literature (8-12 references)
2. Methodologist: Design rigorous methodology
3. Writer: Draft the full paper using research and methods
4. Reviewer: Critically evaluate and suggest improvements
5. Writer: Finalize based on review feedback

Output the final paper in markdown format with all sections."""
    )
    
    # Extract the final paper from the chat history
    final_messages = agents["groupchat"].messages
    for msg in reversed(final_messages):
        if "writer" in msg.get("name", "") and len(msg.get("content", "")) > 500:
            return msg["content"]
    
    # Fallback: return last substantial message
    for msg in reversed(final_messages):
        if len(msg.get("content", "")) > 500:
            return msg["content"]
    
    return "Paper generation in progress. Check the conversation history."


if __name__ == "__main__":
    print("🧪 CAJAL AutoGen Integration Demo")
    print("=" * 50)
    
    topic = "Neural architecture search for resource-constrained devices"
    print(f"\n📄 Generating paper on: {topic}")
    
    paper = generate_paper(topic)
    print(f"\nGenerated {len(paper)} characters")
    print("\nPreview:")
    print(paper[:1000])
