```swarmauri/standard/README.md

# Standard Library

The Standard Library extends the Core Library with concrete implementations of models, agents, tools, parsers, and more. It aims to provide ready-to-use components that can be easily integrated into machine learning projects.

## Features

- **Predefined Models and Agents**: Implements standard models and agents ready for use.
- **Toolkit**: A collection of tools for various tasks (e.g., weather information, math operations).
- **Parsers Implementations**: Various parsers for text data, including HTML and CSV parsers.
- **Conversations and Chunkers**: Manage conversation histories and chunk text data.
- **Vectorizers**: Transform text data into vector representations.
- **Document Stores and Vector Stores**: Concrete implementations for storing and retrieving data.

## Getting Started

To make the best use of the Standard Library, first ensure that the Core Library is set up in your project as the Standard Library builds upon it.

```python
# Example usage of a concrete model from the Standard Library
from swarmauri.standard.models.concrete import OpenAIModel

# Initialize the model with necessary configuration
model = OpenAIModel(api_key="your_api_key_here")
```

## Documentation

For more detailed guides and API documentation, check the [Docs](/docs) directory within the library. You'll find examples, configuration options, and best practices for utilizing the provided components.

## Contributing

Your contributions can help the Standard Library grow! Whether it's adding new tools, improving models, or writing documentation, we appreciate your help. Please send a pull request with your contributions.

## License

Please see the `LICENSE` file in the repository for details.

```

```swarmauri/standard/__init__.py



```

```swarmauri/standard/llms/__init__.py



```

```swarmauri/standard/llms/base/__init__.py



```

```swarmauri/standard/llms/base/LLMBase.py

from abc import ABC, abstractmethod
from typing import Any, Union, Optional, List, Literal
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.llms.IPredict import IPredict

class LLMBase(IPredict, ComponentBase):
    allowed_models: List[str] = []
    resource: Optional[str] =  Field(default=ResourceTypes.LLM.value, frozen=True)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['LLMBase'] = 'LLMBase'

    @model_validator(mode='after')
    @classmethod
    def _validate_name_in_allowed_models(cls, values):
        name = values.name
        allowed_models = values.allowed_models
        if name and name not in allowed_models:
            raise ValueError(f"Model name {name} is not allowed. Choose from {allowed_models}")
        return values
        
    def predict(self, *args, **kwargs):
        raise NotImplementedError('Predict not implemented in subclass yet.')
        

```

```swarmauri/standard/llms/concrete/__init__.py



```

```swarmauri/standard/llms/concrete/OpenAIModel.py

import json
from typing import List, Dict, Literal
from openai import OpenAI
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class OpenAIModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gpt-4o', 
    'gpt-4o-2024-05-13',
    'gpt-4-turbo', 
    'gpt-4-turbo-2024-04-09',
    'gpt-4-turbo-preview',
    'gpt-4-0125-preview',
    'gpt-4-1106-preview',
    'gpt-4',
    'gpt-4-0613',
    'gpt-4-32k',
    'gpt-4-32k-0613',
    'gpt-3.5-turbo-0125',
    'gpt-3.5-turbo-1106',
    'gpt-3.5-turbo-0613',
    'gpt-3.5-turbo-16k-0613',
    'gpt-3.5-turbo-16k',
    'gpt-3.5-turbo']
    name: str = "gpt-3.5-turbo-16k"
    type: Literal['OpenAIModel'] = 'OpenAIModel'
    
    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256, 
        enable_json=False, 
        stop: List[str] = None):
        """
        Generate predictions using the OpenAI model.

        Parameters:
        - messages: Input data/messages for the model.
        - temperature (float): Sampling temperature.
        - max_tokens (int): Maximum number of tokens to generate.
        - enable_json (bool): Format response as JSON.
        
        Returns:
        - The generated message content.
        """
        formatted_messages = self._format_messages(conversation.history)
        client = OpenAI(api_key=self.api_key)
        
        if enable_json:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        else:
            response = client.chat.completions.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop
            )
        
        result = json.loads(response.model_dump_json())
        message_content = result['choices'][0]['message']['content']
        conversation.add_message(AgentMessage(content=message_content))
        
        return conversation

```

```swarmauri/standard/llms/concrete/OpenAIImageGenerator.py

import json
from typing import List, Literal
from openai import OpenAI
from swarmauri.core.llms.base.LLMBase import LLMBase

class OpenAIImageGenerator(LLMBase):
    api_key: str
    allowed_models: List[str] = ['dall-e']
    name: str = "dall-e"
    type: Literal['OpenAIImageGenerator'] = 'OpenAIImageGenerator'

    def predict(self, 
        prompt: str, 
        size: str = "1024x1024", 
        quality: str = "standard", 
        n: int = 1) -> str:
        """
        Generates an image based on the given prompt and other parameters.

        Parameters:
        - prompt (str): A description of the image you want to generate.
        - **kwargs: Additional parameters that the image generation endpoint might use.

        Returns:
        - str: A URL or identifier for the generated image.
        """
        try:
            client =  OpenAI(api_key=self.api_key)
            response = client.images.generate(
                model=self.name,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            result = response.json()
            return result
        
        except Exception as e:
            return str(e)

```

```swarmauri/standard/llms/concrete/OpenAIToolModel.py

import json
import logging
from typing import List, Literal, Dict, Any
from openai import OpenAI
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.OpenAISchemaConverter import OpenAISchemaConverter

class OpenAIToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gpt-4o', 
    'gpt-4o-2024-05-13',
    'gpt-4-turbo', 
    'gpt-4-turbo-2024-04-09',
    'gpt-4-turbo-preview',
    'gpt-4-0125-preview',
    'gpt-4-1106-preview',
    'gpt-4',
    'gpt-4-0613',
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-0125',
    'gpt-3.5-turbo-1106',
    'gpt-3.5-turbo-0613']
    name: str = "gpt-3.5-turbo-0125"
    type: Literal['OpenAIToolModel'] = 'OpenAIToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [OpenAISchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = OpenAI(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )
        logging.info(f"tool_response: {tool_response}")
        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": func_result,
                    }
                )
        logging.info(f'messages: {messages}')
        agent_response = client.chat.completions.create(
            model=self.name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        logging.info(f"agent_response: {agent_response}")
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation

```

```swarmauri/standard/llms/concrete/GroqModel.py

import json
from typing import List, Optional, Dict, Literal
from groq import Groq
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class GroqModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['llama3-8b-8192', 
    'llama3-70b-8192', 
    'mixtral-8x7b-32768', 
    'gemma-7b-it']
    name: str = "gemma-7b-it"
    type: Literal['GroqModel'] = 'GroqModel'

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        temperature: float = 0.7, 
        max_tokens: int = 256, 
        top_p: float = 1.0, 
        enable_json: bool = False, 
        stop: Optional[List[str]] = None) -> str:

        formatted_messages = self._format_messages(conversation.history)

        client = Groq(api_key=self.api_key)
        stop = stop or []
        
        response_format = {"type": "json_object"} if enable_json else None
        response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            response_format=response_format,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop
        )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        conversation.add_message(AgentMessage(content=message_content))
        return conversation

```

```swarmauri/standard/llms/concrete/GroqToolModel.py

from groq import Groq
import json
from typing import List, Literal, Dict, Any
import logging
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.GroqSchemaConverter import GroqSchemaConverter

class GroqToolModel(LLMBase):
    """
    Provider Documentation: https://console.groq.com/docs/tool-use#models
    """
    api_key: str
    allowed_models: List[str] = ['llama3-8b-8192', 
    'llama3-70b-8192', 
    'mixtral-8x7b-32768', 
    'gemma-7b-it']
    name: str = "gemma-7b-it"
    type: Literal['GroqToolModel'] = 'GroqToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [GroqSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = Groq(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = "auto"

        tool_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )
        logging.info(tool_response)

        agent_message = AgentMessage(content=tool_response.choices[0].message.content) 
                                     #tool_calls=tool_response.choices[0].message.tool_calls)
        conversation.add_message(agent_message)


        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                
                func_message = FunctionMessage(content=func_result, 
                                               name=func_name, 
                                               tool_call_id=tool_call.id)
                conversation.add_message(func_message)
            
        logging.info(conversation.history)
        formatted_messages = self._format_messages(conversation.history)
        agent_response = client.chat.completions.create(
            model=self.name,
            messages=formatted_messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        logging.info(agent_response)
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        return conversation

```

```swarmauri/standard/llms/concrete/MistralModel.py

import json
from typing import List, Literal, Dict
from mistralai.client import MistralClient
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class MistralModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['open-mistral-7b', 
    'open-mixtral-8x7b', 
    'open-mixtral-8x22b', 
    'mistral-small-latest',
    'mistral-medium-latest',
    'mistral-large-latest',
    'codestral'
    ]
    name: str = "open-mixtral-8x7b"
    type: Literal['MistralModel'] = 'MistralModel'

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        temperature: int = 0.7, 
        max_tokens: int = 256, 
        top_p: int = 1,
        enable_json: bool=False, 
        safe_prompt: bool=False):
        
        formatted_messages = self._format_messages(conversation.history)

        client =  MistralClient(api_key=self.api_key)        
        if enable_json:
            response = client.chat(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                response_format={ "type": "json_object" },
                max_tokens=max_tokens,
                top_p=top_p,
                safe_prompt=safe_prompt
            )
        else:
            response = client.chat(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,                
                safe_prompt=safe_prompt
            )
        
        result = json.loads(response.json())
        message_content = result['choices'][0]['message']['content']
        conversation.add_message(AgentMessage(content=message_content))

        return conversation

```

```swarmauri/standard/llms/concrete/MistralToolModel.py

import json
import logging
from typing import List, Literal, Dict, Any
from mistralai.client import MistralClient
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.MistralSchemaConverter import MistralSchemaConverter

class MistralToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['open-mixtral-8x22b', 
    'mistral-small-latest',
    'mistral-large-latest',
    ]
    name: str = "open-mixtral-8x22b"
    type: Literal['MistralToolModel'] = 'MistralToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [MistralSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'tool_call_id']
        #message_properties = ['content', 'role', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024, 
        safe_prompt: bool = False):

        client =  MistralClient(api_key=self.api_key)
        formatted_messages = self._format_messages(conversation.history)

        if toolkit and not tool_choice:
            tool_choice = "auto"
            
        tool_response = client.chat(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
            safe_prompt=safe_prompt
        )

        logging.info(f"tool_response: {tool_response}")

        messages = [formatted_messages[-1], tool_response.choices[0].message]
        tool_calls = tool_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                logging.info(type(tool_call.function.arguments))
                logging.info(tool_call.function.arguments)
                
                func_name = tool_call.function.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": func_result,
                    }
                )
        logging.info(f"messages: {messages}")

        agent_response = client.chat(
            model=self.name,
            messages=messages
        )
        logging.info(f"agent_response: {agent_response}")
        agent_message = AgentMessage(content=agent_response.choices[0].message.content)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")      
        return conversation

```

```swarmauri/standard/llms/concrete/CohereModel.py

import json
import logging
from typing import List, Dict, Literal
import cohere
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class CohereModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['command-light',
    'command', 
    'command-r',
    'command-r-plus']
    name: str = "command-light"
    type: Literal['CohereModel'] = 'CohereModel'
    
    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str,str]]:
        """
        Cohere utilizes the following roles: CHATBOT, SYSTEM, TOOL, USER
        """
        message_properties = ['content', 'role']

        messages = [message.model_dump(include=message_properties) for message in messages]
        for message in messages:
            message['message'] = message.pop('content')
            if message.get('role') == 'assistant':
                message['role'] = 'chatbot'
            message['role'] = message['role'].upper()
        logging.info(messages)
        return messages


    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256):
        # Get next message
        next_message = conversation.history[-1].content

        # Format chat_history
        messages = self._format_messages(conversation.history[:-1])


        client = cohere.Client(api_key=self.api_key)
        response = client.chat(
            model=self.name,
            chat_history=messages,
            message=next_message,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_truncation='OFF',
            connectors=[]
        )
        
        result = json.loads(response.json())
        message_content = result['text']
        conversation.add_message(AgentMessage(content=message_content))
        return conversation

```

```swarmauri/standard/llms/concrete/GeminiProModel.py

import json
from typing import List, Dict, Literal
import google.generativeai as genai
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase


class GeminiProModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['gemini-1.5-pro-latest']
    name: str = "gemini-1.5-pro-latest"
    type: Literal['GeminiProModel'] = 'GeminiProModel'
    
    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        # Remove system instruction from messages
        message_properties = ['content', 'role']
        sanitized_messages = [message.model_dump(include=message_properties) for message in messages 
            if message.role != 'system']

        for message in sanitized_messages:
            if message['role'] == 'assistant':
                message['role'] = 'model'

            # update content naming
            message['parts'] = message.pop('content')

        return sanitized_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        system_context = None
        for message in messages:
            if message.role == 'system':
                system_context = message.content
        return system_context
    
    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
            }

        safety_settings = [
          {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
        ]


        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)


        next_message = formatted_messages.pop()

        client = genai.GenerativeModel(model_name=self.name,
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=system_context)

        convo = client.start_chat(
            history=formatted_messages,
            )

        convo.send_message(next_message['parts'])

        message_content = convo.last.text
        conversation.add_message(AgentMessage(content=message_content))
        return conversation


```

```swarmauri/standard/llms/concrete/AnthropicModel.py

import json
from typing import List, Dict, Literal
import anthropic
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class AnthropicModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['claude-3-opus-20240229', 
    'claude-3-sonnet-20240229', 
    'claude-3-haiku-20240307',
    'claude-2.1',
    'claude-2.0',
    'claude-instant-1.2']
    name: str = "claude-3-haiku-20240307"
    type: Literal['AnthropicModel'] = 'AnthropicModel'

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
       # Get only the properties that we require
        message_properties = ["content", "role"]

        # Exclude FunctionMessages
        formatted_messages = [message.model_dump(include=message_properties) for message in messages if message.role != 'system']
        return formatted_messages

    def _get_system_context(self, messages: List[SubclassUnion[MessageBase]]) -> str:
        system_context = None
        for message in messages:
            if message.role == 'system':
                system_context = message.content
        return system_context

    
    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256):

        # Create client
        client = anthropic.Anthropic(api_key=self.api_key)
        
        # Get system_context from last message with system context in it
        system_context = self._get_system_context(conversation.history)
        formatted_messages = self._format_messages(conversation.history)

        if system_context:
            response = client.messages.create(
                model=self.name,
                messages=formatted_messages,
                system=system_context,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            response = client.messages.create(
                model=self.name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        message_content = response.content[0].text
        conversation.add_message(AgentMessage(content=message_content))
        
        return conversation


```

```swarmauri/standard/llms/concrete/CohereToolModel.py

import logging
import json
from typing import List, Literal
from typing import List, Dict, Any, Literal
import cohere
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.CohereSchemaConverter import CohereSchemaConverter

class CohereToolModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['command-r',
    'command-r-plus']
    name: str = "command-r"
    type: Literal['CohereToolModel'] = 'CohereToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [CohereSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        toolkit=None, 
        temperature=0.3,
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = cohere.Client(api_key=self.api_key)
        preamble = "" # 🚧  Placeholder for implementation logic

        logging.info(f"_schema_convert_tools: {self._schema_convert_tools(toolkit.tools)}")
        logging.info(f"message: {formatted_messages[-1]}")
        logging.info(f"formatted_messages: {formatted_messages}")

        tool_response = client.chat(
            model=self.name, 
            message=formatted_messages[-1]['content'], 
            chat_history=formatted_messages[:-1],
            force_single_step=True,
            tools=self._schema_convert_tools(toolkit.tools)
        )

        logging.info(f"tool_response: {tool_response}")
        logging.info(tool_response.text) 
        tool_results = []
        for tool_call in tool_response.tool_calls:
            logging.info(f"tool_call: {tool_call}")
            func_name = tool_call.name
            func_call = toolkit.get_tool_by_name(func_name)
            func_args = tool_call.parameters
            func_results = func_call(**func_args)
            tool_results.append({"call": tool_call, "outputs": [{'result': func_results}]}) # 🚧 Placeholder for variable key-names

        logging.info(f"tool_results: {tool_results}")
        agent_response = client.chat(
            model=self.name,
            message=formatted_messages[-1]['content'],
            chat_history=formatted_messages[:-1],
            tools=self._schema_convert_tools(toolkit.tools),
            force_single_step=True,
            tool_results=tool_results,
            temperature=temperature
        )

        logging.info(f"agent_response: {agent_response}")
        conversation.add_message(AgentMessage(content=agent_response.text))

        logging.info(f"conversation: {conversation}")
        return conversation


```

```swarmauri/standard/llms/concrete/AnthropicToolModel.py

import json
from typing import List, Dict, Literal, Any
import logging
import anthropic
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.AnthropicSchemaConverter import AnthropicSchemaConverter

class AnthropicToolModel(LLMBase):
    """
    Provider resources: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    """
    api_key: str
    allowed_models: List[str] = ['claude-3-haiku-20240307',
    'claude-3-opus-20240229',
    'claude-3-sonnet-20240229']
    name: str = "claude-3-haiku-20240307"
    type: Literal['AnthropicToolModel'] = 'AnthropicToolModel'
    
    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        schema_result = [AnthropicSchemaConverter().convert(tools[tool]) for tool in tools]
        logging.info(schema_result)
        return schema_result

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'tool_call_id', 'tool_calls']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages

    def predict(self, 
        conversation, 
        toolkit=None, 
        tool_choice=None, 
        temperature=0.7, 
        max_tokens=1024):

        formatted_messages = self._format_messages(conversation.history)

        client = anthropic.Anthropic(api_key=self.api_key)
        if toolkit and not tool_choice:
            tool_choice = {"type":"auto"}

        tool_response = client.messages.create(
            model=self.name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=self._schema_convert_tools(toolkit.tools),
            tool_choice=tool_choice,
        )


        logging.info(f"tool_response: {tool_response}")
        tool_text_response = None
        if tool_response.content[0].type =='text':
            tool_text_response = tool_response.content[0].text
            logging.info(f"tool_text_response: {tool_text_response}")

        for tool_call in tool_response.content:
            if tool_call.type == 'tool_use':
                func_name = tool_call.name
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = tool_call.input
                func_result = func_call(**func_args)


        if tool_text_response:
            agent_response = f"{tool_text_response} {func_result}"
        else:
            agent_response = f"{func_result}"

        agent_message = AgentMessage(content=agent_response)
        conversation.add_message(agent_message)
        logging.info(f"conversation: {conversation}")
        return conversation

```

```swarmauri/standard/llms/concrete/GeminiToolModel.py

import logging
import json
from typing import List, Literal, Dict, Any
import google.generativeai as genai
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.messages.concrete.FunctionMessage import FunctionMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.schema_converters.concrete.GeminiSchemaConverter import GeminiSchemaConverter
import google.generativeai as genai

class GeminiToolModel(LLMBase):
    """
    3rd Party's Resources: https://ai.google.dev/api/python/google/generativeai/protos/
    """
    api_key: str
    allowed_models: List[str] = ['gemini-1.5-pro-latest']
    name: str = "gemini-1.5-pro-latest"
    type: Literal['GeminiToolModel'] = 'GeminiToolModel'

    def _schema_convert_tools(self, tools) -> List[Dict[str, Any]]:
        return [GeminiSchemaConverter().convert(tools[tool]) for tool in tools]

    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        # Remove system instruction from messages
        message_properties = ['content', 'role', 'tool_call_id', 'tool_calls']
        sanitized_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages 
            if message.role != 'system']

        for message in sanitized_messages:
            if message['role'] == 'assistant':
                message['role'] = 'model'

            if message['role'] == 'tool':
                message['role'] == 'user'

            # update content naming
            message['parts'] = message.pop('content')

        return sanitized_messages

    def predict(self, 
        conversation, 
        toolkit=None, 
        temperature=0.7, 
        max_tokens=256):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": max_tokens,
            }

        safety_settings = [
          {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
          },
        ]

        tool_config = {
              "function_calling_config": {
                "mode": "ANY"
              },
            }

        client = genai.GenerativeModel(model_name=self.name,
            safety_settings=safety_settings,
            generation_config=generation_config,
            tool_config=tool_config)

        formatted_messages = self._format_messages(conversation.history)
        logging.info(f'formatted_messages: {formatted_messages}')

        tool_response = client.generate_content(
            formatted_messages,
            tools=self._schema_convert_tools(toolkit.tools),
        )
        logging.info(f'tool_response: {tool_response}')

        formatted_messages.append(tool_response.candidates[0].content)


        logging.info(f"tool_response.candidates[0].content: {tool_response.candidates[0].content}")




        tool_calls = tool_response.candidates[0].content.parts

        tool_results = {}
        for tool_call in tool_calls:
            func_name = tool_call.function_call.name
            func_args = tool_call.function_call.args
            logging.info(f"func_name: {func_name}")
            logging.info(f"func_args: {func_args}")

            func_call = toolkit.get_tool_by_name(func_name)
            func_result = func_call(**func_args)
            logging.info(f"func_result: {func_result}")
            tool_results[func_name] = func_result

        formatted_messages.append(genai.protos.Content(role="function",
            parts=[
                genai.protos.Part(function_response=genai.protos.FunctionResponse(
                    name=fn,
                    response={
                        "result": val,  # Return the API response to Gemini
                    },
                )) for fn, val in tool_results.items()]
            ))

        logging.info(f'formatted_messages: {formatted_messages}')

        agent_response = client.generate_content(formatted_messages)

        logging.info(f'agent_response: {agent_response}')
        conversation.add_message(AgentMessage(content=agent_response.text))

        logging.info(f'conversation: {conversation}')
        return conversation

```

```swarmauri/standard/llms/concrete/PerplexityModel.py

import json
from typing import List, Dict, Literal, Optional
import requests
from swarmauri.core.typing import SubclassUnion

from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage
from swarmauri.standard.llms.base.LLMBase import LLMBase

class PerplexityModel(LLMBase):
    api_key: str
    allowed_models: List[str] = ['llama-3-sonar-small-32k-chat',
        'llama-3-sonar-small-32k-online',
        'llama-3-sonar-large-32k-chat',
        'llama-3-sonar-large-32k-online',
        'llama-3-8b-instruct',
        'llama-3-70b-instruct',
        'mixtral-8x7b-instruct']
    name: str = "mixtral-8x7b-instruct"
    type: Literal['PerplexityModel'] = 'PerplexityModel'
    
    def _format_messages(self, messages: List[SubclassUnion[MessageBase]]) -> List[Dict[str, str]]:
        message_properties = ['content', 'role', 'name']
        formatted_messages = [message.model_dump(include=message_properties, exclude_none=True) for message in messages]
        return formatted_messages
    
    def predict(self, 
        conversation, 
        temperature=0.7, 
        max_tokens=256, 
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        return_citations: Optional[bool] = False,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None
        ):


        if top_p and top_k:
            raise ValueError('Do not set top_p and top_k')


        formatted_messages = self._format_messages(conversation.history)

        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": self.name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_citations": True,
            "top_k": top_k,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)
        message_content = response.text
        conversation.add_message(AgentMessage(content=message_content))
        return conversation





```

```swarmauri/standard/agents/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/agents/base/__init__.py



```

```swarmauri/standard/agents/base/AgentToolMixin.py

from pydantic import BaseModel, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.toolkits.base.ToolkitBase import ToolkitBase
from swarmauri.core.agents.IAgentToolkit import IAgentToolkit

class AgentToolMixin(IAgentToolkit, BaseModel):
    toolkit: SubclassUnion[ToolkitBase]
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    

```

```swarmauri/standard/agents/base/AgentBase.py

from typing import Any, Optional, Dict, Union, Literal
from pydantic import ConfigDict, Field, field_validator
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.standard.llms.base.LLMBase import LLMBase

class AgentBase(IAgent, ComponentBase):
    llm: SubclassUnion[LLMBase]
    resource: ResourceTypes =  Field(default=ResourceTypes.AGENT.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['AgentBase'] = 'AgentBase'

    def exec(self, input_str: Optional[Union[str, IMessage]] = "", llm_kwargs: Optional[Dict] = {}) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')

```

```swarmauri/standard/agents/base/AgentVectorStoreMixin.py

from pydantic import BaseModel, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.agents.IAgentVectorStore import IAgentVectorStore
from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase

class AgentVectorStoreMixin(IAgentVectorStore, BaseModel):
    vector_store: SubclassUnion[VectorStoreBase]
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

```

```swarmauri/standard/agents/base/AgentRetrieveMixin.py

from abc import ABC
from typing import List
from pydantic import BaseModel, ConfigDict, field_validator, Field
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.core.agents.IAgentRetrieve import IAgentRetrieve

class AgentRetrieveMixin(IAgentRetrieve, BaseModel):
    last_retrieved: List[Document] = Field(default_factory=list)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)



```

```swarmauri/standard/agents/base/AgentSystemContextMixin.py

from typing import Union
from pydantic import BaseModel, field_validator

from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage
from swarmauri.core.agents.IAgentSystemContext import IAgentSystemContext


class AgentSystemContextMixin(IAgentSystemContext, BaseModel):
    system_context:  Union[SystemMessage, str]

    @field_validator('system_context', mode='before')
    def set_system_context(cls, value: Union[str, SystemMessage]) -> SystemMessage:
        if isinstance(value, str):
            return SystemMessage(content=value)
        return value

```

```swarmauri/standard/agents/base/AgentConversationMixin.py

from pydantic import BaseModel, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class AgentConversationMixin(IAgentConversation, BaseModel):
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

```

```swarmauri/standard/agents/concrete/__init__.py



```

```swarmauri/standard/agents/concrete/ToolAgent.py

from pydantic import ConfigDict
from typing import Any, Optional, Union, Dict, Literal
import json
import logging
from swarmauri.core.messages import IMessage

from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.agents.base.AgentToolMixin import AgentToolMixin
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage

from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class ToolAgent(AgentToolMixin, AgentConversationMixin, AgentBase):
    llm: SubclassUnion[LLMBase]
    toolkit: SubclassUnion[Toolkit]
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ToolAgent'] = 'ToolAgent'
    
    def exec(self, 
        input_data: Optional[Union[str, IMessage]] = "",  
        llm_kwargs: Optional[Dict] = {}) -> Any:

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(content=input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        self.conversation.add_message(human_message)

        #predict a response        
        self.conversation = self.llm.predict(
            conversation=self.conversation, 
            toolkit=self.toolkit, 
            **llm_kwargs)

        logging.info(self.conversation.get_last().content)

        return self.conversation.get_last().content

```

```swarmauri/standard/agents/concrete/SimpleConversationAgent.py

from typing import Any, Optional, Dict, Literal

from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage

from swarmauri.core.typing import SubclassUnion # 🚧  Placeholder
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase # 🚧  Placeholder

class SimpleConversationAgent(AgentConversationMixin, AgentBase):
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    type: Literal['SimpleConversationAgent'] = 'SimpleConversationAgent'
    
    def exec(self, 
        input_str: Optional[str] = "",
        llm_kwargs: Optional[Dict] = {} 
        ) -> Any:
        
        if input_str:
            human_message = HumanMessage(content=input_str)
            self.conversation.add_message(human_message)
        
        self.llm.predict(conversation=self.conversation, **llm_kwargs)
        return self.conversation.get_last().content

```

```swarmauri/standard/agents/concrete/RagAgent.py

from typing import Any, Optional, Union, Dict, Literal
from swarmauri.core.messages import IMessage

from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentRetrieveMixin import AgentRetrieveMixin
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.agents.base.AgentVectorStoreMixin import AgentVectorStoreMixin
from swarmauri.standard.agents.base.AgentSystemContextMixin import AgentSystemContextMixin

from swarmauri.standard.messages.concrete import (HumanMessage, 
                                                  SystemMessage,
                                                  AgentMessage)

from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase
from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase

class RagAgent(AgentRetrieveMixin, 
               AgentVectorStoreMixin, 
               AgentSystemContextMixin, 
               AgentConversationMixin, 
               AgentBase):
    """
    RagAgent (Retriever-And-Generator Agent) extends DocumentAgentBase,
    specialized in retrieving documents based on input queries and generating responses.
    """
    llm: SubclassUnion[LLMBase]
    conversation: SubclassUnion[ConversationBase]
    vector_store: SubclassUnion[VectorStoreBase]
    system_context:  Union[SystemMessage, str]
    type: Literal['RagAgent'] = 'RagAgent'
    
    def _create_preamble_context(self):
        substr = self.system_context.content
        substr += '\n\n'
        substr += '\n'.join([doc.content for doc in self.last_retrieved])
        return substr

    def _create_post_context(self):
        substr = '\n'.join([doc.content for doc in self.last_retrieved])
        substr += '\n\n'
        substr += self.system_context.content
        return substr

    def exec(self, 
             input_data: Optional[Union[str, IMessage]] = "", 
             top_k: int = 5, 
             preamble: bool = True,
             fixed: bool = False,
             llm_kwargs: Optional[Dict] = {}
             ) -> Any:
        try:
            # Check if the input is a string, then wrap it in a HumanMessage
            if isinstance(input_data, str):
                human_message = HumanMessage(content=input_data)
            elif isinstance(input_data, IMessage):
                human_message = input_data
            else:
                raise TypeError("Input data must be a string or an instance of Message.")
            
            # Add the human message to the conversation
            self.conversation.add_message(human_message)

            # Retrieval and set new substr for system context
            if top_k > 0 and len(self.vector_store.documents) > 0:
                self.last_retrieved = self.vector_store.retrieve(query=input_data, top_k=top_k)

                if preamble:
                    substr = self._create_preamble_context()
                else:
                    substr = self._create_post_context()

            else:
                if fixed:
                    if preamble:
                        substr = self._create_preamble_context()
                    else:
                        substr = self._create_post_context()
                else:
                    substr = self.system_context.content
                    self.last_retrieved = []
                
            # Use substr to set system context
            system_context = SystemMessage(content=substr)
            self.conversation.system_context = system_context
            

            # Retrieve the conversation history and predict a response
            if llm_kwargs:
                self.llm.predict(conversation=self.conversation, **llm_kwargs)
            else:
                self.llm.predict(conversation=self.conversation)
                
            return self.conversation.get_last().content

        except Exception as e:
            print(f"RagAgent error: {e}")
            raise e

```

```swarmauri/standard/agents/concrete/QAAgent.py

from typing import Any, Optional, Dict, Literal

from swarmauri.standard.conversations.concrete.MaxSizeConversation import MaxSizeConversation
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
from swarmauri.standard.agents.base.AgentBase import AgentBase

class QAAgent(AgentBase):
    conversation: MaxSizeConversation = MaxSizeConversation(max_size=2)
    type: Literal['QAAgent'] = 'QAAgent'
    
    def exec(self, 
        input_str: Optional[str] = "",
        llm_kwargs: Optional[Dict] = {} 
        ) -> Any:
        
        
        self.conversation.add_message(HumanMessage(content=input_str))
        self.llm.predict(conversation=self.conversation, **llm_kwargs)
        
        return self.conversation.get_last().content

```

```swarmauri/standard/utils/__init__.py



```

```swarmauri/standard/utils/load_documents_from_json.py

import json
from typing import List
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument

def load_documents_from_json_file(json_file_path):
    documents = []
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    documents = [
        EmbeddedDocument(id=str(_), 
        content=doc['content'], 
        metadata={"document_name": doc['document_name']}) 
        for _, doc in enumerate(data) if doc['content']
        ]

    return documents

def load_documents_from_json(json):
    documents = []
    data = json.loads(json)
    documents = [
        EmbeddedDocument(id=str(_), 
        content=doc['content'], 
        metadata={"document_name": doc['document_name']}) 
        for _, doc in enumerate(data) if doc['content']
        ]
    return documents


```

```swarmauri/standard/utils/get_class_hash.py

import hashlib
import inspect

def get_class_hash(cls):
    """
    Generates a unique hash value for a given class.

    This function uses the built-in `hashlib` and `inspect` modules to create a hash value based on the class' methods
    and properties. The members of the class are first sorted to ensure a consistent order, and then the hash object is
    updated with each member's name and signature.

    Parameters:
    - cls (type): The class object to calculate the hash for.

    Returns:
    - str: The generated hexadecimal hash value.
    """
    hash_obj = hashlib.sha256()

    # Get the list of methods and properties of the class
    members = inspect.getmembers(cls, predicate=inspect.isfunction)
    members += inspect.getmembers(cls, predicate=inspect.isdatadescriptor)

    # Sort members to ensure consistent order
    members.sort()

    # Update the hash with each member's name and signature
    for name, member in members:
        hash_obj.update(name.encode('utf-8'))
        if inspect.isfunction(member):
            sig = inspect.signature(member)
            hash_obj.update(str(sig).encode('utf-8'))

    # Return the hexadecimal digest of the hash
    return hash_obj.hexdigest()


```

```swarmauri/standard/utils/sql_log.py

import sqlite3
from datetime import datetime
import asyncio


def sql_log(self, db_path: str, conversation_id, model_name, prompt, response, start_datetime, end_datetime):
    try:
        duration = (end_datetime - start_datetime).total_seconds()
        start_datetime = start_datetime.isoformat()
        end_datetime = end_datetime.isoformat()
        conversation_id = conversation_id
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversations
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        conversation_id TEXT, 
                        model_name TEXT, 
                        prompt TEXT, 
                        response TEXT, 
                        start_datetime TEXT, 
                        end_datetime TEXT,
                        duration NUMERIC)''')
        cursor.execute('''INSERT INTO conversations (
                        conversation_id, 
                        model_name, 
                        prompt, 
                        response, 
                        start_datetime, 
                        end_datetime,
                        duration) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                       (conversation_id, 
                        model_name, 
                        prompt, 
                        response, 
                        start_datetime, 
                        end_datetime, 
                        duration))
        conn.commit()
        conn.close()
    except:
        raise



def sql_log_decorator(func):
    async def wrapper(self, *args, **kwargs):
        start_datetime = datetime.now()
        try:
            # Execute the function
            result = await func(self, *args, **kwargs)
        except Exception as e:
            # Handle errors within the decorated function
            self.agent.conversation._history.pop(0)
            print(f"chatbot_function error: {e}")
            return "", [], kwargs['history']  

        end_datetime = datetime.now()
        
        # SQL logging
        # Unpacking the history and other required parameters from kwargs if they were used
        history = kwargs.get('history', [])
        message = kwargs.get('message', '')
        response = result[1]  # Assuming the response is the second item in the returned tuple
        model_name = kwargs.get('model_name', '')
        conversation_id = str(self.agent.conversation.id)
        sql_log(conversation_id, model_name, message, response, start_datetime, end_datetime)
        return result
    return wrapper


class SqlLogMeta(type):
    def __new__(cls, name, bases, dct):
        for key, value in dct.items():
            if callable(value) and not key.startswith('__'):
                dct[key] = sql_log(value)
        return super().__new__(cls, name, bases, dct)

```

```swarmauri/standard/utils/memoize.py

def memoize(func):
    cache = {}
    def memoized_func(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return memoized_func
    
class MemoizingMeta(type):
    def __new__(cls, name, bases, dct):
        for key, value in dct.items():
            if callable(value) and not key.startswith('__'):
                dct[key] = memoize(value)
        return super().__new__(cls, name, bases, dct)


```

```swarmauri/standard/utils/apply_metaclass.py

def apply_metaclass_to_cls(cls, metaclass):
    # Create a new class using the metaclass, with the same name, bases, and attributes as the original class
    new_class = metaclass(cls.__name__, cls.__bases__, dict(cls.__dict__))
    return new_class


```

```swarmauri/standard/utils/decorate.py

def decorate_cls(cls, decorator_fn):
    import types
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if isinstance(attr, types.FunctionType):
            setattr(cls, attr_name, decorator_fn(attr))
    return cls

def decorate_instance(instance, decorator_fn):
    import types
    for attr_name in dir(instance):
        attr = getattr(instance, attr_name)
        if isinstance(attr, types.MethodType):
            setattr(instance, attr_name, decorator_fn(attr.__func__).__get__(instance))

def decorate_instance_method(instance, method_name, decorator_fn):
    # Get the method from the instance
    original_method = getattr(instance, method_name)
    
    # Decorate the method
    decorated_method = decorator_fn(original_method)
    
    # Rebind the decorated method to the instance
    setattr(instance, method_name, decorated_method.__get__(instance, instance.__class__))

```

```swarmauri/standard/utils/json_validator.py

# swarmauri/standard/utils/json_validator.py
import json
import jsonschema
from jsonschema import validate

def load_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)

def validate_json(data: dict, schema_file: str) -> bool:
    schema = load_json_file(schema_file)
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        print(f"JSON validation error: {err.message}")
        return False
    return True

```

```swarmauri/standard/conversations/__init__.py



```

```swarmauri/standard/conversations/base/__init__.py



```

```swarmauri/standard/conversations/base/ConversationSystemContextMixin.py

from abc import ABC
from typing import Optional, Literal
from pydantic import BaseModel
from swarmauri.core.conversations.ISystemContext import ISystemContext
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

class ConversationSystemContextMixin(ISystemContext, BaseModel):
    system_context: Optional[SystemMessage]


```

```swarmauri/standard/conversations/base/ConversationBase.py

from typing import List, Union, Literal
from pydantic import Field, PrivateAttr, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.messages.base.MessageBase import MessageBase
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.conversations.IConversation import IConversation

class ConversationBase(IConversation, ComponentBase):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """
    _history: List[SubclassUnion[MessageBase]] = PrivateAttr(default_factory=list)
    resource: ResourceTypes =  Field(default=ResourceTypes.CONVERSATION.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ConversationBase'] = 'ConversationBase'

    @property
    def history(self) -> List[SubclassUnion[MessageBase]]:
        """
        Provides read-only access to the conversation history.
        """
        return self._history
    
    def add_message(self, message: SubclassUnion[MessageBase]):
        self._history.append(message)

    def get_last(self) -> Union[SubclassUnion[MessageBase], None]:
        if self._history:
            return self._history[-1]
        return None

    def clear_history(self):
        self._history.clear()


```

```swarmauri/standard/conversations/concrete/__init__.py



```

```swarmauri/standard/conversations/concrete/MaxSizeConversation.py

from typing import Literal
from pydantic import Field
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize

class MaxSizeConversation(IMaxSize, ConversationBase):
    max_size: int = Field(default=2, gt=1)
    type: Literal['MaxSizeConversation'] = 'MaxSizeConversation'

    def add_message(self, message: IMessage):
        """Adds a message and ensures the conversation does not exceed the max size."""
        super().add_message(message)
        self._enforce_max_size_limit()

    def _enforce_max_size_limit(self):
        """
        Enforces the maximum size limit of the conversation history.
        If the current history size exceeds the maximum size, the oldest messages are removed.
        We pop two messages (one for the user's prompt, one for the assistant's response)
        """
        while len(self._history) > self.max_size:
            
            self._history.pop(0)
            self._history.pop(0)

```

```swarmauri/standard/conversations/concrete/MaxSystemContextConversation.py

from typing import Optional, Union, List, Literal
from pydantic import Field, ConfigDict, field_validator
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase
from swarmauri.standard.conversations.base.ConversationSystemContextMixin import ConversationSystemContextMixin
from swarmauri.standard.messages.concrete import SystemMessage, AgentMessage, HumanMessage
from swarmauri.standard.exceptions.concrete import IndexErrorWithContext

class MaxSystemContextConversation(IMaxSize, ConversationSystemContextMixin, ConversationBase):
    system_context: Optional[SystemMessage] = SystemMessage(content="")
    max_size: int = Field(default=2, gt=1)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['MaxSystemContextConversation'] = 'MaxSystemContextConversation'
    
    @field_validator('system_context', mode='before')
    def set_system_context(cls, value: Union[str, SystemMessage]) -> SystemMessage:
        if isinstance(value, str):
            return SystemMessage(content=value)
        return value
    
    @property
    def history(self) -> List[IMessage]:
        """
        Get the conversation history, ensuring it starts with a 'user' message and alternates correctly between 'user' and 'assistant' roles.
        The maximum number of messages returned does not exceed max_size + 1.
        """
        res = []  # Start with an empty list to build the proper history

        # Attempt to find the first 'user' message in the history.
        user_start_index = -1
        for index, message in enumerate(self._history):
            if isinstance(message, HumanMessage):  # Identify user message
                user_start_index = index
                break

        # If no 'user' message is found, just return the system context.
        if user_start_index == -1:
            return [self.system_context]

        # Build history from the first 'user' message ensuring alternating roles.
        res.append(self.system_context)
        alternating = True
        count = 0 
        for message in self._history[user_start_index:]:
            if count >= self.max_size: # max size
                break
            if alternating and isinstance(message, HumanMessage) or not alternating and isinstance(message, AgentMessage):
                res.append(message)
                alternating = not alternating
                count += 1
            elif not alternating and isinstance(message, HumanMessage):
                # If we find two 'user' messages in a row when expecting an 'assistant' message, we skip this 'user' message.
                continue
            else:
                # If there is no valid alternate message to append, break the loop
                break

        return res

    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and ensures history does not exceed the max size.
        """
        if isinstance(message, SystemMessage):
            raise ValueError(f"System context cannot be set through this method on {self.__class_name__}.")
        elif isinstance(message, IMessage):
            self._history.append(message)
        else:
            raise ValueError(f"Must use a subclass of IMessage")
        self._enforce_max_size_limit()
        
    def _enforce_max_size_limit(self):
        """
        Remove messages from the beginning of the conversation history if the limit is exceeded.
        We add one to max_size to account for the system context message
        """
        try:
            while len(self._history) > self.max_size + 1:
                self._history.pop(0)
                self._history.pop(0)
        except IndexError as e:
            raise IndexErrorWithContext(e)


```

```swarmauri/standard/conversations/concrete/SessionCacheConversation.py

from typing import Optional, Union, List, Literal
from pydantic import Field, ConfigDict
from collections import deque
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase
from swarmauri.standard.conversations.base.ConversationSystemContextMixin import ConversationSystemContextMixin
from swarmauri.standard.messages.concrete import SystemMessage, AgentMessage, HumanMessage, FunctionMessage
from swarmauri.standard.exceptions.concrete import IndexErrorWithContext


class SessionCacheConversation(IMaxSize, ConversationSystemContextMixin, ConversationBase):
    max_size: int = Field(default=2, gt=1)
    system_context: Optional[SystemMessage] = None
    session_max_size: int = Field(default=-1)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['SessionCacheConversation'] = 'SessionCacheConversation'

    def __init__(self, **data):
        super().__init__(**data)
        if self.session_max_size == -1:
            self.session_max_size = self.max_size

    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and ensures history does not exceed the max size.
        This only allows system context to be set through the system context method.
        We are forcing the SystemContext to be a preamble only.
        """
        if isinstance(message, SystemMessage):
            raise ValueError(f"System context cannot be set through this method on {self.__class_name__}.")
        if not self._history and not isinstance(message, HumanMessage):
            raise ValueError("The first message in the history must be an HumanMessage.")
        if self._history and isinstance(self._history[-1], HumanMessage) and isinstance(message, HumanMessage):
            raise ValueError("Cannot have two repeating HumanMessages.")
        
        super().add_message(message)


    def session_to_dict(self) -> List[dict]:
        """
        Converts session messages to a list of dictionaries.
        """
        included_fields = {"role", "content"}
        return [message.dict(include=included_fields) for message in self.session]
    
    @property
    def session(self) -> List[IMessage]:
        return self._history[-self.session_max_size:]

    @property
    def history(self):
        res = []
        if not self._history or self.max_size == 0:
            if self.system_context:
                return [self.system_context]
            else:
                return []

        # Initialize alternating with the expectation to start with HumanMessage
        alternating = True
        count = 0

        for message in self._history[-self.max_size:]:
            if isinstance(message, HumanMessage) and alternating:
                res.append(message)
                alternating = not alternating  # Switch to expecting AgentMessage
                count += 1
            elif isinstance(message, AgentMessage) and not alternating:
                res.append(message)
                alternating = not alternating  # Switch to expecting HumanMessage
                count += 1

            if count >= self.max_size:
                break
                
        if self.system_context:
            res = [self.system_context] + res
            
        return res



```

```swarmauri/standard/conversations/concrete/Conversation.py

from typing import Literal
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class Conversation(ConversationBase):
    """
    Concrete implementation of ConversationBase, managing conversation history and operations.
    """    
    type: Literal['Conversation'] = 'Conversation'

```

```swarmauri/standard/documents/__init__.py

from .concrete import *
from .base import *

```

```swarmauri/standard/documents/base/__init__.py



```

```swarmauri/standard/documents/base/DocumentBase.py

from typing import Dict, Optional, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.vectors.concrete.Vector import Vector


class DocumentBase(IDocument, ComponentBase):
    content: str
    metadata: Dict = {}
    embedding: Optional[Vector] = None
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.DOCUMENT.value, frozen=True)
    type: Literal['DocumentBase'] = 'DocumentBase'

```

```swarmauri/standard/documents/concrete/__init__.py

from .Document import Document

```

```swarmauri/standard/documents/concrete/Document.py

from typing import Literal
from swarmauri.standard.documents.base.DocumentBase import DocumentBase

class Document(DocumentBase):
    type: Literal['Document'] = 'Document'

```

```swarmauri/standard/messages/__init__.py



```

```swarmauri/standard/messages/base/__init__.py



```

```swarmauri/standard/messages/base/MessageBase.py

from typing import Optional, Tuple, Literal
from pydantic import PrivateAttr, ConfigDict, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.messages.IMessage import IMessage

class MessageBase(IMessage, ComponentBase):
    content: str
    role: str
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.MESSAGE.value, frozen=True)
    type: Literal['MessageBase'] = 'MessageBase'


```

```swarmauri/standard/messages/concrete/__init__.py

from .HumanMessage import HumanMessage
from .AgentMessage import AgentMessage
from .FunctionMessage import FunctionMessage
from .SystemMessage import SystemMessage

```

```swarmauri/standard/messages/concrete/AgentMessage.py

from typing import Optional, Any, Literal
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class AgentMessage(MessageBase):
    content: Optional[str] = None
    role: str = Field(default='assistant')
    #tool_calls: Optional[Any] = None
    name: Optional[str] = None
    type: Literal['AgentMessage'] = 'AgentMessage'
    usage: Optional[Any] = None # 🚧 Placeholder for CompletionUsage(input_tokens, output_tokens, completion time, etc)

```

```swarmauri/standard/messages/concrete/HumanMessage.py

from typing import Optional, Any, Literal
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class HumanMessage(MessageBase):
    content: str
    role: str = Field(default='user')
    name: Optional[str] = None
    type: Literal['HumanMessage'] = 'HumanMessage'    

```

```swarmauri/standard/messages/concrete/FunctionMessage.py

from typing import Literal, Optional, Any
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class FunctionMessage(MessageBase):
    content: str
    role: str = Field(default='tool')
    tool_call_id: str
    name: str
    type: Literal['FunctionMessage'] = 'FunctionMessage'
    usage: Optional[Any] = None # 🚧 Placeholder for CompletionUsage(input_tokens, output_tokens, completion time, etc)

```

```swarmauri/standard/messages/concrete/SystemMessage.py

from typing import Optional, Any, Literal
from pydantic import Field
from swarmauri.standard.messages.base.MessageBase import MessageBase

class SystemMessage(MessageBase):
    content: str
    role: str = Field(default='system')
    type: Literal['SystemMessage'] = 'SystemMessage'

```

```swarmauri/standard/parsers/__init__.py



```

```swarmauri/standard/parsers/base/__init__.py



```

```swarmauri/standard/parsers/base/ParserBase.py

from abc import ABC, abstractmethod
from typing import Optional, Union, List, Any, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.documents.IDocument import IDocument

class ParserBase(ComponentBase, ABC):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing classes
    should provide concrete implementations for these methods tailored to their specific
    chunking algorithms.
    """
    resource: Optional[str] =  Field(default=ResourceTypes.PARSER.value)
    type: Literal['ParserBase'] = 'ParserBase'
    
    @abstractmethod
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Public method to parse input data (either a str or a Message) into a list of Document instances.
        
        This method leverages the abstract _parse_data method which must be
        implemented by subclasses to define specific parsing logic.
        """
        pass


```

```swarmauri/standard/parsers/concrete/__init__.py



```

```swarmauri/standard/parsers/concrete/CSVParser.py

import csv
from io import StringIO
from typing import List, Union, Any, Literal
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class CSVParser(ParserBase):
    """
    Concrete implementation of IParser for parsing CSV formatted text into Document instances.

    The parser can handle input as a CSV formatted string or from a file, with each row
    represented as a separate Document. Assumes the first row is the header which will
    be used as keys for document metadata.
    """
    type: Literal['CSVParser'] = 'CSVParser'
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the given CSV data into a list of Document instances.

        Parameters:
        - data (Union[str, Any]): The input data to parse, either as a CSV string or file path.

        Returns:
        - List[IDocument]: A list of documents parsed from the CSV data.
        """
        # Prepare an in-memory string buffer if the data is provided as a string
        if isinstance(data, str):
            data_stream = StringIO(data)
        else:
            raise ValueError("Data provided is not a valid CSV string")

        # Create a list to hold the parsed documents
        documents: List[IDocument] = []

        # Read CSV content row by row
        reader = csv.DictReader(data_stream)
        for row in reader:
            # Each row represents a document, where the column headers are metadata fields
            document = Document(doc_id=row.get('id', None), 
                                        content=row.get('content', ''), 
                                        metadata=row)
            documents.append(document)

        return documents

```

```swarmauri/standard/parsers/concrete/EntityRecognitionParser.py

import spacy
from typing import List, Union, Any, Literal
from pydantic import PrivateAttr
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class EntityRecognitionParser(ParserBase):
    """
    EntityRecognitionParser leverages NER capabilities to parse text and 
    extract entities with their respective tags such as PERSON, LOCATION, ORGANIZATION, etc.
    """
    _nlp: Any = PrivateAttr()
    type: Literal['EntityRecognitionParser'] = 'EntityRecognitionParser'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load a SpaCy model. The small model is used for demonstration; larger models provide improved accuracy.
        self._nlp = spacy.load("en_core_web_sm")
    
    def parse(self, text: Union[str, Any]) -> List[IDocument]:
        """
        Parses the input text, identifies entities, and returns a list of documents with entities tagged.

        Parameters:
        - text (Union[str, Any]): The input text to be parsed and analyzed for entities.

        Returns:
        - List[IDocument]: A list of IDocument instances representing the identified entities in the text.
        """
        # Ensure the input is a string type before processing
        if not isinstance(text, str):
            text = str(text)
        
        # Apply the NER model
        doc = self._nlp(text)

        # Compile identified entities into documents
        entities_docs = []
        for ent in doc.ents:
            # Create a document for each entity with metadata carrying entity type
            entity_doc = Document(doc_id=ent.text, content=ent.text, metadata={"entity_type": ent.label_})
            entities_docs.append(entity_doc)
        
        return entities_docs

```

```swarmauri/standard/parsers/concrete/HTMLTagStripParser.py

import html
import re
from typing import Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class HTMLTagStripParser(ParserBase):
    """
    A concrete parser that removes HTML tags and unescapes HTML content,
    leaving plain text.
    """
    type: Literal['HTMLTagStripParser'] = 'HTMLTagStripParser'

    def parse(self, data: str):
        """
        Strips HTML tags from input data and unescapes HTML content.
        
        Args:
            data (str): The HTML content to be parsed.
        
        Returns:
            List[IDocument]: A list containing a single IDocument instance of the stripped text.
        """

        # Ensure that input is a string
        if not isinstance(data, str):
            raise ValueError("HTMLTagStripParser expects input data to be of type str.")
        
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', data)  # Matches anything in < > and replaces it with empty string
        
        # Unescape HTML entities
        text = html.unescape(text)

        # Wrap the cleaned text into a Document and return it in a list
        document = Document(content=text, metadata={"original_length": len(data)})
        
        return [document]

```

```swarmauri/standard/parsers/concrete/KeywordExtractorParser.py

import yake
from typing import List, Union, Any, Literal
from pydantic import ConfigDict, PrivateAttr
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class KeywordExtractorParser(ParserBase):
    """
    Extracts keywords from text using the YAKE keyword extraction library.
    """
    lang: str = 'en'
    num_keywords: int = 10
    _kw_extractor: yake.KeywordExtractor = PrivateAttr(default=None)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['KeywordExtractorParser'] = 'KeywordExtractorParser'
    
    def __init__(self, **data):
        super().__init__(**data)
        self._kw_extractor = yake.KeywordExtractor(lan=self.lang,
                                                   n=3, 
                                                   dedupLim=0.9, 
                                                   dedupFunc='seqm', 
                                                   windowsSize=1, 
                                                   top=self.num_keywords, 
                                                   features=None)
    

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Extract keywords from input text and return as list of Document instances containing keyword information.

        Parameters:
        - data (Union[str, Any]): The input text from which to extract keywords.

        Returns:
        - List[Document]: A list of Document instances, each containing information about an extracted keyword.
        """
        # Ensure data is in string format for analysis
        text = str(data) if not isinstance(data, str) else data

        # Extract keywords using YAKE
        keywords = self._kw_extractor.extract_keywords(text)

        # Create Document instances for each keyword
        documents = [Document(content=keyword, metadata={"score": score}) for index, (keyword, score) in enumerate(keywords)]
        
        return documents

```

```swarmauri/standard/parsers/concrete/MarkdownParser.py

import re
from typing import List, Tuple, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase


class MarkdownParser(ParserBase):
    """
    A concrete implementation of the IParser interface that parses Markdown text.
    
    This parser takes Markdown formatted text, converts it to HTML using Python's
    markdown library, and then uses BeautifulSoup to extract plain text content. The
    resulting plain text is then wrapped into Document instances.
    """
    rules: List[Tuple[str, str]] = [
            (r'###### (.*)', r'<h6>\1</h6>'),
            (r'##### (.*)', r'<h5>\1</h5>'),
            (r'#### (.*)', r'<h4>\1</h4>'),
            (r'### (.*)', r'<h3>\1</h3>'),
            (r'## (.*)', r'<h2>\1</h2>'),
            (r'# (.*)', r'<h1>\1</h1>'),
            (r'\*\*(.*?)\*\*', r'<strong>\1</strong>'),
            (r'\*(.*?)\*', r'<em>\1</em>'),
            (r'!\[(.*?)\]\((.*?)\)', r'<img alt="\1" src="\2" />'),
            (r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>'),
            (r'\n\n', r'<p>'),
            (r'\n', r'<br>'),
        ]
    type: Literal['MarkdownParser'] = 'MarkdownParser'

    def parse(self, data: str) -> List[Document]:
        documents = []
        for pattern, repl in self.rules:
            data = re.sub(pattern, repl, data)
        documents.append( Document(content=data, metadata={} ))
        
        return documents

```

```swarmauri/standard/parsers/concrete/OpenAPISpecParser.py

import yaml
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class OpenAPISpecParser(ParserBase):
    """
    A parser that processes OpenAPI Specification files (YAML or JSON format)
    and extracts information into structured Document instances. 
    This is useful for building documentation, APIs inventory, or analyzing the API specification.
    """
    type: Literal['OpenAPISpecParser'] = 'OpenAPISpecParser'
    
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses an OpenAPI Specification from a YAML or JSON string into a list of Document instances.

        Parameters:
        - data (Union[str, Any]): The OpenAPI specification in YAML or JSON format as a string.

        Returns:
        - List[IDocument]: A list of Document instances representing the parsed information.
        """
        try:
            # Load the OpenAPI spec into a Python dictionary
            spec_dict = yaml.safe_load(data)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse the OpenAPI specification: {e}")
        
        documents = []
        # Iterate over paths in the OpenAPI spec to extract endpoint information
        for path, path_item in spec_dict.get("paths", {}).items():
            for method, operation in path_item.items():
                # Create a Document instance for each operation
                content = yaml.dump(operation)
                metadata = {
                    "path": path,
                    "method": method.upper(),
                    "operationId": operation.get("operationId", "")
                }
                document = Document(content=content, metadata=metadata)
                documents.append(document)

        return documents

```

```swarmauri/standard/parsers/concrete/PhoneNumberExtractorParser.py

import re
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class PhoneNumberExtractorParser(ParserBase):
    """
    A parser that extracts phone numbers from the input text.
    Utilizes regular expressions to identify phone numbers in various formats.
    """
    type: Literal['PhoneNumberExtractorParser'] = 'PhoneNumberExtractorParser'
    
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses the input data, looking for phone numbers employing a regular expression.
        Each phone number found is contained in a separate IDocument instance.

        Parameters:
        - data (Union[str, Any]): The input text to be parsed for phone numbers.

        Returns:
        - List[IDocument]: A list of IDocument instances, each containing a phone number.
        """
        # Define a regular expression for phone numbers.
        # This is a simple example and might not capture all phone number formats accurately.
        phone_regex = r'\+?\d[\d -]{8,}\d'

        # Find all occurrences of phone numbers in the text
        phone_numbers = re.findall(phone_regex, str(data))

        # Create a new IDocument for each phone number found
        documents = [Document(content=phone_number, metadata={}) for index, phone_number in enumerate(phone_numbers)]

        return documents

```

```swarmauri/standard/parsers/concrete/PythonParser.py

import ast
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase
from swarmauri.core.documents.IDocument import IDocument

class PythonParser(ParserBase):
    """
    A parser that processes Python source code to extract structural elements
    such as functions, classes, and their docstrings.
    
    This parser utilizes the `ast` module to parse the Python code into an abstract syntax tree (AST)
    and then walks the tree to extract relevant information.
    """
    type: Literal['PythonParser'] = 'PythonParser'
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the given Python source code to extract structural elements.

        Args:
            data (Union[str, Any]): The input Python source code as a string.

        Returns:
            List[IDocument]: A list of IDocument objects, each representing a structural element 
                             extracted from the code along with its metadata.
        """
        if not isinstance(data, str):
            raise ValueError("PythonParser expects a string input.")
        
        documents = []
        tree = ast.parse(data)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                element_name = node.name
                docstring = ast.get_docstring(node)
                
                # Get the source code snippet
                source_code = ast.get_source_segment(data, node)
                
                # Create a metadata dictionary
                metadata = {
                    "type": "function" if isinstance(node, ast.FunctionDef) else "class",
                    "name": element_name,
                    "docstring": docstring,
                    "source_code": source_code
                }
                
                # Create a Document for each structural element
                document = Document(content=docstring, metadata=metadata)
                documents.append(document)
                
        return documents

```

```swarmauri/standard/parsers/concrete/RegExParser.py

import re
from typing import List, Union, Any, Literal, Pattern
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class RegExParser(ParserBase):
    """
    A parser that uses a regular expression to extract information from text.
    """
    pattern: Pattern = re.compile(r'\d+')
    type: Literal['RegExParser'] = 'RegExParser'
    
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses the input data using the specified regular expression pattern and
        returns a list of IDocument instances containing the extracted information.

        Parameters:
        - data (Union[str, Any]): The input data to be parsed. It can be a string or any format 
                                   that the concrete implementation can handle.

        Returns:
        - List[IDocument]: A list of IDocument instances containing the parsed information.
        """
        # Ensure data is a string
        if not isinstance(data, str):
            data = str(data)

        # Use the regular expression pattern to find all matches in the text
        matches = self.pattern.findall(data)

        # Create a Document for each match and collect them into a list
        documents = [Document(content=match, metadata={}) for i, match in enumerate(matches)]

        return documents

```

```swarmauri/standard/parsers/concrete/TextBlobNounParser.py

from textblob import TextBlob
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class TextBlobNounParser(ParserBase):
    """
    A concrete implementation of IParser using TextBlob for Natural Language Processing tasks.
    
    This parser leverages TextBlob's functionalities such as noun phrase extraction, 
    sentiment analysis, classification, language translation, and more for parsing texts.
    """
    type: Literal['TextBlobNounParser'] = 'TextBlobNounParser'
    
    def __init__(self, **kwargs):
        import nltk
        nltk.download('punkt')
        super().__init__(**kwargs)
        
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses the input data using TextBlob to perform basic NLP tasks 
        and returns a list of documents with the parsed information.
        
        Parameters:
        - data (Union[str, Any]): The input data to parse, expected to be text data for this parser.
        
        Returns:
        - List[IDocument]: A list of documents with metadata generated from the parsing process.
        """
        # Ensure the data is a string
        if not isinstance(data, str):
            raise ValueError("TextBlobParser expects a string as input data.")
        
        # Use TextBlob for NLP tasks
        blob = TextBlob(data)
        
        # Extracts noun phrases to demonstrate one of TextBlob's capabilities. 
        # In practice, this parser could be expanded to include more sophisticated processing.
        noun_phrases = list(blob.noun_phrases)
        
        # Example: Wrap the extracted noun phrases into an IDocument instance
        # In real scenarios, you might want to include more details, like sentiment, POS tags, etc.
        document = Document(content=data, metadata={"noun_phrases": noun_phrases})
        
        return [document]

```

```swarmauri/standard/parsers/concrete/TextBlobSentenceParser.py

from textblob import TextBlob
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase


class TextBlobSentenceParser(ParserBase):
    """
    A parser that leverages TextBlob to break text into sentences.

    This parser uses the natural language processing capabilities of TextBlob
    to accurately identify sentence boundaries within large blocks of text.
    """
    type: Literal['TextBlobSentenceParser'] = 'TextBlobSentenceParser'
    
    def __init__(self, **kwargs):
        import nltk
        nltk.download('punkt')
        super().__init__(**kwargs)

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses the input text into sentence-based document chunks using TextBlob.

        Args:
            data (Union[str, Any]): The input text to be parsed.

        Returns:
            List[IDocument]: A list of IDocument instances, each representing a sentence.
        """
        # Ensure the input is a string
        if not isinstance(data, str):
            data = str(data)

        # Utilize TextBlob for sentence tokenization
        blob = TextBlob(data)
        sentences = blob.sentences

        # Create a document instance for each sentence
        documents = [
            Document(content=str(sentence), metadata={'parser': 'TextBlobSentenceParser'})
            for index, sentence in enumerate(sentences)
        ]

        return documents

```

```swarmauri/standard/parsers/concrete/URLExtractorParser.py

import re
from urllib.parse import urlparse
from typing import List, Union, Any, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class URLExtractorParser(ParserBase):
    """
    A concrete implementation of IParser that extracts URLs from text.
    
    This parser scans the input text for any URLs and creates separate
    documents for each extracted URL. It utilizes regular expressions
    to identify URLs within the given text.
    """
    type: Literal['URLExtractorParser'] = 'URLExtractorParser'

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parse input data (string) and extract URLs, each URL is then represented as a document.
        
        Parameters:
        - data (Union[str, Any]): The input data to be parsed for URLs.
        
        Returns:
        - List[IDocument]: A list of documents, each representing an extracted URL.
        """
        if not isinstance(data, str):
            raise ValueError("URLExtractorParser expects input data to be of type str.")

        # Regular expression for finding URLs
        url_regex = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
        
        # Find all matches in the text
        urls = re.findall(url_regex, data)
        
        # Create a document for each extracted URL
        documents = [Document(content=url, metadata={"source": "URLExtractor"}) for i, url in enumerate(urls)]
        
        return documents

```

```swarmauri/standard/parsers/concrete/XMLParser.py

import xml.etree.ElementTree as ET
from typing import List, Union, Any, Literal

from pydantic import Field
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class XMLParser(ParserBase):
    """
    A parser that extracts information from XML data and converts it into IDocument objects.
    This parser assumes a simple use-case where each targeted XML element represents a separate document.
    """
    element_tag: str = Field(default="root")
    type: Literal['XMLParser'] = 'XMLParser'

    
    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses XML data and converts elements with the specified tag into IDocument instances.

        Parameters:
        - data (Union[str, Any]): The XML data as a string to be parsed.

        Returns:
        - List[IDocument]: A list of IDocument instances created from the XML elements.
        """
        if isinstance(data, str):
            root = ET.fromstring(data)  # Parse the XML string into an ElementTree element
        else:
            raise TypeError("Data for XMLParser must be a string containing valid XML.")

        documents = []
        for element in root.findall(self.element_tag):
            # Extracting content and metadata from each element
            content = "".join(element.itertext())  # Get text content
            metadata = {child.tag: child.text for child in element}  # Extract child elements as metadata

            # Create a Document instance for each element
            doc = Document(content=content, metadata=metadata)
            documents.append(doc)

        return documents

```

```swarmauri/standard/parsers/concrete/BERTEmbeddingParser.py

from typing import List, Union, Any, Literal
from transformers import BertTokenizer, BertModel
import torch
from pydantic import PrivateAttr
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.base.ParserBase import ParserBase

class BERTEmbeddingParser(ParserBase):
    """
    A parser that transforms input text into document embeddings using BERT.
    
    This parser tokenizes the input text, passes it through a pre-trained BERT model,
    and uses the resulting embeddings as the document content.
    """
    parser_model_name: str = 'bert-base-uncased'
    _model: Any = PrivateAttr()
    type: Literal['BERTEmbeddingParser'] = 'BERTEmbeddingParser'

    def __init__(self, **kwargs):
        """
        Initializes the BERTEmbeddingParser with a specific BERT model.
        
        Parameters:
        - model_name (str): The name of the pre-trained BERT model to use.
        """
        super().__init__(**kwargs)
        self.tokenizer = BertTokenizer.from_pretrained(self.parser_model_name)
        self._model = BertModel.from_pretrained(self.parser_model_name)
        self._model.eval()  # Set model to evaluation mode

    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Tokenizes input data and generates embeddings using a BERT model.

        Parameters:
        - data (Union[str, Any]): Input data, expected to be a single string or batch of strings.

        Returns:
        - List[IDocument]: A list containing a single IDocument instance with BERT embeddings as content.
        """
        
        # Tokenization
        inputs = self.tokenizer(data, return_tensors='pt', padding=True, truncation=True, max_length=512)

        # Generate embeddings
        with torch.no_grad():
            outputs = self._model(**inputs)

        # Use the last hidden state as document embeddings (batch_size, sequence_length, hidden_size)
        embeddings = outputs.last_hidden_state
        
        # Convert to list of numpy arrays
        embeddings = embeddings.detach().cpu().numpy()
        
        # For simplicity, let's consider the mean of embeddings across tokens to represent the document
        doc_embeddings = embeddings.mean(axis=1)
        
        # Creating document object(s)
        documents = [Document(doc_id=str(i), content=emb, metadata={"source": "BERTEmbeddingParser"}) for i, emb in enumerate(doc_embeddings)]
        
        return documents

```

```swarmauri/standard/prompts/__init__.py



```

```swarmauri/standard/prompts/base/__init__.py



```

```swarmauri/standard/prompts/base/PromptMatrixBase.py

from typing import List, Tuple, Optional, Any, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.prompts.IPromptMatrix import IPromptMatrix

class PromptMatrixBase(IPromptMatrix, ComponentBase):
    matrix: List[List[str]] = []
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value)
    type: Literal['PromptMatrixBase'] = 'PromptMatrixBase'    

    @property
    def shape(self) -> Tuple[int, int]:
        """Get the shape (number of agents, sequence length) of the prompt matrix."""
        if self.matrix:
            return len(self.matrix), len(self.matrix[0])
        return 0, 0

    def add_prompt_sequence(self, sequence: List[Optional[str]]) -> None:
        if not self.matrix or (self.matrix and len(sequence) == len(self.matrix[0])):
            self.matrix.append(sequence)
        else:
            raise ValueError("Sequence length does not match the prompt matrix dimensions.")

    def remove_prompt_sequence(self, index: int) -> None:
        if 0 <= index < len(self.matrix):
            self.matrix.pop(index)
        else:
            raise IndexError("Index out of range.")

    def get_prompt_sequence(self, index: int) -> List[Optional[str]]:
        if 0 <= index < len(self._matrix):
            return self.matrix[index]
        else:
            raise IndexError("Index out of range.")

    def show(self) -> List[List[Optional[str]]]:
        return self.matrix

```

```swarmauri/standard/prompts/base/PromptBase.py

from typing import Optional, Literal
from pydantic import ConfigDict, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.prompts.IPrompt import IPrompt

class PromptBase(IPrompt, ComponentBase):
    """
    The ChatPrompt class represents a simple, chat-like prompt system where a 
    message can be set and retrieved as needed. It's particularly useful in 
    applications involving conversational agents, chatbots, or any system that 
    requires dynamic text-based interactions.
    """
    prompt: str = ""
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal['PromptBase'] = 'PromptBase'

    def __call__(self):
        """
        Enables the instance to be callable, allowing direct retrieval of the message. 
        This method facilitates intuitive access to the prompt's message, mimicking callable 
        behavior seen in functional programming paradigms.
        
        Returns:
        - str: The current message stored in the prompt.
        """
        return self.prompt

    def set_prompt(self, prompt: str):
        """
        Updates the internal message of the chat prompt. This method provides a way to change 
        the content of the prompt dynamically, reflecting changes in the conversational context 
        or user inputs.
        
        Parameters:
        - message (str): The new message to set for the prompt.
        """
        self.prompt = prompt

```

```swarmauri/standard/prompts/base/PromptTemplateBase.py

from typing import Dict, List, Union, Optional, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.prompts.IPrompt import IPrompt
from swarmauri.core.prompts.ITemplate import ITemplate

class PromptTemplateBase(IPrompt, ITemplate, ComponentBase):
    """
    A class for generating prompts based on a template and variables.
    Implements the IPrompt for generating prompts and ITemplate for template manipulation.
    """

    template: str = ""
    variables: Union[List[Dict[str, str]], Dict[str,str]] = {}
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal['PromptTemplateBase'] = 'PromptTemplateBase'

    def set_template(self, template: str) -> None:
        """
        Sets or updates the current template string.
        """
        self.template = template

    def set_variables(self, variables: Dict[str, str]) -> None:
        """
        Sets or updates the variables to be substituted into the template.
        """
        self.variables = variables

    def generate_prompt(self, variables: Dict[str, str] = None) -> str:
        variables = variables or self.variables
        return self.template.format(**variables)

    def __call__(self, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Generates a prompt using the current template and provided keyword arguments for substitution.
        """
        variables = variables if variables else self.variables
        return self.generate_prompt(variables)

```

```swarmauri/standard/prompts/base/PromptGeneratorBase.py

from typing import Dict, List, Generator, Any, Union, Optional, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.prompts.IPrompt import IPrompt
from swarmauri.core.prompts.ITemplate import ITemplate


class PromptGeneratorBase(IPrompt, ITemplate, ComponentBase):
    """
    A class that generates prompts based on a template and a list of variable sets.
    It implements the IPrompt and ITemplate interfaces.
    """

    template: str = ""
    variables: Union[List[Dict[str, Any]], Dict[str, Any]] = {}
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal['PromptGeneratorBase'] = 'PromptGeneratorBase'

    def set_template(self, template: str) -> None:
        self.template = template

    def set_variables(self, variables: List[Dict[str, Any]]) -> None:
        self.variables = variables

    def generate_prompt(self, variables: Dict[str, Any]) -> str:
        """
        Generates a prompt using the provided variables if any
        else uses the next variables set in the list.
        """
        variables = variables if variables else self.variables.pop(0) if self.variables else {}
        return self.template.format(**variables)

    def __call__(self) -> Generator[str, None, None]:
        """
        Returns a generator that yields prompts constructed from the template and 
        each set of variables in the variables list.
        """
        for variables_set in self.variables:
            yield self.generate_prompt(variables_set)
        self.variables = []

```

```swarmauri/standard/prompts/concrete/__init__.py



```

```swarmauri/standard/prompts/concrete/Prompt.py

from typing import Literal
from swarmauri.standard.prompts.base.PromptBase import PromptBase

class Prompt(PromptBase):
    type: Literal['Prompt'] = 'Prompt'

```

```swarmauri/standard/prompts/concrete/PromptTemplate.py

from typing import Literal
from swarmauri.standard.prompts.base.PromptTemplateBase import PromptTemplateBase

class PromptTemplate(PromptTemplateBase):
    type: Literal['PromptTemplate'] = 'PromptTemplate'

```

```swarmauri/standard/prompts/concrete/PromptGenerator.py

from typing import Literal
from swarmauri.standard.prompts.base.PromptGeneratorBase import PromptGeneratorBase

class PromptGenerator(PromptGeneratorBase):
    type: Literal['PromptGenerator'] = 'PromptGenerator'

```

```swarmauri/standard/prompts/concrete/PromptMatrix.py

from typing import Literal
from swarmauri.standard.prompts.base.PromptMatrixBase import PromptMatrixBase

class PromptMatrix(PromptMatrixBase):
    type: Literal['PromptMatrix'] = 'PromptMatrix'

```

```swarmauri/standard/swarms/__init__.py



```

```swarmauri/standard/swarms/base/__init__.py



```

```swarmauri/standard/swarms/base/SwarmComponentBase.py

from swarmauri.core.swarms.ISwarmComponent import ISwarmComponent

class SwarmComponentBase(ISwarmComponent):
    """
    Interface for defining basics of any component within the swarm system.
    """
    def __init__(self, key: str, name: str, superclass: str, module: str, class_name: str, args=None, kwargs=None):
        self.key = key
        self.name = name
        self.superclass = superclass
        self.module = module
        self.class_name = class_name
        self.args = args or []
        self.kwargs = kwargs or {}
    

```

```swarmauri/standard/swarms/concrete/__init__.py



```

```swarmauri/standard/swarms/concrete/SimpleSwarmFactory.py

import json
import pickle
from typing import List
from swarmauri.core.chains.ISwarmFactory import (
    ISwarmFactory , 
    CallableChainItem, 
    AgentDefinition, 
    FunctionDefinition
)
class SimpleSwarmFactory(ISwarmFactory):
    def __init__(self):
        self.swarms = []
        self.callable_chains = []

    def create_swarm(self, agents=[]):
        swarm = {"agents": agents}
        self.swarms.append(swarm)
        return swarm

    def create_agent(self, agent_definition: AgentDefinition):
        # For simplicity, agents are stored in a list
        # Real-world usage might involve more sophisticated management and instantiation based on type and configuration
        agent = {"definition": agent_definition._asdict()}
        self.agents.append(agent)
        return agent

    def create_callable_chain(self, chain_definition: List[CallableChainItem]):
        chain = {"definition": [item._asdict() for item in chain_definition]}
        self.callable_chains.append(chain)
        return chain

    def register_function(self, function_definition: FunctionDefinition):
        if function_definition.identifier in self.functions:
            raise ValueError(f"Function {function_definition.identifier} is already registered.")
        
        self.functions[function_definition.identifier] = function_definition
    
    def export_configuration(self, format_type: str = 'json'):
        # Now exporting both swarms and callable chains
        config = {"swarms": self.swarms, "callable_chains": self.callable_chains}
        if format_type == "json":
            return json.dumps(config)
        elif format_type == "pickle":
            return pickle.dumps(config)

    def load_configuration(self, config_data, format_type: str = 'json'):
        # Loading both swarms and callable chains
        config = json.loads(config_data) if format_type == "json" else pickle.loads(config_data)
        self.swarms = config.get("swarms", [])
        self.callable_chains = config.get("callable_chains", [])

```

```swarmauri/standard/toolkits/__init__.py



```

```swarmauri/standard/toolkits/base/__init__.py



```

```swarmauri/standard/toolkits/base/ToolkitBase.py

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.toolkits.IToolkit import IToolkit



class ToolkitBase(IToolkit, ComponentBase):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    tools: Dict[str, SubclassUnion[ToolBase]] = {}
    resource: Optional[str] =  Field(default=ResourceTypes.TOOLKIT.value, frozen=True)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ToolkitBase'] = 'ToolkitBase'

    def get_tools(self, 
                   include: Optional[List[str]] = None, 
                   exclude: Optional[List[str]] = None,
                   by_alias: bool = False, 
                   exclude_unset: bool = False,
                   exclude_defaults: bool = False, 
                   exclude_none: bool = False
                   ) -> Dict[str, SubclassUnion[ToolBase]]:
            """
            List all tools in the toolkit with options to include or exclude specific fields.
    
            Parameters:
                include (List[str], optional): Fields to include in the returned dictionary.
                exclude (List[str], optional): Fields to exclude from the returned dictionary.
    
            Returns:
                Dict[str, SubclassUnion[ToolBase]]: A dictionary of tools with specified fields included or excluded.
            """
            return [tool.model_dump(include=include, exclude=exclude, by_alias=by_alias,
                                   exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, 
                                    exclude_none=exclude_none) for name, tool in self.tools.items()]

    def add_tools(self, tools: Dict[str, SubclassUnion[ToolBase]]) -> None:
        """
        Add multiple tools to the toolkit.

        Parameters:
            tools (Dict[str, Tool]): A dictionary of tool objects keyed by their names.
        """
        self.tools.update(tools)

    def add_tool(self, tool: SubclassUnion[ToolBase])  -> None:
        """
        Add a single tool to the toolkit.

        Parameters:
            tool (Tool): The tool instance to be added to the toolkit.
        """
        self.tools[tool.name] = tool

    def remove_tool(self, tool_name: str) -> None:
        """
        Remove a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to be removed from the toolkit.
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def get_tool_by_name(self, tool_name: str) -> SubclassUnion[ToolBase]:
        """
        Get a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to retrieve.

        Returns:
            Tool: The tool instance with the specified name.
        """
        if tool_name in self.tools:
            return self.tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def __len__(self) -> int:
        """
        Returns the number of tools in the toolkit.

        Returns:
            int: The number of tools in the toolkit.
        """
        return len(self.tools)

```

```swarmauri/standard/toolkits/concrete/__init__.py



```

```swarmauri/standard/toolkits/concrete/Toolkit.py

from typing import Literal
from swarmauri.standard.toolkits.base.ToolkitBase import ToolkitBase

class Toolkit(ToolkitBase):
    type: Literal['Toolkit'] = 'Toolkit'

```

```swarmauri/standard/tools/__init__.py



```

```swarmauri/standard/tools/base/__init__.py



```

```swarmauri/standard/tools/base/ToolBase.py

from abc import ABC, abstractmethod
from typing import Optional, List, Any, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.standard.tools.concrete.Parameter import Parameter
from swarmauri.core.tools.ITool import ITool


class ToolBase(ITool, ComponentBase, ABC):
    name: str
    description: Optional[str] = None
    parameters: List[Parameter] = Field(default_factory=list)
    resource: Optional[str] =  Field(default=ResourceTypes.TOOL.value)
    type: Literal['ToolBase'] = 'ToolBase'
    
    def call(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)
    
    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the __call__ method.")


   # #def __getstate__(self):
        # return {'type': self.type, 'function': self.function}


    #def __iter__(self):
    #    yield ('type', self.type)
    #    yield ('function', self.function)

    # @property
    # def function(self):
    #     # Dynamically constructing the parameters schema
    #     properties = {}
    #     required = []

    #     for param in self.parameters:
    #         properties[param.name] = {
    #             "type": param.type,
    #             "description": param.description,
    #         }
    #         if param.enum:
    #             properties[param.name]['enum'] = param.enum

    #         if param.required:
    #             required.append(param.name)

    #     function = {
    #         "name": self.name,
    #         "description": self.description,
    #         "parameters": {
    #             "type": "object",
    #             "properties": properties,
    #         }
    #     }
        
    #     if required:  # Only include 'required' if there are any required parameters
    #         function['parameters']['required'] = required
    #     return function

   # def as_dict(self):
    #    #return asdict(self)
   #     return {'type': self.type, 'function': self.function}

```

```swarmauri/standard/tools/base/ParameterBase.py

from typing import Optional, List, Any
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.tools.IParameter import IParameter


class ParameterBase(IParameter, ComponentBase):
    name: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    resource: Optional[str] =  Field(default=ResourceTypes.PARAMETER.value)
    type: str # THIS DOES NOT USE LITERAL


```

```swarmauri/standard/tools/concrete/__init__.py



```

```swarmauri/standard/tools/concrete/TestTool.py

from typing import List, Literal
from pydantic import Field
import subprocess as sp
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 

class TestTool(ToolBase):
    version: str = "1.0.0"
        
    # Define the parameters required by the tool
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="program",
            type="string",
            description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
            required=True,
            enum=["notepad", "calc", "mspaint"]
        )
    ])
    name: str = 'TestTool'
    description: str = "This opens a program based on the user's request."
    type: Literal['TestTool'] = 'TestTool'

    def __call__(self, program) -> str:
        # sp.check_output(program)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Program Opened: {program}"


```

```swarmauri/standard/tools/concrete/Parameter.py

from swarmauri.standard.tools.base.ParameterBase import ParameterBase

class Parameter(ParameterBase):
    pass

```

```swarmauri/standard/tools/concrete/CodeInterpreterTool.py

import sys
import io
from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 


class CodeInterpreterTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(default_factory=lambda: [
            Parameter(
                name="user_code",
                type="string",
                description=("Executes the provided Python code snippet in a secure sandbox environment. "
                             "This tool is designed to interpret the execution of the python code snippet."
                             "Returns the output"),
                required=True
            )
        ])
    name: str = 'CodeInterpreterTool'
    description: str = "Executes provided Python code and captures its output."
    type: Literal['CodeInterpreterTool'] = 'CodeInterpreterTool'

    def __call__(self, user_code: str) -> str:
        """
        Executes the provided user code and captures its stdout output.
        
        Parameters:
            user_code (str): Python code to be executed.
        
        Returns:
            str: Captured output or error message from the executed code.
        """
        return self.execute_code(user_code)
    
    def execute_code(self, user_code: str) -> str:
        """
        Executes the provided user code and captures its stdout output.

        Args:
            user_code (str): Python code to be executed.

        Returns:
            str: Captured output or error message from the executed code.
        """
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        try:
            # Note: Consider security implications of using 'exec'
            builtins = globals().copy()
            exec(user_code, builtins)
            sys.stdout = old_stdout
            captured_output = redirected_output.getvalue()
            return str(captured_output)
        except Exception as e:
            sys.stdout = old_stdout
            return f"An error occurred: {str(e)}"

```

```swarmauri/standard/tools/concrete/CalculatorTool.py

from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter

class CalculatorTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="operation",
            type="string",
            description="The arithmetic operation to perform ('add', 'subtract', 'multiply', 'divide').",
            required=True,
            enum=["add", "subtract", "multiply", "divide"]
        ),
        Parameter(
            name="x",
            type="number",
            description="The left operand for the operation.",
            required=True
        ),
        Parameter(
            name="y",
            type="number",
            description="The right operand for the operation.",
            required=True
        )
    ])
    name: str = 'CalculatorTool'
    description: str = "Performs basic arithmetic operations."
    type: Literal['CalculatorTool'] = 'CalculatorTool'

    def __call__(self, operation: str, x: float, y: float) -> str:
        try:
            if operation == "add":
                result = x + y
            elif operation == "subtract":
                result = x - y
            elif operation == "multiply":
                result = x * y
            elif operation == "divide":
                if y == 0:
                    return "Error: Division by zero."
                result = x / y
            else:
                return "Error: Unknown operation."
            return str(result)
        except Exception as e:
            return f"An error occurred: {str(e)}"


```

```swarmauri/standard/tools/concrete/ImportMemoryModuleTool.py

import sys
import types
import importlib
from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 

class ImportMemoryModuleTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(default_factory=lambda: [
            Parameter(
                name="name",
                type="string",
                description="Name of the new module.",
                required=True
            ),
            Parameter(
                name="code",
                type="string",
                description="Python code snippet to include in the module.",
                required=True
            ),
            Parameter(
                name="package_path",
                type="string",
                description="Dot-separated package path where the new module should be inserted.",
                required=True
            )
        ])
    
    name: str = 'ImportMemoryModuleTool'
    description: str = "Dynamically imports a module from memory into a specified package path."
    type: Literal['ImportMemoryModuleTool'] = 'ImportMemoryModuleTool'

    def __call__(self, name: str, code: str, package_path: str) -> str:
        """
        Dynamically creates a module from a code snippet and inserts it into the specified package path.

        Args:
            name (str): Name of the new module.
            code (str): Python code snippet to include in the module.
            package_path (str): Dot-separated package path where the new module should be inserted.
        """
        # Implementation adapted from the provided snippet
        # Ensure the package structure exists
        current_package = self.ensure_module(package_path)
        
        # Create a new module
        module = types.ModuleType(name)
        
        # Execute code in the context of this new module
        exec(code, module.__dict__)
        
        # Insert the new module into the desired location
        setattr(current_package, name, module)
        sys.modules[package_path + '.' + name] = module
        return f"{name} has been successfully imported into {package_path}"

    @staticmethod
    def ensure_module(package_path: str):
        package_parts = package_path.split('.')
        module_path = ""
        current_module = None

        for part in package_parts:
            if module_path:
                module_path += "." + part
            else:
                module_path = part
                
            if module_path not in sys.modules:
                try:
                    # Try importing the module; if it exists, this will add it to sys.modules
                    imported_module = importlib.import_module(module_path)
                    sys.modules[module_path] = imported_module
                except ImportError:
                    # If the module doesn't exist, create a new placeholder module
                    new_module = types.ModuleType(part)
                    if current_module:
                        setattr(current_module, part, new_module)
                    sys.modules[module_path] = new_module
            current_module = sys.modules[module_path]

        return current_module

```

```swarmauri/standard/tools/concrete/AdditionTool.py

from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter

class AdditionTool(ToolBase):
    version: str = "0.0.1"
    parameters: List[Parameter] = Field(default_factory=lambda: [
            Parameter(
                name="x",
                type="integer",
                description="The left operand",
                required=True
            ),
            Parameter(
                name="y",
                type="integer",
                description="The right operand",
                required=True
            )
        ])

    name: str = 'AdditionTool'
    description: str = "This tool has two numbers together"
    type: Literal['AdditionTool'] = 'AdditionTool'


    def __call__(self, x: int, y: int) -> int:
        """
        Add two numbers x and y and return the sum.

        Parameters:
        - x (int): The first number.
        - y (int): The second number.

        Returns:
        - str: The sum of x and y.
        """
        return str(x + y)

```

```swarmauri/standard/tools/concrete/WeatherTool.py

from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 

class WeatherTool(ToolBase):
    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="location",
            type="string",
            description="The location for which to fetch weather information",
            required=True
        ),
        Parameter(
            name="unit",
            type="string",
            description="The unit for temperature ('fahrenheit' or 'celsius')",
            required=True,
            enum=["fahrenheit", "celsius"]
        )
    ])
    name: str = 'WeatherTool'
    description: str = "Fetch current weather info for a location"
    type: Literal['WeatherTool'] = 'WeatherTool'

    def __call__(self, location, unit="fahrenheit") -> str:
        weather_info = (location, unit)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Weather Info: {weather_info}\n"


```

```swarmauri/standard/apis/__init__.py



```

```swarmauri/standard/apis/base/__init__.py



```

```swarmauri/standard/apis/base/README.md



```

```swarmauri/standard/apis/concrete/__init__.py



```

```swarmauri/standard/vector_stores/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vector_stores/base/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vector_stores/base/VectorStoreBase.py

import json
from abc import ABC, abstractmethod
from typing import List, Optional, Literal
from pydantic import Field, PrivateAttr
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.core.vector_stores.IVectorStore import IVectorStore

class VectorStoreBase(IVectorStore, ComponentBase):
    """
    Abstract base class for document stores, implementing the IVectorStore interface.

    This class provides a standard API for adding, updating, getting, and deleting documents in a vector store.
    The specifics of storing (e.g., in a database, in-memory, or file system) are to be implemented by concrete subclasses.
    """
    documents: List[Document] = []
    _embedder = PrivateAttr()
    _distance = PrivateAttr()
    resource: Optional[str] =  Field(default=ResourceTypes.VECTOR_STORE.value)
    type: Literal['VectorStoreBase'] = 'VectorStoreBase'
    
    @property
    def embedder(self):
        return self._embedder

    @abstractmethod
    def add_document(self, document: Document) -> None:
        """
        Add a single document to the document store.

        Parameters:
        - document (IDocument): The document to be added to the store.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add multiple documents to the document store in a batch operation.

        Parameters:
        - documents (List[IDocument]): A list of documents to be added to the store.
        """
        pass

    @abstractmethod
    def get_document(self, id: str) -> Optional[Document]:
        """
        Retrieve a single document by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to retrieve.

        Returns:
        - Optional[IDocument]: The requested document if found; otherwise, None.
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[Document]:
        """
        Retrieve all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents in the store.
        """
        pass

    @abstractmethod
    def update_document(self, id: str, updated_document: Document) -> None:
        """
        Update a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier of the document to update.
        - updated_document (IDocument): The updated document instance.
        """
        pass

    @abstractmethod
    def delete_document(self, id: str) -> None:
        """
        Delete a document from the document store by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """
        pass

    def clear_documents(self) -> None:
        """
        Deletes all documents from the vector store

        """
        self.documents = []
    
    def document_count(self):
        return len(self.documents)
    
    def document_dumps(self) -> str:
        """
        Placeholder
        """
        return json.dumps([each.to_dict() for each in self.documents])

    def document_dump(self, file_path: str) -> None:
        """
        Placeholder
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([each.to_dict() for each in self.documents], 
                f,
                ensure_ascii=False, 
                indent=4)  

    def document_loads(self, json_data: str) -> None:
        """
        Placeholder
        """
        self.documents = [globals()[each['type']].from_dict(each) for each in json.loads(json_data)]

    def document_load(self, file_path: str) -> None:
        """
        Placeholder
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self.documents = [globals()[each['type']].from_dict(each) for each in json.load(file_path)]

```

```swarmauri/standard/vector_stores/base/VectorStoreSaveLoadMixin.py

from typing import List
import os
from pydantic import BaseModel
import json
import glob
import importlib 
from swarmauri.core.vector_stores.IVectorStoreSaveLoad import IVectorStoreSaveLoad
from swarmauri.standard.documents.concrete.Document import Document

class VectorStoreSaveLoadMixin(IVectorStoreSaveLoad, BaseModel):
    """
    Base class for vector stores with built-in support for saving and loading
    the vectorizer's model and the documents.
    """
    
    
    def save_store(self, directory_path: str) -> None:
        """
        Saves both the vectorizer's model and the documents.
        """
        # Ensure the directory exists
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            
        # Save the vectorizer model
        model_path = os.path.join(directory_path, "embedding_model")
        self._vectorizer.save_model(model_path)
        
        # Save documents
        documents_path = os.path.join(directory_path, "documents.json")
        with open(documents_path, 'w', encoding='utf-8') as f:
            json.dump([each.to_dict() for each in self.documents], 
                f,
                ensure_ascii=False, 
                indent=4)

    
    def load_store(self, directory_path: str) -> None:
        """
        Loads both the vectorizer's model and the documents.
        """
        # Load the vectorizer model
        model_path = os.path.join(directory_path, "embedding_model")
        self.vectorizer.load_model(model_path)
        
        # Load documents
        documents_path = os.path.join(directory_path, "documents.json")
        with open(documents_path, 'r', encoding='utf-8') as f:
            self.documents = [self._load_document(each) for each in json.load(f)]

    def _load_document(self, data):
        document_type = data.pop("type") 
        if document_type:
            module = importlib.import_module(f"swarmauri.standard.documents.concrete.{document_type}")
            document_class = getattr(module, document_type)
            document = document_class.from_dict(data)
            return document
        else:
            raise ValueError("Unknown document type")

    def save_parts(self, directory_path: str, chunk_size: int = 10485760) -> None:
        """
        Splits the file into parts if it's too large and saves those parts individually.
        """
        file_number = 1
        model_path = os.path.join(directory_path, "embedding_model")
        parts_directory = os.path.join(directory_path, "parts")
        
        if not os.path.exists(parts_directory):
            os.makedirs(parts_directory)



        with open(f"{model_path}/model.safetensors", 'rb') as f:
            chunk = f.read(chunk_size)
            while chunk:
                with open(f"{parts_directory}/model.safetensors.part{file_number:03}", 'wb') as chunk_file:
                    chunk_file.write(chunk)
                file_number += 1
                chunk = f.read(chunk_size)

        # Split the documents into parts and save them
        documents_dir = os.path.join(directory_path, "documents")

        self._split_json_file(directory_path, chunk_size=chunk_size)


    def _split_json_file(self, directory_path: str, max_records=100, chunk_size: int = 10485760):    
        # Read the input JSON file
        combined_documents_file_path = os.path.join(directory_path, "documents.json")

        # load the master JSON file
        with open(combined_documents_file_path , 'r') as file:
            data = json.load(file)

        # Set and Create documents parts folder if it does not exist
        documents_dir = os.path.join(directory_path, "documents")
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)
        current_batch = []
        file_index = 1
        current_size = 0
        
        for record in data:
            current_batch.append(record)
            current_size = len(json.dumps(current_batch).encode('utf-8'))
            
            # Check if current batch meets the splitting criteria
            if len(current_batch) >= max_records or current_size >= chunk_size:
                # Write current batch to a new file
                output_file = f'document_part_{file_index}.json'
                output_file = os.path.join(documents_dir, output_file)
                with open(output_file, 'w') as outfile:
                    json.dump(current_batch, outfile)
                
                # Prepare for the next batch
                current_batch = []
                current_size = 0
                file_index += 1

        # Check if there's any remaining data to be written
        if current_batch:
            output_file = f'document_part_{file_index}.json'
            output_file = os.path.join(documents_dir, output_file)
            with open(output_file, 'w') as outfile:
                json.dump(current_batch, outfile)

    def load_parts(self, directory_path: str, file_pattern: str = '*.part*') -> None:
        """
        Combines file parts from a directory back into a single file and loads it.
        """
        model_path = os.path.join(directory_path, "embedding_model")
        parts_directory = os.path.join(directory_path, "parts")
        output_file_path = os.path.join(model_path, "model.safetensors")

        parts = sorted(glob.glob(os.path.join(parts_directory, file_pattern)))
        with open(output_file_path, 'wb') as output_file:
            for part in parts:
                with open(part, 'rb') as file_part:
                    output_file.write(file_part.read())

        # Load the combined_model now        
        model_path = os.path.join(directory_path, "embedding_model")
        self._vectorizer.load_model(model_path)

        # Load document files
        self._load_documents(directory_path)
        

    def _load_documents(self, directory_path: str) -> None:
        """
        Loads the documents from parts stored in the given directory.
        """
        part_paths = glob.glob(os.path.join(directory_path, "documents/*.json"))
        for part_path in part_paths:
            with open(part_path, "r") as f:
                part_documents = json.load(f)
                for document_data in part_documents:
                    document_type = document_data.pop("type")
                    document_module = importlib.import_module(f"swarmauri.standard.documents.concrete.{document_type}")
                    document_class = getattr(document_module, document_type)
                    document = document_class.from_dict(document_data)
                    self.documents.append(document)

```

```swarmauri/standard/vector_stores/base/VectorStoreRetrieveMixin.py

from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.core.vector_stores.IVectorStoreRetrieve import IVectorStoreRetrieve


class VectorStoreRetrieveMixin(IVectorStoreRetrieve, BaseModel):
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        
        Args:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        pass

```

```swarmauri/standard/vector_stores/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vector_stores/concrete/TfidfVectorStore.py

from typing import List, Union, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.embeddings.concrete.TfidfEmbedding import TfidfEmbedding
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.standard.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.standard.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    

class TfidfVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal['TfidfVectorStore'] = 'TfidfVectorStore'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = TfidfEmbedding()
        self._distance = CosineDistance()
        self.documents = []
      

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None

    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != id]
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def update_document(self, id: str, updated_document: Document) -> None:
        for i, document in enumerate(self.documents):
            if document.id == id:
                self.documents[i] = updated_document
                break

        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        documents = [query]
        documents.extend([doc.content for doc in self.documents])
        transform_matrix = self._embedder.fit_transform(documents)
        
        # The inferred vector is the last vector in the transformed_matrix
        # The rest of the matrix is what we are comparing
        distances = self._distance.distances(transform_matrix[-1], transform_matrix[:-1])  

        # Get the indices of the top_k most similar (least distant) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]



```

```swarmauri/standard/vector_stores/concrete/Doc2VecVectorStore.py

from typing import List, Union, Literal
from pydantic import PrivateAttr

from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.embeddings.concrete.TfidfEmbedding import TfidfEmbedding
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.standard.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.standard.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    


class Doc2VecVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal['Doc2VecVectorStore'] = 'Doc2VecVectorStore'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = TfidfEmbedding()
        self._distance = CosineDistance()
      

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None

    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != id]
        # Recalculate TF-IDF matrix for the current set of documents
        self._embedder.fit([doc.content for doc in self.documents])

    def update_document(self, id: str, updated_document: Document) -> None:
        for i, document in enumerate(self.documents):
            if document.id == id:
                self.documents[i] = updated_document
                break

        # Recalculate TF-IDF matrix for the current set of documents
        self._embedding.fit([doc.content for doc in self.documents])

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        documents = [query]
        documents.extend([doc.content for doc in self.documents])
        transform_matrix = self._embedder.fit_transform(documents)

        # The inferred vector is the last vector in the transformed_matrix
        # The rest of the matrix is what we are comparing
        distances = self._distance.distances(transform_matrix[-1], transform_matrix[:-1])  

        # Get the indices of the top_k most similar (least distant) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]


```

```swarmauri/standard/vector_stores/concrete/MlmVectorStore.py

from typing import List, Union, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.embeddings.concrete.MlmEmbedding import MlmEmbedding
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.standard.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.standard.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    

class MlmVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal['MlmVectorStore'] = 'MlmVectorStore'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = MlmEmbedding()
        self._distance = CosineDistance()
        self.documents: List[Document] = []   

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self._embedder.fit_transform(documents_text)

        embedded_documents = [Document(id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count])

        for _count, _d in enumerate(self.documents) if _d.content]

        self.documents = embedded_documents

    def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self._embedder.fit_transform(documents_text)

        embedded_documents = [Document(id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count]) for _count, _d in enumerate(self.documents) 
            if _d.content]

        self.documents = embedded_documents

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None
        
    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [_d for _d in self.documents if _d.id != id]

    def update_document(self, id: str) -> None:
        raise NotImplementedError('Update_document not implemented on MLMVectorStore class.')
        
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        query_vector = self._embedder.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]
        distances = self._distance.distances(query_vector, document_vectors)
        
        # Get the indices of the top_k most similar documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]

```

```swarmauri/standard/vector_stores/concrete/SpatialDocVectorStore.py

from typing import List, Union, Literal
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.embeddings.concrete.SpatialDocEmbedding import SpatialDocEmbedding
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.standard.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.standard.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    


class SpatialDocVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal['SpatialDocVectorStore'] = 'SpatialDocVectorStore'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = SpatialDocEmbedding()  # Assuming this is already implemented
        self._distance = CosineDistance()
        self.documents: List[Document] = []

    def add_document(self, document: Document) -> None:
        self.add_documents([document])  # Reuse the add_documents logic for batch processing

    def add_documents(self, documents: List[Document]) -> None:
        chunks = [doc.content for doc in documents]
        # Prepare a list of metadata dictionaries for each document based on the required special tokens
        metadata_list = [{ 
            'dir': doc.metadata.get('dir', ''),
            'type': doc.metadata.get('type', ''),
            'section': doc.metadata.get('section', ''),
            'path': doc.metadata.get('path', ''),
            'paragraph': doc.metadata.get('paragraph', ''),
            'subparagraph': doc.metadata.get('subparagraph', ''),
            'chapter': doc.metadata.get('chapter', ''), 
            'title': doc.metadata.get('title', ''),
            'subsection': doc.metadata.get('subsection', ''),
        } for doc in documents]

        # Use vectorize_document to process all documents with their corresponding metadata
        embeddings = self._embedder.vectorize_document(chunks, metadata_list=metadata_list)
        
        # Create Document instances for each document with the generated embeddings
        for doc, embedding in zip(documents, embeddings):
            embedded_doc = Document(
                id=doc.id, 
                content=doc.content, 
                metadata=doc.metadata, 
                embedding=embedding
            )
            self.documents.append(embedded_doc)

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None
        
    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [_d for _d in self.documents if _d.id != id]

    def update_document(self, id: str) -> None:
        raise NotImplementedError('Update_document not implemented on SpatialDocVectorStore class.')
        
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        query_vector = self._embedder.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]
        distances = self._distance.distances(query_vector, document_vectors)
        
        # Get the indices of the top_k most similar documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]



```

```swarmauri/standard/document_stores/__init__.py



```

```swarmauri/standard/document_stores/base/__init__.py



```

```swarmauri/standard/document_stores/base/DocumentStoreBase.py

import json
from abc import ABC, abstractmethod
from typing import List, Optional
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore

class DocumentStoreBase(IDocumentStore, ABC):
    """
    Abstract base class for document stores, implementing the IDocumentStore interface.

    This class provides a standard API for adding, updating, getting, and deleting documents in a store.
    The specifics of storing (e.g., in a database, in-memory, or file system) are to be implemented by concrete subclasses.
    """

    @abstractmethod
    def add_document(self, document: IDocument) -> None:
        """
        Add a single document to the document store.

        Parameters:
        - document (IDocument): The document to be added to the store.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Add multiple documents to the document store in a batch operation.

        Parameters:
        - documents (List[IDocument]): A list of documents to be added to the store.
        """
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[IDocument]:
        """
        Retrieve a single document by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to retrieve.

        Returns:
        - Optional[IDocument]: The requested document if found; otherwise, None.
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieve all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents in the store.
        """
        pass

    @abstractmethod
    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        """
        Update a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier of the document to update.
        - updated_document (IDocument): The updated document instance.
        """
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the document store by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """
        pass
    
    def document_count(self):
        return len(self.documents)
    
    def dump(self, file_path):
        with open(file_path, 'w') as f:
            json.dumps([each.__dict__ for each in self.documents], f, indent=4)
            
    def load(self, file_path):
        with open(file_path, 'r') as f:
            self.documents = json.loads(f)

```

```swarmauri/standard/document_stores/base/DocumentStoreRetrieveBase.py

from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.document_stores.IDocumentRetrieve import IDocumentRetrieve
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.document_stores.base.DocumentStoreBase import DocumentStoreBase

class DocumentStoreRetrieveBase(DocumentStoreBase, IDocumentRetrieve, ABC):

        
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        
        Args:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        pass

```

```swarmauri/standard/document_stores/concrete/__init__.py



```

```swarmauri/standard/chunkers/__init__.py



```

```swarmauri/standard/chunkers/base/__init__.py



```

```swarmauri/standard/chunkers/base/ChunkerBase.py

from abc import ABC, abstractmethod
from typing import Optional, Union, List, Any, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes

class ChunkerBase(ComponentBase, ABC):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing classes
    should provide concrete implementations for these methods tailored to their specific
    chunking algorithms.
    """
    resource: Optional[str] =  Field(default=ResourceTypes.CHUNKER.value)
    type: Literal['ChunkerBase'] = 'ChunkerBase'
    
    @abstractmethod
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[Any]:
        pass

```

```swarmauri/standard/chunkers/concrete/__init__.py



```

```swarmauri/standard/chunkers/concrete/SlidingWindowChunker.py

from typing import List, Literal
from swarmauri.standard.chunkers.base.ChunkerBase import ChunkerBase


class SlidingWindowChunker(ChunkerBase):
    """
    A concrete implementation of ChunkerBase that uses sliding window technique
    to break the text into chunks.
    """
    window_size: int = 256
    step_size: int = 256
    overlap: bool = False
    type: Literal['SlidingWindowChunker'] = 'SlidingWindowChunker'
         
    def chunk_text(self, text: str, *args, **kwargs) -> List[str]:
        """
        Splits the input text into chunks based on the sliding window technique.
        
        Parameters:
        - text (str): The input text to be chunked.
        
        Returns:
        - List[str]: A list of text chunks.
        """
        step_size = self.step_size if self.overlap else self.window_size  # Non-overlapping if window size equals step size.


        words = text.split()  # Tokenization by whitespaces. More sophisticated tokenization might be necessary.
        chunks = []
        
        for i in range(0, len(words) - self.window_size + 1, step_size):
            chunk = ' '.join(words[i:i+self.window_size])
            chunks.append(chunk)
        
        return chunks

```

```swarmauri/standard/chunkers/concrete/DelimiterBasedChunker.py

from typing import List, Union, Any, Literal
import re
from swarmauri.standard.chunkers.base.ChunkerBase import ChunkerBase

class DelimiterBasedChunker(ChunkerBase):
    """
    A concrete implementation of IChunker that splits text into chunks based on specified delimiters.
    """
    delimiters: List[str] = ['.', '!', '?']
    type: Literal['DelimiterBasedChunker'] = 'DelimiterBasedChunker'
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[str]:
        """
        Chunks the given text based on the delimiters specified during initialization.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked.

        Returns:
        - List[str]: A list of text chunks split based on the specified delimiters.
        """
        delimiter_pattern = f"({'|'.join(map(re.escape, self.delimiters))})"
        
        # Split the text based on the delimiter pattern, including the delimiters in the result
        chunks = re.split(delimiter_pattern, text)
        
        # Combine delimiters with the preceding text chunk since re.split() separates them
        combined_chunks = []
        for i in range(0, len(chunks), 2):  # Step by 2 to process text chunk with its following delimiter
            combined_chunks.append(chunks[i] + (chunks[i + 1] if i + 1 < len(chunks) else ''))

        # Remove whitespace
        combined_chunks = [chunk.strip() for chunk in combined_chunks]
        return combined_chunks

```

```swarmauri/standard/chunkers/concrete/FixedLengthChunker.py

from typing import List, Union, Any, Literal
from swarmauri.standard.chunkers.base.ChunkerBase import ChunkerBase

class FixedLengthChunker(ChunkerBase):
    """
    Concrete implementation of ChunkerBase that divides text into fixed-length chunks.
    
    This chunker breaks the input text into chunks of a specified size, making sure 
    that each chunk has exactly the number of characters specified by the chunk size, 
    except for possibly the last chunk.
    """
    chunk_size: int = 256
    type: Literal['FixedLengthChunker'] = 'FixedLengthChunker'
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[str]:
        """
        Splits the input text into fixed-length chunks.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked.
        
        Returns:
        - List[str]: A list of text chunks, each of a specified fixed length.
        """
        # Check if the input is a string, if not, attempt to convert to a string.
        if not isinstance(text, str):
            text = str(text)
        
        # Using list comprehension to split text into chunks of fixed size
        chunks = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        
        return chunks

```

```swarmauri/standard/chunkers/concrete/SentenceChunker.py

from typing import Literal
import re
from swarmauri.standard.chunkers.base.ChunkerBase import ChunkerBase

class SentenceChunker(ChunkerBase):
    """
    A simple implementation of the ChunkerBase to chunk text into sentences.
    
    This class uses basic punctuation marks (., !, and ?) as indicators for sentence boundaries.
    """
    type: Literal['SentenceChunker'] = 'SentenceChunker'
    
    def chunk_text(self, text, *args, **kwargs):
        """
        Chunks the given text into sentences using basic punctuation.

        Args:
            text (str): The input text to be chunked into sentences.
        
        Returns:
            List[str]: A list of sentence chunks.
        """
        # Split text using a simple regex pattern that looks for periods, exclamation marks, or question marks.
        # Note: This is a very simple approach and might not work well with abbreviations or other edge cases.
        sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s'
        sentences = re.split(sentence_pattern, text)
        
        # Filter out any empty strings that may have resulted from the split operation
        sentences = [sentence.strip() for sentence in sentences if sentence]
        
        return sentences

```

```swarmauri/standard/chunkers/concrete/MdSnippetChunker.py

from typing import List, Union, Any, Optional, Literal
import re
from swarmauri.standard.chunkers.base.ChunkerBase import ChunkerBase

class MdSnippetChunker(ChunkerBase):
    language: Optional[str] = None
    type: Literal['MdSnippetChunker'] = 'MdSnippetChunker'
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[tuple]:
        """
        Extracts paired comments and code blocks from Markdown content based on the 
        specified programming language.
        """
        if self.language:
            # If language is specified, directly extract the corresponding blocks
            pattern = fr'```{self.language}\s*(.*?)```'
            scripts = re.findall(pattern, text, re.DOTALL)
            comments_temp = re.split(pattern, text, flags=re.DOTALL)
        else:
            # Extract blocks and languages dynamically if no specific language is provided
            scripts = []
            languages = []
            for match in re.finditer(r'```(\w+)?\s*(.*?)```', text, re.DOTALL):
                if match.group(1) is not None:  # Checks if a language identifier is present
                    languages.append(match.group(1))
                    scripts.append(match.group(2))
                else:
                    languages.append('')  # Default to an empty string if no language is found
                    scripts.append(match.group(2))
            comments_temp = re.split(r'```.*?```', text, flags=re.DOTALL)

        comments = [comment.strip() for comment in comments_temp]

        if text.strip().startswith('```'):
            comments = [''] + comments
        if text.strip().endswith('```'):
            comments.append('')

        if self.language:
            structured_output = [(comments[i], self.language, scripts[i].strip()) for i in range(len(scripts))]
        else:
            structured_output = [(comments[i], languages[i], scripts[i].strip()) for i in range(len(scripts))]

        return structured_output


```

```swarmauri/standard/vectors/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vectors/base/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vectors/base/VectorBase.py

from abc import ABC, abstractmethod
from typing import List, Optional, Literal
import json
import numpy as np
from pydantic import Field
from swarmauri.core.vectors.IVector import IVector
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes

class VectorBase(IVector, ComponentBase):
    value: List[float]
    resource: Optional[str] =  Field(default=ResourceTypes.VECTOR.value, frozen=True)
    type: Literal['VectorBase'] = 'VectorBase'

    def to_numpy(self) -> np.ndarray:
        """
        Converts the vector into a numpy array.

        Returns:
            np.ndarray: The numpy array representation of the vector.
        """
        return np.array(self.data)
        
    def __len__(self):
        return len(self.data)


```

```swarmauri/standard/vectors/concrete/__init__.py

# -*- coding: utf-8 -*-



```

```swarmauri/standard/vectors/concrete/Vector.py

from typing import Literal
from swarmauri.standard.vectors.base.VectorBase import VectorBase

class Vector(VectorBase):
    type: Literal['Vector'] = 'Vector'

```

```swarmauri/standard/vectors/concrete/VectorProductMixin.py

import numpy as np
from typing import List
from pydantic import BaseModel
from swarmauri.core.vectors.IVectorProduct import IVectorProduct
from swarmauri.standard.vectors.concrete.Vector import Vector

class VectorProductMixin(IVectorProduct, BaseModel):
    def dot_product(self, vector_a: Vector, vector_b: Vector) -> float:
        a = np.array(vector_a.value).flatten()
        b = np.array(vector_b.value).flatten()
        return np.dot(a, b)
    
    def cross_product(self, vector_a: Vector, vector_b: Vector) -> Vector:
        if len(vector_a.value) != 3 or len(vector_b.value) != 3:
            raise ValueError("Cross product is only defined for 3-dimensional vectors")
        a = np.array(vector_a.value)
        b = np.array(vector_b.value)
        cross = np.cross(a, b)
        return Vector(value=cross.tolist())
    
    def vector_triple_product(self, vector_a: Vector, vector_b: Vector, vector_c: Vector) -> Vector:
        a = np.array(vector_a.value)
        b = np.array(vector_b.value)
        c = np.array(vector_c.value)
        result = np.cross(a, np.cross(b, c))
        return Vector(value=result.tolist())
    
    def scalar_triple_product(self, vector_a: Vector, vector_b: Vector, vector_c: Vector) -> float:
        a = np.array(vector_a.value)
        b = np.array(vector_b.value)
        c = np.array(vector_c.value)
        return np.dot(a, np.cross(b, c))

```

```swarmauri/standard/embeddings/__init__.py

#

```

```swarmauri/standard/embeddings/base/__init__.py

#

```

```swarmauri/standard/embeddings/base/EmbeddingBase.py

from typing import Optional, Literal
from pydantic import Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.embeddings.IVectorize import IVectorize
from swarmauri.core.embeddings.IFeature import IFeature
from swarmauri.core.embeddings.ISaveModel import ISaveModel

class EmbeddingBase(IVectorize, IFeature, ISaveModel, ComponentBase):
    resource: Optional[str] =  Field(default=ResourceTypes.EMBEDDING.value, frozen=True)
    type: Literal['EmbeddingBase'] = 'EmbeddingBase'
        


```

```swarmauri/standard/embeddings/concrete/__init__.py

#

```

```swarmauri/standard/embeddings/concrete/Doc2VecEmbedding.py

from typing import List, Union, Any, Literal
from pydantic import PrivateAttr
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from swarmauri.standard.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.standard.vectors.concrete.Vector import Vector

class Doc2VecEmbedding(EmbeddingBase):
    _model = PrivateAttr()
    type: Literal['Doc2VecEmbedding'] = 'Doc2VecEmbedding'    

    def __init__(self, 
                 vector_size: int = 2000, 
                 window: int = 10,
                 min_count: int = 1,
                 workers: int = 5,
                 **kwargs):
        super().__init__(**kwargs)
        self._model = Doc2Vec(vector_size=vector_size, 
                              window=window, 
                              min_count=min_count, 
                              workers=workers)
        

    def extract_features(self) -> List[Any]:
        return list(self._model.wv.key_to_index.keys())

    def fit(self, documents: List[str], labels=None) -> None:
        tagged_data = [TaggedDocument(words=_d.split(), 
            tags=[str(i)]) for i, _d in enumerate(documents)]

        self._model.build_vocab(tagged_data)
        self._model.train(tagged_data, total_examples=self._model.corpus_count, epochs=self._model.epochs)

    def transform(self, documents: List[str]) -> List[Vector]:
        vectors = [self._model.infer_vector(doc.split()) for doc in documents]
        return [Vector(value=vector) for vector in vectors]

    def fit_transform(self, documents: List[str], **kwargs) -> List[Vector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: str) -> Vector:
        vector = self._model.infer_vector(data.split())
        return Vector(value=vector.squeeze().tolist())

    def save_model(self, path: str) -> None:
        """
        Saves the Doc2Vec model to the specified path.
        """
        self._model.save(path)
    
    def load_model(self, path: str) -> None:
        """
        Loads a Doc2Vec model from the specified path.
        """
        self._model = Doc2Vec.load(path)

```

```swarmauri/standard/embeddings/concrete/TfidfEmbedding.py

from typing import List, Union, Any, Literal
import joblib
from pydantic import PrivateAttr
from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer

from swarmauri.standard.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.standard.vectors.concrete.Vector import Vector

class TfidfEmbedding(EmbeddingBase):
    _model = PrivateAttr()
    _fit_matrix = PrivateAttr()
    type: Literal['TfidfEmbedding'] = 'TfidfEmbedding'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model = SklearnTfidfVectorizer()
    
    def extract_features(self):
        return self._model.get_feature_names_out().tolist()

    def fit(self, documents: List[str]) -> None:
        self._fit_matrix = self._model.fit_transform(documents)

    def fit_transform(self, documents: List[str]) -> List[Vector]:
        self._fit_matrix = self._model.fit_transform(documents)
        # Convert the sparse matrix rows into Vector instances
        vectors = [Vector(value=vector.toarray().flatten()) for vector in self._fit_matrix]
        return vectors
    
    def transform(self, data: Union[str, Any], documents: List[str]) -> List[Vector]:
        raise NotImplementedError('Transform not implemented on TFIDFVectorizer.')

    def infer_vector(self, data: str, documents: List[str]) -> Vector:
        documents.append(data)
        tmp_tfidf_matrix = self.transform(documents)
        query_vector = tmp_tfidf_matrix[-1]
        return query_vector

    def save_model(self, path: str) -> None:
        """
        Saves the TF-IDF model to the specified path using joblib.
        """
        joblib.dump(self._model, path)
    
    def load_model(self, path: str) -> None:
        """
        Loads a TF-IDF model from the specified path using joblib.
        """
        self._model = joblib.load(path)

```

```swarmauri/standard/embeddings/concrete/MlmEmbedding.py

from typing import List, Union, Any, Literal
import logging
from pydantic import PrivateAttr
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
from torch.optim import AdamW
from transformers import AutoModelForMaskedLM, AutoTokenizer
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

from swarmauri.standard.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.standard.vectors.concrete.Vector import Vector

class MlmEmbedding(EmbeddingBase):
    """
    EmbeddingBase implementation that fine-tunes a Masked Language Model (MLM).
    """

    embedding_name: str = 'bert-base-uncased'
    batch_size: int = 32
    learning_rate: float = 5e-5
    masking_ratio: float = 0.15
    randomness_ratio: float = 0.10
    epochs: int = 0
    add_new_tokens: bool = False
    _tokenizer = PrivateAttr()
    _model = PrivateAttr()
    _device = PrivateAttr()
    _mask_token_id = PrivateAttr()        
    type: Literal['MlmEmbedding'] = 'MlmEmbedding'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tokenizer = AutoTokenizer.from_pretrained(self.embedding_name)
        self._model = AutoModelForMaskedLM.from_pretrained(self.embedding_name)
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model.to(self._device)
        self._mask_token_id = self._tokenizer.convert_tokens_to_ids([self._tokenizer.mask_token])[0]

    def extract_features(self) -> List[str]:
        """
        Extracts the tokens from the vocabulary of the fine-tuned MLM.

        Returns:
        - List[str]: A list of token strings in the model's vocabulary.
        """
        # Get the vocabulary size
        vocab_size = len(self._tokenizer)
        
        # Retrieve the token strings for each id in the vocabulary
        token_strings = [self._tokenizer.convert_ids_to_tokens(i) for i in range(vocab_size)]
        
        return token_strings

    def _mask_tokens(self, encodings):
        input_ids = encodings.input_ids.to(self._device)
        attention_mask = encodings.attention_mask.to(self._device)

        labels = input_ids.detach().clone()

        probability_matrix = torch.full(labels.shape, self.masking_ratio, device=self._device)
        special_tokens_mask = [
            self._tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
        ]
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool, device=self._device), value=0.0)
        masked_indices = torch.bernoulli(probability_matrix).bool()

        labels[~masked_indices] = -100
        
        indices_replaced = torch.bernoulli(torch.full(labels.shape, self.masking_ratio, device=self._device)).bool() & masked_indices
        input_ids[indices_replaced] = self._mask_token_id

        indices_random = torch.bernoulli(torch.full(labels.shape, self.randomness_ratio, device=self._device)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self._tokenizer), labels.shape, dtype=torch.long, device=self._device)
        input_ids[indices_random] = random_words[indices_random]

        return input_ids, attention_mask, labels

    def fit(self, documents: List[Union[str, Any]]):
        # Check if we need to add new tokens
        if self.add_new_tokens:
            new_tokens = self.find_new_tokens(documents)
            if new_tokens:
                num_added_toks = self._tokenizer.add_tokens(new_tokens)
                if num_added_toks > 0:
                    logging.info(f"Added {num_added_toks} new tokens.")
                    self.model.resize_token_embeddings(len(self._tokenizer))

        encodings = self._tokenizer(documents, return_tensors='pt', padding=True, truncation=True, max_length=512)
        input_ids, attention_mask, labels = self._mask_tokens(encodings)
        optimizer = AdamW(self._model.parameters(), lr=self.learning_rate)
        dataset = TensorDataset(input_ids, attention_mask, labels)
        data_loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self._model.train()
        for batch in data_loader:
            batch = {k: v.to(self._device) for k, v in zip(['input_ids', 'attention_mask', 'labels'], batch)}
            outputs = self._model(**batch)
            loss = outputs.loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        self.epochs += 1
        logging.info(f"Epoch {self.epochs} complete. Loss {loss.item()}")

    def find_new_tokens(self, documents):
        # Identify unique words in documents that are not in the tokenizer's vocabulary
        unique_words = set()
        for doc in documents:
            tokens = set(doc.split())  # Simple whitespace tokenization
            unique_words.update(tokens)
        existing_vocab = set(self._tokenizer.get_vocab().keys())
        new_tokens = list(unique_words - existing_vocab)
        return new_tokens if new_tokens else None

    def transform(self, documents: List[Union[str, Any]]) -> List[Vector]:
        """
        Generates embeddings for a list of documents using the fine-tuned MLM.
        """
        self._model.eval()
        embedding_list = []
        
        for document in documents:
            inputs = self._tokenizer(document, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self._model(**inputs)
            # Extract embedding (for simplicity, averaging the last hidden states)
            if hasattr(outputs, 'last_hidden_state'):
                embedding = outputs.last_hidden_state.mean(1)
            else:
                # Fallback or corrected attribute access
                embedding = outputs['logits'].mean(1)
            embedding = embedding.cpu().numpy()
            embedding_list.append(Vector(value=embedding.squeeze().tolist()))

        return embedding_list

    def fit_transform(self, documents: List[Union[str, Any]], **kwargs) -> List[Vector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, data: Union[str, Any], *args, **kwargs) -> Vector:
        """
        Generates an embedding for the input data.

        Parameters:
        - data (Union[str, Any]): The input data, expected to be a textual representation.
                                  Could be a single string or a batch of strings.
        """
        # Tokenize the input data and ensure the tensors are on the correct device.
        self._model.eval()
        inputs = self._tokenizer(data, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        # Generate embeddings using the model
        with torch.no_grad():
            outputs = self._model(**inputs)

        if hasattr(outputs, 'last_hidden_state'):
            # Access the last layer and calculate the mean across all tokens (simple pooling)
            embedding = outputs.last_hidden_state.mean(dim=1)
        else:
            embedding = outputs['logits'].mean(1)
        # Move the embeddings back to CPU for compatibility with downstream tasks if necessary
        embedding = embedding.cpu().numpy()

        return Vector(value=embedding.squeeze().tolist())

    def save_model(self, path: str) -> None:
        """
        Saves the model and tokenizer to the specified directory.
        """
        self._model.save_pretrained(path)
        self._tokenizer.save_pretrained(path)

    def load_model(self, path: str) -> None:
        """
        Loads the model and tokenizer from the specified directory.
        """
        self._model = AutoModelForMaskedLM.from_pretrained(path)
        self._tokenizer = AutoTokenizer.from_pretrained(path)
        self._model.to(self._device)  # Ensure the model is loaded to the correct device

```

```swarmauri/standard/embeddings/concrete/NmfEmbedding.py

import joblib
from typing import List, Any, Literal
from pydantic import PrivateAttr
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from swarmauri.standard.embeddings.base.EmbeddingBase import EmbeddingBase
from swarmauri.standard.vectors.concrete.Vector import Vector

class NmfEmbedding(EmbeddingBase):
    n_components: int = 10
    _tfidf_vectorizer = PrivateAttr()
    _model = PrivateAttr()
    feature_names: List[Any] = []
    
    type: Literal['NmfEmbedding'] = 'NmfEmbedding'
    def __init__(self,**kwargs):

        super().__init__(**kwargs)
        # Initialize TF-IDF Vectorizer
        self._tfidf_vectorizer = TfidfVectorizer()
        # Initialize NMF with the desired number of components
        self._model = NMF(n_components=self.n_components)

    def fit(self, data):
        """
        Fit the NMF model to data.

        Args:
            data (Union[str, Any]): The text data to fit.
        """
        # Transform data into TF-IDF matrix
        tfidf_matrix = self._tfidf_vectorizer.fit_transform(data)
        # Fit the NMF model
        self._model.fit(tfidf_matrix)
        # Store feature names
        self.feature_names = self._tfidf_vectorizer.get_feature_names_out()

    def transform(self, data):
        """
        Transform new data into NMF feature space.

        Args:
            data (Union[str, Any]): Text data to transform.

        Returns:
            List[IVector]: A list of vectors representing the transformed data.
        """
        # Transform data into TF-IDF matrix
        tfidf_matrix = self._tfidf_vectorizer.transform(data)
        # Transform TF-IDF matrix into NMF space
        nmf_features = self._model.transform(tfidf_matrix)

        # Wrap NMF features in SimpleVector instances and return
        return [Vector(value=features.tolist()) for features in nmf_features]

    def fit_transform(self, data):
        """
        Fit the model to data and then transform it.
        
        Args:
            data (Union[str, Any]): The text data to fit and transform.

        Returns:
            List[IVector]: A list of vectors representing the fitted and transformed data.
        """
        self.fit(data)
        return self.transform(data)

    def infer_vector(self, data):
        """
        Convenience method for transforming a single data point.
        
        Args:
            data (Union[str, Any]): Single text data to transform.

        Returns:
            IVector: A vector representing the transformed single data point.
        """
        return self.transform([data])[0]
    
    def extract_features(self):
        """
        Extract the feature names from the TF-IDF vectorizer.
        
        Returns:
            The feature names.
        """
        return self.feature_names.tolist()

    def save_model(self, path: str) -> None:
        """
        Saves the NMF model and TF-IDF vectorizer using joblib.
        """
        # It might be necessary to save both tfidf_vectorizer and model
        # Consider using a directory for 'path' or appended identifiers for each model file
        joblib.dump(self._tfidf_vectorizer, f"{path}_tfidf.joblib")
        joblib.dump(self._model, f"{path}_nmf.joblib")

    def load_model(self, path: str) -> None:
        """
        Loads the NMF model and TF-IDF vectorizer from paths using joblib.
        """
        self._tfidf_vectorizer = joblib.load(f"{path}_tfidf.joblib")
        self._model = joblib.load(f"{path}_nmf.joblib")
        # Dependending on your implementation, you might need to refresh the feature_names
        self.feature_names = self._tfidf_vectorizer.get_feature_names_out()

```

```swarmauri/standard/tracing/__init__.py

#

```

```swarmauri/standard/tracing/base/__init__.py

#

```

```swarmauri/standard/tracing/concrete/SimpleTracer.py

from datetime import datetime
import uuid
from typing import Dict, Any, Optional

from swarmauri.core.tracing.ITracer import ITracer
from swarmauri.standard.tracing.concrete.SimpleTraceContext import SimpleTraceContext

class SimpleTracer(ITracer):
    _instance = None  # Singleton instance placeholder

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if SimpleTracer._instance is not None:
            raise RuntimeError("SimpleTracer is a singleton. Use SimpleTracer.instance().")
        self.trace_stack = []

    def start_trace(self, name: str, initial_attributes: Optional[Dict[str, Any]] = None) -> SimpleTraceContext:
        trace_id = str(uuid.uuid4())
        trace_context = SimpleTraceContext(trace_id, name, initial_attributes)
        self.trace_stack.append(trace_context)
        return trace_context

    def end_trace(self):
        if self.trace_stack:
            completed_trace = self.trace_stack.pop()
            completed_trace.close()
            # Example of simply printing the completed trace; in practice, you might log it or store it elsewhere
            print(f"Trace Completed: {completed_trace.name}, Duration: {completed_trace.start_time} to {completed_trace.end_time}, Attributes: {completed_trace.attributes}")

    def annotate_trace(self, key: str, value: Any):
        if not self.trace_stack:
            print("No active trace to annotate.")
            return
        current_trace = self.trace_stack[-1]
        current_trace.add_attribute(key, value)

```

```swarmauri/standard/tracing/concrete/TracedVariable.py

from typing import Any
from swarmauri.standard.tracing.concrete.SimpleTracer import SimpleTracer  # Assuming this is the path to the tracer

class TracedVariable:
    """
    Wrapper class to trace multiple changes to a variable within the context manager.
    """
    def __init__(self, name: str, value: Any, tracer: SimpleTracer):
        self.name = name
        self._value = value
        self._tracer = tracer
        self._changes = []  # Initialize an empty list to track changes

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any):
        # Record the change before updating the variable's value
        change_annotation = {"from": self._value, "to": new_value}
        self._changes.append(change_annotation)
        
        # Update the trace by appending the latest change to the list under a single key
        # Note that the key is now constant and does not change with each update
        self._tracer.annotate_trace(key=f"{self.name}_changes", value=self._changes)
        
        self._value = new_value

```

```swarmauri/standard/tracing/concrete/ChainTracer.py

from swarmauri.core.tracing.IChainTracer import IChainTracer
from typing import Callable, List, Tuple, Dict, Any   
        
class ChainTracer(IChainTracer):
    def __init__(self):
        self.traces = []

    def process_chain(self, chain: List[Tuple[Callable[..., Any], List[Any], Dict[str, Any]]]) -> "ChainTracer":
        """
        Processes each item in the operation chain by executing the specified external function
        with its args and kwargs. Logs starting, annotating, and ending the trace based on tuple position.

        Args:
            chain (List[Tuple[Callable[..., Any], List[Any], Dict[str, Any]]]): A list where each tuple contains:
                - An external function to execute.
                - A list of positional arguments for the function.
                - A dictionary of keyword arguments for the function.
        """
        for i, (func, args, kwargs) in enumerate(chain):
            # Infer operation type and log
            
            if i == 0:
                operation = "Start"
                self.start_trace(*args, **kwargs)
            elif i == len(chain) - 1:
                operation = "End"
                self.end_trace(*args, **kwargs)
            else:
                operation = "Annotate"
                self.annotate_trace(*args, **kwargs)
                
            # For the actual external function call
            result = func(*args, **kwargs)
            print(f"Function '{func.__name__}' executed with result: {result}")

            self.traces.append((operation, func, args, kwargs, result))

        return self

    def start_trace(self, *args, **kwargs) -> None:
        print(f"Starting trace with args: {args}, kwargs: {kwargs}")
        
    def annotate_trace(self, *args, **kwargs) -> None:
        print(f"Annotating trace with args: {args}, kwargs: {kwargs}")

    def end_trace(self, *args, **kwargs) -> None:
        print(f"Ending trace with args: {args}, kwargs: {kwargs}")

    def show(self) -> None:
        for entry in self.traces:
            print(entry)

```

```swarmauri/standard/tracing/concrete/SimpleTraceContext.py

from datetime import datetime
from typing import Dict, Any, Optional

from swarmauri.core.tracing.ITraceContext import ITraceContext

class SimpleTraceContext(ITraceContext):
    def __init__(self, trace_id: str, name: str, initial_attributes: Optional[Dict[str, Any]] = None):
        self.trace_id = trace_id
        self.name = name
        self.attributes = initial_attributes if initial_attributes else {}
        self.start_time = datetime.now()
        self.end_time = None

    def get_trace_id(self) -> str:
        return self.trace_id

    def add_attribute(self, key: str, value: Any):
        self.attributes[key] = value

    def close(self):
        self.end_time = datetime.now()

```

```swarmauri/standard/tracing/concrete/VariableTracer.py

from contextlib import contextmanager

from swarmauri.standard.tracing.concrete.TracedVariable import TracedVariable
from swarmauri.standard.tracing.concrete.SimpleTracer import SimpleTracer

# Initialize a global instance of SimpleTracer for use across the application
global_tracer = SimpleTracer()

@contextmanager
def VariableTracer(name: str, initial_value=None):
    """
    Context manager for tracing the declaration, modification, and usage of a variable.
    """
    trace_context = global_tracer.start_trace(name=f"Variable: {name}", initial_attributes={"initial_value": initial_value})
    traced_variable = TracedVariable(name, initial_value, global_tracer)
    
    try:
        yield traced_variable
    finally:
        # Optionally record any final value or state of the variable before it goes out of scope
        global_tracer.annotate_trace(key=f"{name}_final", value={"final_value": traced_variable.value})
        # End the trace, marking the variable's lifecycle
        global_tracer.end_trace()

```

```swarmauri/standard/tracing/concrete/CallableTracer.py

import functools
from swarmauri.standard.tracing.concrete.SimpleTracer import SimpleTracer  # Import SimpleTracer from the previously defined path

# Initialize the global tracer object
tracer = SimpleTracer()

def CallableTracer(func):
    """
    A decorator to trace function or method calls, capturing inputs, outputs, and the caller.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Trying to automatically identify the caller details; practical implementations 
        # might need to adjust based on specific requirements or environment.
        caller_info = f"{func.__module__}.{func.__name__}"
        
        # Start a new trace context for this callable
        trace_context = tracer.start_trace(name=caller_info, initial_attributes={'args': args, 'kwargs': kwargs})
        
        try:
            # Call the actual function/method
            result = func(*args, **kwargs)
            tracer.annotate_trace(key="result", value=result)
            return result
        except Exception as e:
            # Optionally annotate the trace with the exception details
            tracer.annotate_trace(key="exception", value=str(e))
            raise  # Re-raise the exception to not interfere with the program's flow
        finally:
            # End the trace after the function call is complete
            tracer.end_trace()
    return wrapper

```

```swarmauri/standard/tracing/concrete/__init__.py



```

```swarmauri/standard/chains/__init__.py



```

```swarmauri/standard/chains/base/__init__.py

#

```

```swarmauri/standard/chains/base/ChainBase.py

from typing import List, Dict, Any, Optional, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChain import IChain
from swarmauri.stanard.chains.concrete.ChainStep import ChainStep
from swarmauri.core.typing import SubclassUnion

class ChainBase(IChain, ComponentBase):
    """
    A base implementation of the IChain interface.
    """
    steps: List[ChainStep] = []
    resource: Optional[str] =  Field(default=ResourceTypes.CHAIN.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ChainBase'] = 'ChainBase'

    def add_step(self, step: ChainStep) -> None:
        self.steps.append(step)

    def remove_step(self, step: ChainStep) -> None:
        """
        Removes an existing step from the chain. This alters the chain's execution sequence
        by excluding the specified step from subsequent executions of the chain.

        Parameters:
            step (ChainStep): The Callable representing the step to remove from the chain.
        """

        raise NotImplementedError('This is not yet implemented')

    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError('This is not yet implemented')



```

```swarmauri/standard/chains/base/ChainStepBase.py

from typing import Any, Tuple, Dict, Optional, Union, Literal
from pydantic import Field, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChainStep import IChainStep

class ChainStepBase(IChainStep, ComponentBase):
    """
    Represents a single step within an execution chain.
    """
    key: str
    method: SubclassUnion[ToolBase]
    args: Tuple = Field(default_factory=tuple)
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    ref: Optional[str] =  Field(default=None)
    resource: Optional[str] =  Field(default=ResourceTypes.CHAINSTEP.value)
    type: Literal['ChainStepBase'] = 'ChainStepBase'

```

```swarmauri/standard/chains/base/PromptContextChainBase.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Literal
from pydantic import Field
from collections import defaultdict, deque
import re
import numpy as np


from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.standard.chains.concrete.ChainStep import ChainStep
from swarmauri.standard.chains.base.ChainContextBase import ChainContextBase
from swarmauri.standard.prompts.concrete.PromptMatrix import PromptMatrix
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.core.prompts.IPromptMatrix import IPromptMatrix
from swarmauri.core.chains.IChainDependencyResolver import IChainDependencyResolver

class PromptContextChainBase(IChainDependencyResolver, ChainContextBase, ComponentBase):
    prompt_matrix: PromptMatrix
    agents: List[SubclassUnion[AgentBase]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    llm_kwargs: Dict[str, Any] = Field(default_factory=dict)
    response_matrix: Optional[PromptMatrix] = None
    current_step_index: int = 0
    steps: List[Any] = Field(default_factory=list)
    resource: Optional[str] =  Field(default=ResourceTypes.CHAIN.value)
    type: Literal['PromptContextChainBase'] = 'PromptContextChainBase'
    
    def __init__(self, **data: Any):
        super().__init__(**data)
        # Now that the instance is created, we can safely access `prompt_matrix.shape`
        self.response_matrix = PromptMatrix(matrix=[[None for _ in range(self.prompt_matrix.shape[1])] 
                                                    for _ in range(self.prompt_matrix.shape[0])])

    def execute(self, build_dependencies=True) -> None:
        """
        Execute the chain of prompts based on the state of the prompt matrix.
        Iterates through each sequence in the prompt matrix, resolves dependencies, 
        and executes prompts in the resolved order.
        """
        if build_dependencies:
            self.steps = self.build_dependencies()
            self.current_step_index = 0

        while self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            method = step.method
            args = step.args
            ref = step.ref
            result = method(*args)
            self.context[ref] = result
            prompt_index = self._extract_step_number(ref)
            self._update_response_matrix(args[0], prompt_index, result)
            self.current_step_index += 1  # Move to the next step
        else:
            print("All steps have been executed.")

    def execute_next_step(self):
        """
        Execute the next step in the steps list if available.
        """
        if self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            method = step.method
            args = step.args
            ref = step.ref
            result = method(*args)
            self.context[ref] = result
            prompt_index = self._extract_step_number(ref)
            self._update_response_matrix(args[0], prompt_index, result)
            self.current_step_index += 1  # Move to the next step
        else:
            print("All steps have been executed.")

    def _execute_prompt(self, agent_index: int, prompt: str, ref: str):
        """
        Executes a given prompt using the specified agent and updates the response.
        """
        formatted_prompt = prompt.format(**self.context)  # Using context for f-string formatting
        
        agent = self.agents[agent_index]
        # get the unformatted version
        unformatted_system_context = agent.system_context
        # use the formatted version
        agent.system_context = agent.system_context.content.format(**self.context)
        response = agent.exec(formatted_prompt, model_kwargs=self.model_kwargs)
        # reset back to the unformatted version
        agent.system_context = unformatted_system_context

        self.context[ref] = response
        prompt_index = self._extract_step_number(ref)
        self._update_response_matrix(agent_index, prompt_index, response)
        return response

    def _update_response_matrix(self, agent_index: int, prompt_index: int, response: Any):
        self.response_matrix.matrix[agent_index][prompt_index] = response


    def _extract_agent_number(self, text):
        # Regular expression to match the pattern and capture the agent number
        match = re.search(r'\{Agent_(\d+)_Step_\d+_response\}', text)
        if match:
            # Return the captured group, which is the agent number
            return int(match.group(1))
        else:
            # Return None if no match is found
            return None
    
    def _extract_step_number(self, ref):
        # This regex looks for the pattern '_Step_' followed by one or more digits.
        match = re.search(r"_Step_(\d+)_", ref)
        if match:
            return int(match.group(1))  # Convert the extracted digits to an integer
        else:
            return None  # If no match is found, return None
    
    def build_dependencies(self) -> List[ChainStep]:
        """
        Build the chain steps in the correct order by resolving dependencies first.
        """
        steps = []
        
        for i in range(self.prompt_matrix.shape[1]):
            try:
                sequence = np.array(self.prompt_matrix.matrix)[:,i].tolist()
                execution_order = self.resolve_dependencies(sequence=sequence)
                for j in execution_order:
                    prompt = sequence[j]
                    if prompt:
                        ref = f"Agent_{j}_Step_{i}_response"  # Using a unique reference string
                        step = ChainStep(
                            key=f"Agent_{j}_Step_{i}",
                            method=self._execute_prompt,
                            args=[j, prompt, ref],
                            ref=ref
                        )
                        steps.append(step)
            except Exception as e:
                print(str(e))
        return steps

    def resolve_dependencies(self, sequence: List[Optional[str]]) -> List[int]:
        """
        Resolve dependencies within a specific sequence of the prompt matrix.
        
        Args:
            matrix (List[List[Optional[str]]]): The prompt matrix.
            sequence_index (int): The index of the sequence to resolve dependencies for.

        Returns:
            List[int]: The execution order of the agents for the given sequence.
        """
        
        return [x for x in range(0, len(sequence), 1)]

```

```swarmauri/standard/chains/base/ChainContextBase.py

from typing import Any, Callable, Dict, List, Optional, Literal
from pydantic import Field, ConfigDict
import re
from swarmauri.standard.chains.concrete.ChainStep import ChainStep
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChainContext import IChainContext

class ChainContextBase(IChainContext, ComponentBase):
    steps: List[ChainStep] = []
    context: Dict = {}
    resource: Optional[str] =  Field(default=ResourceTypes.CHAIN.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ChainContextBase'] = 'ChainContextBase'

    def update(self, **kwargs):
        self.context.update(kwargs)

    def get_value(self, key: str) -> Any:
        return self.context.get(key)

    def _resolve_fstring(self, template: str) -> str:
        pattern = re.compile(r'{([^}]+)}')
        def replacer(match):
            expression = match.group(1)
            try:
                return str(eval(expression, {}, self.context))
            except Exception as e:
                print(f"Failed to resolve expression: {expression}. Error: {e}")
                return f"{{{expression}}}"
        return pattern.sub(replacer, template)

    def _resolve_placeholders(self, value: Any) -> Any:
        if isinstance(value, str):
            return self._resolve_fstring(value)
        elif isinstance(value, dict):
            return {k: self._resolve_placeholders(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._resolve_placeholders(v) for v in value]
        else:
            return value

    def _resolve_ref(self, value: Any) -> Any:
        if isinstance(value, str) and value.startswith('$'):
            placeholder = value[1:]
            return placeholder
        return value

```

```swarmauri/standard/chains/concrete/__init__.py



```

```swarmauri/standard/chains/concrete/CallableChain.py

from typing import Any, Callable, List, Dict, Optional
from swarmauri.core.chains.ICallableChain import ICallableChain, CallableDefinition


class CallableChain(ICallableChain):
    
    def __init__(self, callables: Optional[List[CallableDefinition]] = None):
        
        self.callables = callables if callables is not None else []

    def __call__(self, *initial_args, **initial_kwargs):
        result = None
        for func, args, kwargs in self.callables:
            if result is not None:
                # If there was a previous result, use it as the first argument for the next function
                args = [result] + list(args)
            result = func(*args, **kwargs)
        return result
    
    def add_callable(self, func: Callable[[Any], Any], args: List[Any] = None, kwargs: Dict[str, Any] = None) -> None:
        # Add a new callable to the chain
        self.callables.append((func, args or [], kwargs or {}))
    
    def __or__(self, other: "CallableChain") -> "CallableChain":
        if not isinstance(other, CallableChain):
            raise TypeError("Operand must be an instance of CallableChain")
        
        new_chain = CallableChain(self.callables + other.callables)
        return new_chain

```

```swarmauri/standard/chains/concrete/ChainStep.py

from typing import Literal
from swarmauri.standard.chains.base.ChainStepBase import ChainStepBase

class ChainStep(ChainStepBase):
    """
    Represents a single step within an execution chain.
    """
    type: Literal['ChainStep'] = 'ChainStep'

```

```swarmauri/standard/chains/concrete/ContextChain.py

from typing import Any, Dict, List, Callable, Optional, Tuple, Union, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.chains.concrete.ChainStep import ChainStep
from swarmauri.standard.chains.base.ChainContextBase import ChainContextBase
from swarmauri.core.chains.IChain import IChain

class ContextChain(IChain, ChainContextBase):
    """
    Enhanced to support ChainSteps with return parameters, storing return values as instance state variables.
    Implements the IChain interface including get_schema_info and remove_step methods.
    """
    type: Literal['ContextChain'] = 'ContextChain'

    def add_step(self, 
        key: str, 
        method: SubclassUnion[ToolBase],
        args: Tuple = (), 
        kwargs: Dict[str, Any] = {}, 
        ref: Optional[str] = None):

        # Directly store args, kwargs, and optionally a return_key without resolving them
        step = ChainStep(key=key, method=method, args=args, kwargs=kwargs, ref=ref)
        self.steps.append(step)

    def remove_step(self, step: ChainStep) -> None:
        self.steps = [s for s in self._steps if s.key != step.key]

    def execute(self, *args, **kwargs) -> Any:
        # Execute the chain and manage result storage based on return_key
        for step in self.steps:
            resolved_args = [self._resolve_placeholders(arg) for arg in step.args]
            resolved_kwargs = {k: self._resolve_placeholders(v) for k, v in step.kwargs.items() if k != 'ref'}
            result = step.method(*resolved_args, **resolved_kwargs)
            if step.ref:  # step.ref is used here as the return_key analogy
                resolved_ref = self._resolve_ref(step.ref)
                self.context[resolved_ref] = result
                self.update(**{resolved_ref: result})  # Update context with new state value
        return self.context  # or any specific result you intend to return


```

```swarmauri/standard/chains/concrete/PromptContextChain.py

from typing import Literal
from swarmauri.standard.chains.base.PromptContextChainBase import PromptContextChainBase

class PromptContextChain(PromptContextChainBase):
    type: Literal['PromptContextChain'] = 'PromptContextChain'

```

```swarmauri/standard/distances/__init__.py



```

```swarmauri/standard/distances/base/__init__.py



```

```swarmauri/standard/distances/base/DistanceBase.py

from abc import abstractmethod
from numpy.linalg import norm
from typing import List, Optional, Literal
from pydantic import Field
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.vectors.concrete.VectorProductMixin import VectorProductMixin
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes

class DistanceBase(IDistanceSimilarity, VectorProductMixin, ComponentBase):
    """
    Implements cosine distance calculation as an IDistanceSimiliarity interface.
    Cosine distance measures the cosine of the angle between two non-zero vectors
    of an inner product space, capturing the orientation rather than the magnitude 
    of these vectors.
    """
    resource: Optional[str] =  Field(default=ResourceTypes.DISTANCE.value, frozen=True)
    type: Literal['DistanceBase'] = 'DistanceBase'
    @abstractmethod
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        pass
    
    @abstractmethod
    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        pass
       

    @abstractmethod
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        pass
        
    @abstractmethod
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        pass
        

```

```swarmauri/standard/distances/concrete/ChiSquaredDistance.py

from typing import List, Literal

from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase

class ChiSquaredDistance(DistanceBase):
    """
    Implementation of the IDistanceSimilarity interface using Chi-squared distance metric.
    """    
    type: Literal['ChiSquaredDistance'] = 'ChiSquaredDistance'

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Chi-squared distance between two vectors.
        """
        if len(vector_a.value) != len(vector_b.value):
            raise ValueError("Vectors must have the same dimensionality.")

        chi_squared_distance = 0
        for a, b in zip(vector_a.value, vector_b.value):
            if (a + b) != 0:
                chi_squared_distance += (a - b) ** 2 / (a + b)

        return 0.5 * chi_squared_distance

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Compute the similarity between two vectors based on the Chi-squared distance.
        """
        return 1 / (1 + self.distance(vector_a, vector_b))
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities



```

```swarmauri/standard/distances/concrete/CosineDistance.py

from numpy.linalg import norm
from typing import List, Literal
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase

class CosineDistance(DistanceBase):
    """
    Implements cosine distance calculation as an IDistanceSimiliarity interface.
    Cosine distance measures the cosine of the angle between two non-zero vectors
    of an inner product space, capturing the orientation rather than the magnitude 
    of these vectors.
    """
    type: Literal['CosineDistance'] = 'CosineDistance'   
       
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """ 
        Computes the cosine distance between two vectors: 1 - cosine similarity.
    
        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.
    
        Returns:
            float: The computed cosine distance between vector_a and vector_b.
                   It ranges from 0 (completely similar) to 2 (completely dissimilar).
        """
        norm_a = norm(vector_a.value)
        norm_b = norm(vector_b.value)
    
        # Check if either of the vector norms is close to zero
        if norm_a < 1e-10 or norm_b < 1e-10:
            return 1.0  # Return maximum distance for cosine which varies between -1 to 1, so 1 indicates complete dissimilarity
    
        # Compute the cosine similarity between the vectors
        cos_sim = self.dot_product(vector_a, vector_b) / (norm_a * norm_b)
    
        # Covert cosine similarity to cosine distance
        cos_distance = 1 - cos_sim
    
        return cos_distance
    
    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the cosine similarity between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The cosine similarity between vector_a and vector_b.
        """
        return 1 - self.distance(vector_a, vector_b)

    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/EuclideanDistance.py

from math import sqrt
from typing import List, Literal
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase

class EuclideanDistance(DistanceBase):
    """
    Class to compute the Euclidean distance between two vectors.
    Implements the IDistanceSimiliarity interface.
    """    
    type: Literal['EuclideanDistance'] = 'EuclideanDistance'
    
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Euclidean distance between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The computed Euclidean distance between vector_a and vector_b.
        """
        if len(vector_a.value) != len(vector_b.value):
            raise ValueError("Vectors do not have the same dimensionality.")
        
        distance = sqrt(sum((a - b) ** 2 for a, b in zip(vector_a.value, vector_b.value)))
        return distance

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the similarity score as the inverse of the Euclidean distance between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The similarity score between vector_a and vector_b.
        """
        distance = self.distance(vector_a, vector_b)
        return 1 / (1 + distance)
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/JaccardIndexDistance.py

from typing import List, Literal
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase


class JaccardIndexDistance(DistanceBase):
    """
    A class implementing Jaccard Index as a similarity and distance metric between two vectors.
    """    
    type: Literal['JaccardIndexDistance'] = 'JaccardIndexDistance'
    
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Jaccard distance between two vectors.

        The Jaccard distance, which is 1 minus the Jaccard similarity,
        measures dissimilarity between sample sets. It's defined as
        1 - (the intersection of the sets divided by the union of the sets).

        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.

        Returns:
            float: The Jaccard distance between vector_a and vector_b.
        """
        set_a = set(vector_a.value)
        set_b = set(vector_b.value)

        # Calculate the intersection and union of the two sets.
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))

        # In the special case where the union is zero, return 1.0 which implies complete dissimilarity.
        if union == 0:
            return 1.0

        # Compute Jaccard similarity and then return the distance as 1 - similarity.
        jaccard_similarity = intersection / union
        return 1 - jaccard_similarity

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Jaccard similarity between two vectors.

        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.

        Returns:
            float: Jaccard similarity score between vector_a and vector_b.
        """
        set_a = set(vector_a.value)
        set_b = set(vector_b.value)

        # Calculate the intersection and union of the two sets.
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))

        # In case the union is zero, which means both vectors have no elements, return 1.0 implying identical sets.
        if union == 0:
            return 1.0

        # Compute and return Jaccard similarity.
        return intersection / union
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/LevenshteinDistance.py

import numpy as np
from typing import List, Literal
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase


class LevenshteinDistance(DistanceBase):
    """
    Implements the IDistance interface to calculate the Levenshtein distance between two vectors.
    The Levenshtein distance between two strings is given by the minimum number of operations needed to transform
    one string into the other, where an operation is an insertion, deletion, or substitution of a single character.
    """
    type: Literal['LevenshteinDistance'] = 'LevenshteinDistance'   
    
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Compute the Levenshtein distance between two vectors.

        Note: Since Levenshtein distance is typically calculated between strings,
        it is assumed that the vectors represent strings where each element of the
        vector corresponds to the ASCII value of a character in the string.

        Args:
            vector_a (List[float]): The first vector in the comparison.
            vector_b (List[float]): The second vector in the comparison.

        Returns:
           float: The computed Levenshtein distance between vector_a and vector_b.
        """
        string_a = ''.join([chr(int(round(value))) for value in vector_a.value])
        string_b = ''.join([chr(int(round(value))) for value in vector_b.value])
        
        return self.levenshtein(string_a, string_b)
    
    def levenshtein(self, seq1: str, seq2: str) -> float:
        """
        Calculate the Levenshtein distance between two strings.
        
        Args:
            seq1 (str): The first string.
            seq2 (str): The second string.
        
        Returns:
            float: The Levenshtein distance between seq1 and seq2.
        """
        size_x = len(seq1) + 1
        size_y = len(seq2) + 1
        matrix = np.zeros((size_x, size_y))
        
        for x in range(size_x):
            matrix[x, 0] = x
        for y in range(size_y):
            matrix[0, y] = y

        for x in range(1, size_x):
            for y in range(1, size_y):
                if seq1[x-1] == seq2[y-1]:
                    matrix[x, y] = min(matrix[x-1, y] + 1, matrix[x-1, y-1], matrix[x, y-1] + 1)
                else:
                    matrix[x, y] = min(matrix[x-1, y] + 1, matrix[x-1, y-1] + 1, matrix[x, y-1] + 1)
        
        return matrix[size_x - 1, size_y - 1]
    
    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        string_a = ''.join([chr(int(round(value))) for value in vector_a.value])
        string_b = ''.join([chr(int(round(value))) for value in vector_b.value])
        return 1 - self.levenshtein(string_a, string_b) / max(len(vector_a), len(vector_b))
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

```

```swarmauri/standard/distances/concrete/__init__.py



```

```swarmauri/standard/metrics/__init__.py



```

```swarmauri/standard/metrics/base/__init__.py



```

```swarmauri/standard/metrics/base/MetricBase.py

from typing import Any, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.metrics.IMetric import IMetric

class MetricBase(IMetric, ComponentBase):
    """
    A base implementation of the IMetric interface that provides the foundation
    for specific metric implementations.
    """
    unit: str
    value: Any = None
    resource: Optional[str] =  Field(default=ResourceTypes.METRIC.value, frozen=True)
    type: Literal['MetricBase'] = 'MetricBase'

    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value

```

```swarmauri/standard/metrics/base/MetricCalculateMixin.py

from abc import abstractmethod
from typing import Any, Literal
from pydantic import BaseModel
from swarmauri.core.metrics.IMetricCalculate import IMetricCalculate

class MetricCalculateMixin(IMetricCalculate, BaseModel):
    """
    A base implementation of the IMetric interface that provides the foundation
    for specific metric implementations.
    """
    
    def update(self, value) -> None:
        """
        Update the metric value based on new information.
        This should be used internally by the `calculate` method or other logic.
        """
        self.value = value

    @abstractmethod
    def calculate(self, **kwargs) -> Any:
        """
        Calculate the metric based on the provided data.
        This method must be implemented by subclasses to define specific calculation logic.
        """
        raise NotImplementedError('calculate is not implemented yet.')
    
    def __call__(self, **kwargs) -> Any:
        """
        Calculates the metric, updates the value, and returns the current value.
        """
        self.calculate(**kwargs)
        return self.value


```

```swarmauri/standard/metrics/base/MetricAggregateMixin.py

from typing import List, Any, Literal
from pydantic import BaseModel
from swarmauri.core.metrics.IMetricAggregate import IMetricAggregate

class MetricAggregateMixin(IMetricAggregate, BaseModel):
    """
    An abstract base class that implements the IMetric interface, providing common 
    functionalities and properties for metrics within SwarmAURI.
    """
    measurements: List[Any] = []

    
    def add_measurement(self, measurement) -> None:
        """
        Adds measurement to the internal store of measurements.
        """
        self.measurements.append(measurement)

    def reset(self) -> None:
        """
        Resets the metric's state/value, allowing for fresh calculations.
        """
        self.measurements.clear()
        self.value = None



```

```swarmauri/standard/metrics/base/MetricThresholdMixin.py

from abc import ABC, abstractmethod
from typing import Literal
from pydantic import BaseModel
from swarmauri.core.metrics.IThreshold import IThreshold

class MetricThresholdMixin(IThreshold, BaseModel):
    k: int
    

```

```swarmauri/standard/metrics/concrete/__init__.py



```

```swarmauri/standard/metrics/concrete/MeanMetric.py

from typing import Literal
from swarmauri.standard.metrics.base.MetricBase import MetricBase
from swarmauri.standard.metrics.base.MetricCalculateMixin import MetricCalculateMixin
from swarmauri.standard.metrics.base.MetricAggregateMixin import MetricAggregateMixin

class MeanMetric(MetricAggregateMixin, MetricCalculateMixin, MetricBase):
    """
    A metric that calculates the mean (average) of a list of numerical values.

    Attributes:
        name (str): The name of the metric.
        unit (str): The unit of measurement for the mean (e.g., "degrees", "points").
        _value (float): The calculated mean of the measurements.
        _measurements (list): A list of measurements (numerical values) to average.
    """
    type: Literal['MeanMetric'] = 'MeanMetric'

    def add_measurement(self, measurement: int) -> None:
        """
        Adds a measurement to the internal list of measurements.

        Args:
            measurement (float): A numerical value to be added to the list of measurements.
        """
        # Append the measurement to the internal list
        self.measurements.append(measurement)

    def calculate(self) -> float:
        """
        Calculate the mean of all added measurements.
        
        Returns:
            float: The mean of the measurements or None if no measurements have been added.
        """
        if not self.measurements:
            return None  # Return None if there are no measurements
        # Calculate the mean
        mean = sum(self.measurements) / len(self.measurements)
        # Update the metric's value
        self.update(mean)
        # Return the calculated mean
        return mean

```

```swarmauri/standard/metrics/concrete/ZeroMetric.py

from typing import Literal
from swarmauri.standard.metrics.base.MetricBase import MetricBase

class ZeroMetric(MetricBase):
    """
    A concrete implementation of MetricBase that statically represents the value 0.
    This can be used as a placeholder or default metric where dynamic calculation is not required.
    """
    unit: str = "unitless"
    value: int = 0
    type: Literal['ZeroMetric'] = 'ZeroMetric'

    def __call__(self):
        """
        Overrides the value property to always return 0.
        """
        return self.value


```

```swarmauri/standard/metrics/concrete/FirstImpressionMetric.py

from typing import Any, Literal
from swarmauri.standard.metrics.base.MetricBase import MetricBase

class FirstImpressionMetric(MetricBase):
    """
    Metric for capturing the first impression score from a set of scores.
    """
    type: Literal['FirstImpressionMetric'] = 'FirstImpressionMetric'
    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value


```

```swarmauri/standard/metrics/concrete/StaticMetric.py

from typing import Any, Literal
from swarmauri.standard.metrics.base.MetricBase import MetricBase

class StaticMetric(MetricBase):
    """
    Metric for capturing the first impression score from a set of scores.
    """
    type: Literal['StaticMetric'] = 'StaticMetric'

    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value


```

```swarmauri/standard/agent_factories/__init__.py



```

```swarmauri/standard/agent_factories/base/__init__.py



```

```swarmauri/standard/agent_factories/concrete/AgentFactory.py

import json
from datetime import datetime
from typing import Callable, Dict, Any
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.agentfactories.IAgentFactory import IAgentFactory
from swarmauri.core.agentfactories.IExportConf import IExportConf

class AgentFactory(IAgentFactory, IExportConf):
    def __init__(self):
        """ Initializes the AgentFactory with an empty registry and metadata. """
        self._registry: Dict[str, Callable[..., IAgent]] = {}
        self._metadata = {
            'id': None,
            'name': 'DefaultAgentFactory',
            'type': 'Generic',
            'date_created': datetime.now(),
            'last_modified': datetime.now()
        }
    
    # Implementation of IAgentFactory methods
    def create_agent(self, agent_type: str, **kwargs) -> IAgent:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        constructor = self._registry[agent_type]
        return constructor(**kwargs)

    def register_agent(self, agent_type: str, constructor: Callable[..., IAgent]) -> None:
        if agent_type in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is already registered.")
        self._registry[agent_type] = constructor
        self._metadata['last_modified'] = datetime.now()
    
    # Implementation of IExportConf methods
    def to_dict(self) -> Dict[str, Any]:
        """Exports the registry metadata as a dictionary."""
        export_data = self._metadata.copy()
        export_data['registry'] = list(self._registry.keys())
        return export_data

    def to_json(self) -> str:
        """Exports the registry metadata as a JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        """Exports the registry metadata to a file."""
        with open(file_path, 'w') as f:
            f.write(self.to_json())
    
    @property
    def id(self) -> int:
        return self._metadata['id']

    @id.setter
    def id(self, value: int) -> None:
        self._metadata['id'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def name(self) -> str:
        return self._metadata['name']

    @name.setter
    def name(self, value: str) -> None:
        self._metadata['name'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def type(self) -> str:
        return self._metadata['type']

    @type.setter
    def type(self, value: str) -> None:
        self._metadata['type'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def date_created(self) -> datetime:
        return self._metadata['date_created']

    @property
    def last_modified(self) -> datetime:
        return self._metadata['last_modified']

    @last_modified.setter
    def last_modified(self, value: datetime) -> None:
        self._metadata['last_modified'] = value

```

```swarmauri/standard/agent_factories/concrete/ConfDrivenAgentFactory.py

import json
import importlib
from datetime import datetime
from typing import Any, Dict, Callable
from swarmauri.core.agents.IAgent import IAgent  # Replace with the correct IAgent path
from swarmauri.core.agentfactories.IAgentFactory import IAgentFactory
from swarmauri.core.agentfactories.IExportConf import IExportConf


class ConfDrivenAgentFactory(IAgentFactory, IExportConf):
    def __init__(self, config_path: str):
        self._config_path = config_path
        self._config = self._load_config(config_path)
        self._registry = {}
        self._metadata = {
            'id': None,
            'name': 'ConfAgentFactory',
            'type': 'Configurable',
            'date_created': datetime.now(),
            'last_modified': datetime.now()
        }
        
        self._initialize_registry()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as file:
            return json.load(file)
    
    def _initialize_registry(self) -> None:
        for agent_type, agent_info in self._config.get("agents", {}).items():
            module_name, class_name = agent_info["class_path"].rsplit('.', 1)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            self.register_agent(agent_type, cls)
    
    # Implementation of IAgentFactory methods
    def create_agent(self, agent_type: str, **kwargs) -> IAgent:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        return self._registry[agent_type](**kwargs)

    def register_agent(self, agent_type: str, constructor: Callable[..., IAgent]) -> None:
        self._registry[agent_type] = constructor
        self._metadata['last_modified'] = datetime.now()
    
    # Implementation of IExportConf methods
    def to_dict(self) -> Dict[str, Any]:
        return self._metadata.copy()

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        with open(file_path, 'w') as f:
            f.write(self.to_json())

    # Additional methods to implement required properties and their setters
    # Implementing getters and setters for metadata properties as needed
    @property
    def id(self) -> int:
        return self._metadata['id']

    @id.setter
    def id(self, value: int) -> None:
        self._metadata['id'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def name(self) -> str:
        return self._metadata['name']

    @name.setter
    def name(self, value: str) -> None:
        self._metadata['name'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def type(self) -> str:
        return self._metadata['type']

    @type.setter
    def type(self, value: str) -> None:
        self._metadata['type'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def date_created(self) -> datetime:
        return self._metadata['date_created']

    @property
    def last_modified(self) -> datetime:
        return self._metadata['last_modified']

    @last_modified.setter
    def last_modified(self, value: datetime) -> None:
        self._metadata['last_modified'] = value

```

```swarmauri/standard/agent_factories/concrete/ReflectiveAgentFactory.py

import importlib
from datetime import datetime
import json
from typing import Callable, Dict, Type, Any
from swarmauri.core.agents.IAgent import IAgent  # Update this import path as needed
from swarmauri.core.agentfactories.IAgentFactory import IAgentFactory
from swarmauri.core.agentfactories.IExportConf import IExportConf

class ReflectiveAgentFactory(IAgentFactory, IExportConf):
    def __init__(self):
        self._registry: Dict[str, Type[IAgent]] = {}
        self._metadata = {
            'id': None,
            'name': 'ReflectiveAgentFactory',
            'type': 'Reflective',
            'date_created': datetime.now(),
            'last_modified': datetime.now()
        }

    def create_agent(self, agent_type: str, **kwargs) -> IAgent:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        agent_class = self._registry[agent_type]
        return agent_class(**kwargs)

    def register_agent(self, agent_type: str, class_path: str) -> None:
        module_name, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        self._registry[agent_type] = cls
        self._metadata['last_modified'] = datetime.now()

    # Implementations for the IExportConf interface
    def to_dict(self) -> Dict[str, Any]:
        return self._metadata.copy()

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        with open(file_path, 'w') as file:
            file.write(self.to_json())

    # Property implementations: id, name, type, date_created, and last_modified
    @property
    def id(self) -> int:
        return self._metadata['id']

    @id.setter
    def id(self, value: int) -> None:
        self._metadata['id'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def name(self) -> str:
        return self._metadata['name']

    @name.setter
    def name(self, value: str) -> None:
        self._metadata['name'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def type(self) -> str:
        return self._metadata['type']

    @type.setter
    def type(self, value: str) -> None:
        self._metadata['type'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def date_created(self) -> datetime:
        return self._metadata['date_created']

    @property
    def last_modified(self) -> datetime:
        return self._metadata['last_modified']

    @last_modified.setter
    def last_modified(self, value: datetime) -> None:
        self._metadata['last_modified'] = value

```

```swarmauri/standard/agent_factories/concrete/__init__.py



```

```swarmauri/standard/agent_factories/concrete/JsonAgentFactory.py

import json
from jsonschema import validate, ValidationError
from typing import Dict, Any, Callable, Type
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.agent_factories.IAgentFactory import IAgentFactory
from swarmauri.core.agent_factories.IExportConf import IExportConf
import importlib

class JsonAgentFactory:
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._registry: Dict[str, Type[Any]] = {}

        # Load and validate config
        self._validate_config()
        self._load_config()

    def _validate_config(self) -> None:
        """Validates the configuration against the JSON schema."""
        schema = {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "agents": {
                  "type": "object",
                  "patternProperties": {
                    "^[a-zA-Z][a-zA-Z0-9_-]*$": {
                      "type": "object",
                      "properties": {
                        "constructor": {
                          "type": "object",
                          "required": ["module", "class"]
                        }
                      },
                      "required": ["constructor"]
                    }
                  }
                }
              },
              "required": ["agents"]
            }

        try:
            validate(instance=self._config, schema=schema)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e.message}")

    def _load_config(self):
        """Loads configuration and registers agents accordingly."""
        agents_config = self._config.get("agents", {})
        for agent_type, agent_info in agents_config.items():
            module_name = agent_info["constructor"]["module"]
            class_name = agent_info["constructor"]["class"]

            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)

            self.register_agent(agent_type, cls)

    def create_agent(self, agent_type: str, **kwargs) -> Any:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        constructor = self._registry[agent_type]
        print(f"Creating instance of {constructor}, with args: {kwargs}")
        return constructor(**kwargs)

    def register_agent(self, agent_type: str, constructor: Callable[..., Any]) -> None:
        if agent_type in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is already registered.")
        
        print(f"Registering agent type '{agent_type}' with constructor: {constructor}")
        self._registry[agent_type] = constructor

    def to_dict(self) -> Dict[str, Any]:
        return self._config

    def to_json(self) -> str:
        return json.dumps(self._config, default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        with open(file_path, 'w') as file:
            file.write(self.to_json())

    @property
    def id(self) -> int:
        return self._config.get('id', None)  # Assuming config has an 'id'.

    @id.setter
    def id(self, value: int) -> None:
        self._config['id'] = value

    @property
    def name(self) -> str:
        return self._config.get('name', 'ConfDrivenAgentFactory')

    @name.setter
    def name(self, value: str) -> None:
        self._config['name'] = value

    @property
    def type(self) -> str:
        return self._config.get('type', 'Configuration-Driven')

    @type.setter
    def type(self, value: str) -> None:
        self._config['type'] = value

    @property
    def date_created(self) -> str:
        return self._config.get('date_created', None)

    @property
    def last_modified(self) -> str:
        return self._config.get('last_modified', None)

    @last_modified.setter
    def last_modified(self, value: str) -> None:
        self._config['last_modified'] = value
        self._config['last_modified'] = value

```

```swarmauri/standard/exceptions/__init__.py



```

```swarmauri/standard/exceptions/base/__init__.py



```

```swarmauri/standard/exceptions/concrete/IndexErrorWithContext.py

import inspect

class IndexErrorWithContext(Exception):
    def __init__(self, original_exception):
        self.original_exception = original_exception
        self.stack_info = inspect.stack()
        self.handle_error()

    def handle_error(self):
        # You might want to log this information or handle it differently depending on your application's needs
        frame = self.stack_info[1]  # Assuming the IndexError occurs one level up from where it's caught
        error_details = {
            "message": str(self.original_exception),
            "function": frame.function,
            "file": frame.filename,
            "line": frame.lineno,
            "code_context": ''.join(frame.code_context).strip() if frame.code_context else "No context available"
        }
        print("IndexError occurred with detailed context:")
        for key, value in error_details.items():
            print(f"{key.capitalize()}: {value}")

```

```swarmauri/standard/exceptions/concrete/__init__.py

from .IndexErrorWithContext import IndexErrorWithContext

```

```swarmauri/standard/schema_converters/__init__.py



```

```swarmauri/standard/schema_converters/base/SchemaConverterBase.py

from abc import abstractmethod
from typing import Optional, Dict, Any, Literal
from pydantic import ConfigDict, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.schema_converters.ISchemaConvert import ISchemaConvert
from swarmauri.core.tools.ITool import ITool

class SchemaConverterBase(ISchemaConvert, ComponentBase):
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.SCHEMA_CONVERTER.value, frozen=True)
    type: Literal['SchemaConverterBase'] = 'SchemaConverterBase'

    @abstractmethod
    def convert(self, tool: ITool) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the convert method.")


```

```swarmauri/standard/schema_converters/base/__init__.py



```

```swarmauri/standard/schema_converters/concrete/__init__.py



```

```swarmauri/standard/schema_converters/concrete/GroqSchemaConverter.py

from typing import  Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class GroqSchemaConverter(SchemaConverterBase):
    type: Literal['GroqSchemaConverter'] = 'GroqSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]['enum'] = param.enum

            if param.required:
                required.append(param.name)

        function = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                }
            }
        }
        if required:
            function['function']['parameters']['required'] = required

        return function


```

```swarmauri/standard/schema_converters/concrete/AnthropicSchemaConverter.py

from typing import  Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class AnthropicSchemaConverter(SchemaConverterBase):
    type: Literal['AnthropicSchemaConverter'] = 'AnthropicSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.required:
                required.append(param.name)

        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }


```

```swarmauri/standard/schema_converters/concrete/OpenAISchemaConverter.py

from typing import  Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class OpenAISchemaConverter(SchemaConverterBase):
    type: Literal['OpenAISchemaConverter'] = 'OpenAISchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]['enum'] = param.enum

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }

```

```swarmauri/standard/schema_converters/concrete/CohereSchemaConverter.py

from typing import Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class CohereSchemaConverter(SchemaConverterBase):
    type: Literal['CohereSchemaConverter'] = 'CohereSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}

        for param in tool.parameters:
            properties[param.name] = {
                "description": param.description,
                "required": param.required
            }
            if param.type == 'string':
                _type = 'str'
            elif param.type == 'float':
                _type = 'float'
            elif param.type == 'integer':
                _type = 'int'
            elif param.type == 'boolean':
                _type = 'bool'
            else:
                raise NotImplementedError(f'🚧 Support for missing type pending https://docs.cohere.com/docs/parameter-types-in-tool-use\n: Missing Type: {param.type}')
            properties[param.name].update({'type': _type})

        return {
            "name": tool.name,
            "description": tool.description,
            "parameter_definitions": properties
        }

```

```swarmauri/standard/schema_converters/concrete/MistralSchemaConverter.py

from typing import Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class MistralSchemaConverter(SchemaConverterBase):
    type: Literal['MistralSchemaConverter'] = 'MistralSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]['enum'] = param.enum

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }

```

```swarmauri/standard/schema_converters/concrete/GeminiSchemaConverter.py

from typing import Dict, Any, Literal
import google.generativeai as genai
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class GeminiSchemaConverter(SchemaConverterBase):
    type: Literal['GeminiSchemaConverter'] = 'GeminiSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> genai.protos.FunctionDeclaration:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = genai.protos.Schema(
                type=self.convert_type(param.type),
                description=param.description
            )
            if param.required:
                required.append(param.name)

        schema = genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties=properties,
            required=required
        )

        return genai.protos.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=schema
        )

    def convert_type(self, param_type: str) -> genai.protos.Type:
        type_mapping = {
            "string": genai.protos.Type.STRING,
            "str": genai.protos.Type.STRING,
            "integer": genai.protos.Type.INTEGER,
            "int": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "bool": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT
        }
        return type_mapping.get(param_type, genai.protos.Type.STRING)

```