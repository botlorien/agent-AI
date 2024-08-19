import json
import logging
import os,os.path
from utils.decorators import time_out
from utils.generics import get_dummy
from openai import OpenAI
import openai
import copy
import uuid
import base64
import requests
import inspect

class RunningQueue(Exception):
    pass


class Assistant:

    def __init__(self, name_assistent, instructions, tools=None, model='gpt-3.5-turbo-1106', temperature: int = 0,
                 *args, **kwargs):
        self.client = OpenAI(**self._filter_params(OpenAI,kwargs))
        self.responses = None
        self.message = None
        self.run = None
        self.assistant = None
        self.thread = None
        self.available_functions = None
        self.name = name_assistent
        self.instructions = instructions
        self.tools = tools if tools is not None else [{"type": "code_interpreter"}]
        self.model = model
        self.temperature = temperature
        self.assistant_id = self.get_assistent_config()['assistant_id']
        self.thread_id = None
        self.update_assistant()

    def _filter_attrs(self,__obj:object,__kwargs:dict):
        print(__kwargs)
        __new_kwargs = {}
        for key in __kwargs:
            if hasattr(__obj,key):
                __new_kwargs[key]=__kwargs[key]
        print(__new_kwargs)
        return __new_kwargs

    def _filter_params(self, cls, kwargs):
        # Get the signature of the class constructor
        sig = inspect.signature(cls.__init__)
        # Get the parameters that the constructor accepts
        valid_params = sig.parameters.keys()
        # Filter the kwargs to only include valid parameters
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}
        return filtered_kwargs
    def create_assistent(self, *args, **kwargs):
        self.assistant = self.client.beta.assistants.create(
            name=self.name,
            instructions=self.instructions,
            tools=self.tools,
            model=self.model,
            temperature=self.temperature,
            **kwargs
        )
        return self

    def update_assistant(self, **kwargs):
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant_id,
            name=self.name,
            instructions=self.instructions,
            tools=self.tools,
            model=self.model,
            temperature=self.temperature
        )
        return self

    def get_list_created_assistents(self):
        my_assistants = self.client.beta.assistants.list(
            order="desc",
        )
        return my_assistants.data

    def get_assistent_config(self):
        try:
            if not os.path.exists('../../config/config_assistent.json'):
                self.assistant_id = self.create_assistent().assistant.id
                assistent_config_file = {
                    'assistant_id': self.assistant_id
                }
                os.makedirs('../../config', exist_ok=True)
                with open('../../config/config_assistent.json', 'w', encoding='utf-8') as f:
                    f.write(json.dumps(assistent_config_file, ensure_ascii=False, indent=4))
            else:
                with open('../../config/config_assistent.json', 'r', encoding='utf-8') as f:
                    assistent_config_file = json.loads(f.read())
            print(assistent_config_file)
            return assistent_config_file
        except Exception as e:
            logging.exception(e)

    def load_available_functions(self, available_functions):
        self.available_functions = available_functions
        return self

    def create_new_conversation(self):
        self.thread = self.client.beta.threads.create()
        self.thread_id = self.thread.id
        return self

    def use_existent_thread_id(self, thread_id):
        if thread_id is not None and isinstance(thread_id,str) and len(thread_id)>0:
            self.thread_id = thread_id
        else:
            raise ValueError('Invalid thread_id!')
        return self

    def run_assistent(self):
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions=self.instructions,
            tools=self.tools,
        )
        return self

    def verify_expiration(self, expires_at):
        print(expires_at)  # 1704832738
        # Timestamps
        now = get_dummy() / 1000
        print(now)
        if now < expires_at:
            return True
        return False

    @time_out(120, show_exception=True)
    def verify_run(self):
        run = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id,
            run_id=self.run.id
        )
        print(run)
        status = [val for val in (run.completed_at, run.cancelled_at, run.failed_at) if val is not None]
        if run.failed_at is not None:
            return {"error":f"Erro {run.last_error.message}"}

        elif run.cancelled_at is not None:
            return {"error": f"Erro {run.last_error.message}"}
        elif run.required_action:
            if isinstance(self.verify_response_tools(run.required_action), Assistent):
                raise RunningQueue
            return False
        elif run.completed_at is not None:
            return {"message": str(run)}
        else:
            raise RunningQueue

    def add_file_search_to_main_assistent(self, name_to_vector_store, list_of_files_path):
        self.tools.append({"type": "file_search"})
        self.update_assistant(tools=self.tools)
        # Create a vector store caled "Financial Statements"
        self.vector_store = self.client.beta.vector_stores.create(name=name_to_vector_store)

        # Ready the files for upload to OpenAI
        file_streams = [open(path, "rb") for path in list_of_files_path]

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store.id, files=file_streams
        )

        # You can print the status and the file counts of the batch to see the result of this operation.
        print(file_batch.status)
        print(file_batch.file_counts)
        self.update_assistant(tool_resources={"file_search": {"vector_store_ids": [self.vector_store.id]}})
        return self

    def add_file_search_to_thread_assistent(self, name_to_vector_store, list_of_files_path):
        self.tools.append({"type": "file_search"})
        self.update_assistant(tools=self.tools)
        # Create a vector store caled "Financial Statements"
        self.vector_store_thread = self.client.beta.vector_stores.create(
            name=name_to_vector_store,
            expires_after={
                "anchor": "last_active_at",
                "days": 3
            }
        )
        # Ready the files for upload to OpenAI
        file_streams = [open(path, "rb") for path in list_of_files_path]

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store_thread.id, files=file_streams
        )
        print(file_batch.status)
        print(file_batch.file_counts)

        self.update_thread(
            tool_resources={"file_search": {"vector_store_ids": [self.vector_store_thread.id]}}
        )

        # The thread now has a vector store with that file in its tool resources.
        print(self.thread.tool_resources.file_search)
        return self

    def update_thread(self, **kwargs):
        # Update a thread
        self.thread = self.client.beta.threads.update(
            thread_id=self.thread_id,
            **kwargs
        )
        return self

    def add_user_message(self, msg):
        self.message = self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=msg
        )
        return self

    def show_responses(self):
        self.responses = self.client.beta.threads.messages.list(
            thread_id=self.thread_id
        )
        print(self.responses)
        if self.responses.data[0].role !='user':
            answer = self.responses.data[0].content[0].text.value
        else:
            answer = f'O {self.model} não está respondendo adequadamente!'
        print(answer)
        return answer

    def test_assistent(self):
        print('Sou seu assistente pessoal, em que posso ajudar?')
        while True:
            ask = input()
            self.add_user_message(ask)
            self.run_assistent()
            self.verify_run()
            self.show_responses()

    def submit_tools_response(self, tool_outputs):
        self.run = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=self.run.id,
            tool_outputs=tool_outputs
        )
        return self

    def verify_response_tools(self, response):
        tool_outputs = []
        try:
            for tool_call in response.submit_tool_outputs.tool_calls:
                function_name = tool_call.function.name
                function_to_call = self.available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                print(function_args)
                function_response = function_to_call(
                    **function_args
                )
                function_response = function_response if function_response is not None else 'Erro na busca'
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": str(function_response),
                })
                # print(tool_outputs)
            self.submit_tools_response(tool_outputs)
        except Exception as e:
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": f'ERRO: {str(e)}',
            })
            self.submit_tools_response(tool_outputs)
        return self

    def chat(self,query:str,thread_id:int=None,*args,**kwargs):
        if not query:
            return {'error': 'No query provided'}, 400
        if thread_id is None:
            thread_id = self.create_new_conversation().thread_id
        else:
            thread_id = self.use_existent_thread_id(thread_id).thread_id
        self.add_user_message(query)
        self.run_assistent()
        resp = self.verify_run()
        if 'error' in resp:
            return resp
        return {'message': self.show_responses(), 'thread_id': thread_id}


class Vision:

    def __init__(self, model: str = "gpt-4o"):
        self.client = OpenAI()
        self.model = model

    # Function to encode the image
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            base64_content = base64.b64encode(image_file.read()).decode('utf-8')
        os.remove(image_path)
        return base64_content

    def get_image(self, path_image):
        resp = requests.get(path_image)
        os.makedirs('files', exist_ok=True)
        name_file = 'img_' + str(uuid.uuid4()) + '.jpeg'
        path_file = os.path.join('files', name_file)
        with open(path_file, 'wb') as f:
            f.write(resp.content)
        return path_file

    def identify_type_image(self, path_image):
        base64_url = f"data:image/jpeg;base64,{self.encode_image(self.get_image(path_image))}" \
            if 'https://' in path_image else f"data:image/jpeg;base64,{self.encode_image(path_image)}"
        return base64_url

    def submit_image(self, path_image, prompt="Whats in this image?", max_tokens=300, **kwargs):

        list_objects = []
        if isinstance(path_image, list):
            for path_ in path_image:
                list_objects.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": self.identify_type_image(path_),
                        }
                    }
                )
        else:
            list_objects = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": self.identify_type_image(path_image),
                    }
                }
            ]
        self.response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        *list_objects
                    ],
                }
            ],
            max_tokens=max_tokens,
            **kwargs
        )
        message = self.response.choices[0].message.content
        print(message)
        return message


if __name__ == '__main__':
    instructions="""
    Você é um Assitente pessoal responsavel por fornecer insights do mercado financeiro com base na resposta de consulta de  Apis
    Além da habilidade de encaminhar emails
    """
    ass = Assistent(
        'portfolio',
        instructions=instructions,
        api_key=os.getenv('OPENAI_API_KEY_PORTFOLIO')
    )
    query = input('Digite algo:')
    resp = ass.chat(query)
    print(resp)

