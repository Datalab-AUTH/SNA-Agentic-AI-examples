"""
Example 09 - Testing agents without an LLM
=========================================

Real LLM calls are slow, cost resources and give a different answer every
time - bad for automated tests. Pydantic AI lets you swap the real model for
a fake one with `agent.override(model=...)`:

  TestModel      calls your tools with made-up arguments and returns made-up
                 (but schema-valid) output. Great for "does it run at all?".
  FunctionModel  YOU write the model's behaviour as a Python function.
                 Great for testing one exact scenario.

Run from the repository root:
    pytest 09_testing -v
"""

from pydantic_ai import ModelMessage, ModelResponse, RetryPromptPart, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel

from course_agent import StudentProfile, advisor_agent, find_course

MARIA = StudentProfile(name="Maria", completed_courses=["DWS101", "DWS105"])


def tool_calls(messages: list[ModelMessage]) -> list[str]:
    """The names of the tools the 'LLM' called, in order."""
    return [part.tool_name for message in messages for part in message.parts if isinstance(part, ToolCallPart)]


# 1. Tools are plain Python functions: test them like any other function. No LLM needed.
def test_find_course():
    assert find_course("dws105")["title"] == "Social Network Analysis"
    assert find_course("NOPE") is None


# 2. TestModel: a quick smoke test of the whole agent (instructions, deps, tools).
def test_agent_runs_with_test_model():
    with advisor_agent.override(model=TestModel(call_tools=["my_completed_courses"])):
        result = advisor_agent.run_sync("Which courses have I completed?", deps=MARIA)

    assert tool_calls(result.all_messages()) == ["my_completed_courses"]
    # The tool used the deps we passed in:
    tool_return = next(
        part for message in result.all_messages() for part in message.parts if isinstance(part, ToolReturnPart)
    )
    assert [course["code"] for course in tool_return.content] == ["DWS101", "DWS105"]


# 3. FunctionModel: script exactly what the "LLM" does, step by step.
def scripted_llm(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    last_part = messages[-1].parts[-1]
    if isinstance(last_part, ToolReturnPart):
        # Second step: the tool answered, now give the final answer.
        return ModelResponse(parts=[TextPart(f"DWS105 is {last_part.content['title']}.")])
    # First step: call the tool.
    return ModelResponse(parts=[ToolCallPart("course_details", {"code": "DWS105"})])


def test_agent_answers_from_tool_result():
    with advisor_agent.override(model=FunctionModel(scripted_llm)):
        result = advisor_agent.run_sync("What is DWS105?", deps=MARIA)

    assert result.output == "DWS105 is Social Network Analysis."


# 4. FunctionModel again: check that a wrong course code makes the tool ask for a retry.
def llm_that_makes_a_mistake(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    last_part = messages[-1].parts[-1]
    if isinstance(last_part, RetryPromptPart):
        # The tool said "there is no such course" -> try again with a correct code.
        return ModelResponse(parts=[ToolCallPart("course_details", {"code": "DWS105"})])
    if isinstance(last_part, ToolReturnPart):
        return ModelResponse(parts=[TextPart(last_part.content["title"])])
    return ModelResponse(parts=[ToolCallPart("course_details", {"code": "SNA101"})])  # wrong code


def test_wrong_course_code_is_retried():
    with advisor_agent.override(model=FunctionModel(llm_that_makes_a_mistake)):
        result = advisor_agent.run_sync("Tell me about the SNA course.", deps=MARIA)

    assert tool_calls(result.all_messages()) == ["course_details", "course_details"]
    retry = next(
        part for message in result.all_messages() for part in message.parts if isinstance(part, RetryPromptPart)
    )
    assert "There is no course 'SNA101'" in retry.model_response()
    assert result.output == "Social Network Analysis"


# 5. Dynamic instructions use the deps.
def test_instructions_mention_the_student():
    with advisor_agent.override(model=TestModel(call_tools=[])):
        result = advisor_agent.run_sync("Hello", deps=MARIA)

    first_request = result.all_messages()[0]
    assert "The student's name is Maria." in first_request.instructions
