"""CAJAL + LangChain for research agents"""
from langchain.llms.base import LLM
from cajal_p2pclaw import CAJALChat

class CAJALLangChain(LLM):
    """Use CAJAL as LangChain LLM for scientific tasks"""
    
    def _call(self, prompt, stop=None):
        chat = CAJALChat()
        return chat.send(prompt)
    
    @property
    def _llm_type(self):
        return "cajal"

# Usage
llm = CAJALLangChain()
result = llm.predict("Generate a paper abstract on P2P networks")
print(result)
