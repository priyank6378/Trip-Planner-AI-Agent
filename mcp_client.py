import asyncio
import sys 
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters


class MyMCPClient(): 
    def __init__(self):
        self.server_parameters = StdioServerParameters(
            command=sys.executable,
            args=["mcp_server.py"],
        )

    async def list_tools(self):
        async with stdio_client(self.server_parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return result
            
    async def call_tool(self, tool_name: str, arguments: dict):
        async with stdio_client(self.server_parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result
            

if __name__ == "__main__":
    client = MyMCPClient()
    # tools = asyncio.run(client.list_tools())
    # print("Available tools:", tools)
    # print(type(tools.tools))

    tool_response = asyncio.run(client.call_tool("get_weather_details", {"location": "Pune", "days": 2}))
    print(len(str(tool_response.content)))