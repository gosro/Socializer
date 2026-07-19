from __future__ import annotations
from socializer.contacts import Contact
from socializer.llm.base import LLMProvider
from socializer.brain.context_builder import build_system_prompt, build_user_turns
from socializer.memory.personality import read_personality
from socializer.memory.conversation_memory import read_memory


async def generate_reply(provider: LLMProvider, data_dir: str, contact: Contact,
                         recent: list[tuple[str, str]]) -> str:
    personality = read_personality(data_dir)
    memory = read_memory(data_dir, contact)
    system = build_system_prompt(personality, contact, memory)
    turns = build_user_turns(recent)
    result = await provider.complete(system, turns)
    return result.strip()
