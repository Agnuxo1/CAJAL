# CAJAL Jupyter Kernel
from cajal_p2pclaw import CAJALChat

class CAJALKernel:
    def __init__(self):
        self.chat = CAJALChat()
    
    def execute(self, code):
        if code.startswith("%%cajal"):
            prompt = code.replace("%%cajal", "").strip()
            return self.chat.send(prompt)
        return None
