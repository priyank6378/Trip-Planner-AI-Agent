from groq import Groq
from tools import get_weather_details, get_tools_list, get_tools_mapping
import rich
import json


class TripPlannerAgent():
    chat_history = []
    console = rich.console.Console()

    def __init__(self):
        with open("skills.md", "r") as f:
            self.skills = f.read()
        
        self.tools_details = get_tools_list()
        self.tools_mapping = get_tools_mapping()

        self.skills = self.skills.replace("<tools_list_details_agent_have_access_to>", "\n".join([f"- {name}: {details}" for name, details in self.tools_details.items()]))
        self.system_prompt = self.skills 

        self.chat_history.append({"role": "system", "content": self.system_prompt})

        self.client = Groq()    
        

    def generate_response(self):
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=self.chat_history,
            temperature=1,
            top_p=1,
            stop=None
        )

        self.chat_history.append({"role": "assistant", "content": response.choices[0].message.content})
        return response.choices[0].message.content


    def agentic_loop(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})       
        
        with rich.console.Console().status("[bold green]Agent is thinking...[/bold green]", spinner="dots"):
            while True:
                response = self.generate_response()
                self.console.print(response)
                if "tool_name" in response:
                    self.console.print("[bold yellow]Agent is calling a tool...[/bold yellow]")
                    self.console.print(f"[bold yellow]Tool call details:[/bold yellow] {response}")
                    tool_call_details = json.loads(response)
                    self.tool_execution(tool_call_details)
                else:
                    break

        return response
    
    def tool_execution(self, tool_call_details):
        tool_name = tool_call_details.get("tool_name")
        parameters = tool_call_details.get("parameters", {}) 
        tool_to_call = self.tools_mapping.get(tool_name, None)
        if tool_to_call:
            tool_response = tool_to_call(**parameters)
            self.chat_history.append({"role": "tool", "content": f"Tool {tool_name} responded with: {tool_response}", "tool_call_id": tool_call_details.get("tool_call_id")})
        else:
            self.chat_history.append({"role": "tool", "content": f"Tool {tool_name} not found."})

    def chat_loop(self):

        self.console.print("Welcome to the Trip Planner Agent! Type 'q' to quit.")
        while True:
            user_input = self.console.input("[bold green]You:[/bold green] ")
            if user_input.lower() == "q":
                break
            response = self.agentic_loop(user_input)
            self.console.print(f"[bold blue]Agent:[/bold blue] {response}")
