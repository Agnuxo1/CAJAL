# CAJAL Framework Integrations

Native integrations for popular AI/ML frameworks.

## LangChain

```python
from cajal_p2pclaw.integrations.langchain import CAJALLangChain

llm = CAJALLangChain(server_url="http://localhost:8000")
result = llm.predict("Explain P2P consensus.")
```

## LlamaIndex

```python
from cajal_p2pclaw.integrations.llamaindex import CAJALLlamaIndex

llm = CAJALLlamaIndex(server_url="http://localhost:8000")
response = llm.complete("Summarize this paper.")
```

## CrewAI

```python
from cajal_p2pclaw.integrations.crewai import CAJALCrewAI
from crewai import Agent, Task, Crew

llm = CAJALCrewAI(server_url="http://localhost:8000")
agent = Agent(role="Researcher", goal="Analyze P2P", llm=llm)
```

## AutoGen

```python
from cajal_p2pclaw.integrations.autogen import CAJALAutoGen

client = CAJALAutoGen(server_url="http://localhost:8000")
response = client.create(messages=[{"role": "user", "content": "Hello"}])
```

## Requirements

- `pip install cajal-p2pclaw`
- Running `cajal-server` on your preferred port
- Framework-specific packages: `langchain`, `llama-index`, `crewai`, `pyautogen`
