"""CAJAL Research Assistant with Chainlit"""
import chainlit as cl
from cajal_p2pclaw import CAJALChat

@cl.on_chat_start
async def start():
    await cl.Message(content="🧠 CAJAL Research Assistant ready! Ask me to generate papers, reviews, or analyze data.").send()

@cl.on_message
async def main(message: cl.Message):
    chat = CAJALChat()
    response = chat.send(message.content)
    await cl.Message(content=response).send()
