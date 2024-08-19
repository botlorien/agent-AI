from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage
from langchain_community.llms import Ollama
from typing import List, Tuple


# ollama = Ollama(
#     base_url=f'http://localhost:11434',
#     model="llama3:8b"
# )
# print(ollama.invoke("hi"))

class Assistant:
    def __init__(self, name_assistent, instructions, tools=None, model='llama3:8b', temperature: int = 0,
                 *args, **kwargs):
        self.name_assistent = name_assistent
        self._instructions = instructions
        self._tools = tools
        self._model = model
        self.temperature = temperature
        self.base_url = kwargs.get('base_url', False) or 'http://localhost:11434'
        print(self.base_url)
        self.llm = ChatOllama(
            model=self._model,
            temperature=self.temperature,
            base_url=self.base_url
            # other params...
        )
        self._messages: List[Tuple[str, str]] = []
        self.add_message(('system', self._instructions))

    @property
    def messages(self):
        return self._messages

    def add_message(self, message: Tuple[str, str]):
        self._messages.append(message)

    def chat(self, query):
        self.add_message(("user", query))
        ai_msg = self.llm.invoke(self.messages)
        print(ai_msg.content)
        self.add_message(("ai", ai_msg.content))
        return {"message": ai_msg.content}


if __name__ == '__main__':
    ass = Assistant(
        name_assistent='test',
        instructions=' this is test',
        base_url='http://10.0.20.70:11434'
    )

