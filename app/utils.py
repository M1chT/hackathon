from typing import Callable
from langchain_core.tools import BaseTool, tool as create_tool
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt
from langgraph.prebuilt.interrupt import HumanInterruptConfig, HumanInterrupt

def add_human_in_the_loop(
    tool: Callable | BaseTool,
    *,
    interrupt_config: HumanInterruptConfig = None,
) -> BaseTool:
    if not isinstance(tool, BaseTool):
        tool = create_tool(tool)

    if interrupt_config is None:
        interrupt_config = {
            "allow_accept": True,
            "allow_edit": True,
            "allow_reject": True,
        }

    @create_tool(
        tool.name,
        description=tool.description,
        args_schema=tool.args_schema
    )
    async def call_tool_with_interrupt(config: RunnableConfig, **tool_input):
        request: HumanInterrupt = {
            "action_request": {
                "action": tool.name,
                "args": tool_input
            },
            "config": interrupt_config,
            "description": "Please review the tool call"
        }
        # print("Interrupt requested:", request)  
        responses = interrupt([request])
        response = responses[0]
        print("res", response)
        # print("Interrupt response:", response)
        if response["type"] == "accept":
            tool_response = await tool.ainvoke(tool_input, config)
        elif response["type"] == "edit":
            tool_input = response["args"]
            tool_response = await tool.ainvoke(tool_input, config)
        elif response["type"] == "reject":
            tool_response = f"Tool: '{tool.name}' was not executed because the user rejected the action to call the tool."
        else:
            raise ValueError(f"Unsupported interrupt response type: {response['type']}")
        return tool_response

    return call_tool_with_interrupt