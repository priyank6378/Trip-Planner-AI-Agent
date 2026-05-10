from groq import Groq
import rich
import json
from mcp_client import MyMCPClient
import asyncio


class TripPlannerAgent():
    chat_history = []
    console = rich.console.Console()

    def __init__(self):
        with open("skills.md", "r") as f:
            self.skills = f.read()
        
        self.model_name = "openai/gpt-oss-120b"
        self.client = Groq()    

        self.mcp_client = MyMCPClient()
        self.tools_list = asyncio.run(self.mcp_client.list_tools()).tools
        self.tools_list = self.parse_tools_list_for_model(self.tools_list)

        self.system_prompt = self.skills 
        self.chat_history.append({"role": "system", "content": self.system_prompt})

    def parse_tools_list_for_model(self, tools_list):
        tools = []
        for tool in tools_list:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })

        return tools

    def summarize_single_response(self, user_input):
        final_response = ""
        parts = 10
        if len(user_input) > 20000:
            for i in range(10):
                part_input = user_input[i*len(user_input)//parts:(i+1)*len(user_input)//parts]
                part_response = self.client.chat.completions.create(
                                    model=self.model_name,
                                    messages=[{"role": "user", "content": f"{part_input} \n\n\nSummarize the above user query (if it is big) in max 5 lines."}],
                                    temperature=1,
                                )
                final_response += part_response.choices[0].message.content + "\n"
        
        else :
            final_response = user_input

        final_response_summary = self.client.chat.completions.create(
                                model=self.model_name,
                                messages=[{"role": "user", "content": f"{final_response} \n\n\nSummarize the above summary in max 5 lines."}],
                                temperature=1,
                            )
        return final_response_summary.choices[0].message.content


    def generate_response(self):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.chat_history,
            temperature=1,
            tools=self.tools_list,
            tool_choice="auto"
        )

        return response.choices[0].message


    def agentic_loop(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})       
        
        with rich.console.Console().status("[bold green]Agent is thinking...[/bold green]", spinner="dots"):
            while True:
                response = self.generate_response()
                tool_calls = response.tool_calls
                if tool_calls:
                    self.chat_history.append({
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            } for tc in tool_calls
                        ]
                    })
                    self.console.print(f"[yellow]Calling tools...[/yellow]", emoji="🔧")
                    for tool_call in tool_calls:
                        self.console.print(f"[yellow]Tool to call:[/yellow] {tool_call.function.name}", emoji="🔧")
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        tool_call_response = str(asyncio.run(self.mcp_client.call_tool(function_name, arguments)).content)
                        tool_call_response_summary = self.summarize_single_response(f"{tool_call_response}")
                        self.chat_history.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": tool_call_response_summary
                        })
                else:
                    self.chat_history.append({"role": "assistant", "content": response.content})
                    break

        return response.content
    
    def get_tool_name_and_parameters(self, response):
        pass
    
    def tool_execution(self, tool_call_details):
        tool_name = tool_call_details.get("tool_name")
        parameters = tool_call_details.get("parameters", {}) 
        tool_to_call = self.tools_mapping.get(tool_name, None)
        if tool_to_call:
            tool_response = tool_to_call(**parameters)
            self.chat_history.append({"role": "user", "content": f"Tool {tool_name} responded with: {tool_response}"})
        else:
            self.chat_history.append({"role": "user", "content": f"Tool {tool_name} not found."})

    def chat_loop(self):

        self.console.print("Welcome to the Trip Planner Agent! Type 'q' to quit.")
        while True:
            user_input = self.console.input("[bold green]You:[/bold green] ", emoji="👤")
            if user_input.lower() == "q":
                break
            response = self.agentic_loop(user_input)
            self.console.print(f"[bold blue]Agent:[/bold blue] {response}", emoji="🤖")
