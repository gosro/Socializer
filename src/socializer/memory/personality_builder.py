from __future__ import annotations
from socializer.llm.base import LLMProvider
from socializer.memory.personality import write_personality

_SYSTEM = "Ты — аналитик стиля переписки. Отвечай только на русском."

_INSTRUCTION = """Проанализируй, КАК пишет этот человек, по его собственным сообщениям ниже.
Определи: тон, типичную длину сообщений, использование эмодзи (какие и как часто),
сленг, пунктуацию (ставит ли точки, скобки-смайлы). Не пересказывай содержание.

Верни готовый файл personality.md на русском в таком формате:
# Мой стиль общения
## Тон
...
## Как пишу
- ...
## Примеры моих реплик
- (3-5 характерных примеров, взятых/обобщённых из сообщений)
## Чего избегаю
- ...

Сообщения (только этого человека), каждое с новой строки:
<<<
{samples}
>>>"""


def build_personality_prompt(samples: list[str]) -> str:
    joined = "\n".join(samples)
    return _INSTRUCTION.format(samples=joined)


async def generate_personality(provider: LLMProvider, samples: list[str], data_dir: str) -> str:
    prompt = build_personality_prompt(samples)
    result = await provider.complete(_SYSTEM, [{"role": "user", "content": prompt}])
    write_personality(data_dir, result)
    return result
