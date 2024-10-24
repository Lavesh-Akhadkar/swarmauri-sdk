import logging

import pytest
import os
from dotenv import load_dotenv
from swarmauri.llms.concrete.MistralToolModel import MistralToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete import HumanMessage
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")


@pytest.fixture(scope="module")
def mistral_tool_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.fixture(scope="module")
def toolkit():
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    return toolkit


@pytest.fixture(scope="module")
def conversation():
    conversation = Conversation()

    input_data = "Add 512+671"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    return conversation


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)
    return llm.allowed_models


@pytest.mark.unit
def test_ubc_resource(mistral_tool_model):
    assert mistral_tool_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(mistral_tool_model):
    assert mistral_tool_model.type == "MistralToolModel"


@pytest.mark.unit
def test_serialization(mistral_tool_model):
    assert (
        mistral_tool_model.id
        == LLM.model_validate_json(mistral_tool_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(mistral_tool_model):
    assert mistral_tool_model.name == "open-mixtral-8x22b"


@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_agent_exec(mistral_tool_model, toolkit, model_name):
    mistral_tool_model.name = model_name
    conversation = Conversation()

    # Use mistral_tool_model from the fixture
    agent = ToolAgent(
        llm=mistral_tool_model, conversation=conversation, toolkit=toolkit
    )
    result = agent.exec("Add 512+671")
    assert type(result) == str


@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_predict(mistral_tool_model, toolkit, conversation, model_name):
    mistral_tool_model.name = model_name

    conversation = mistral_tool_model.predict(
        conversation=conversation, toolkit=toolkit
    )
    logging.info(conversation.get_last().content)

    assert type(conversation.get_last().content) == str


@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_stream(mistral_tool_model, toolkit, conversation, model_name):
    mistral_tool_model.name = model_name

    collected_tokens = []
    for token in mistral_tool_model.stream(conversation=conversation, toolkit=toolkit):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_batch(mistral_tool_model, toolkit, model_name):
    mistral_tool_model.name = model_name

    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = mistral_tool_model.batch(conversations=conversations, toolkit=toolkit)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)


@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_apredict(mistral_tool_model, toolkit, conversation, model_name):
    mistral_tool_model.name = model_name

    result = await mistral_tool_model.apredict(
        conversation=conversation, toolkit=toolkit
    )
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_astream(mistral_tool_model, toolkit, conversation, model_name):
    mistral_tool_model.name = model_name

    collected_tokens = []
    async for token in mistral_tool_model.astream(
        conversation=conversation, toolkit=toolkit
    ):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_abatch(mistral_tool_model, toolkit, model_name):
    mistral_tool_model.name = model_name

    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await mistral_tool_model.abatch(
        conversations=conversations, toolkit=toolkit
    )
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
