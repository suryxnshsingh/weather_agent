#Chain of Thought prompting example
from openai import OpenAI
from dotenv import load_dotenv
import json
import requests

load_dotenv()

client = OpenAI()

def get_weather_info(city : str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.text.strip()
    else:
        return "Sorry, I couldn't fetch the weather information right now."

SYSTEM_PROMPT = """
You are an expert AI assistant in resolving user queries using chain of thought.
You work on START -> PLAN -> OUTPUT framework.
You need to first PLAN your approach to solve the problem in steps and then provide the final OUTPUT.
You can also call the tool from the list of available tools if needed.
For every tool call, wait for the observation before moving to the next step.

Rules:
-strictly follow this JSON output format.
-Only run one step at a time.
-The sequence of steps is START (user giving an input), PLAN (the model planning the steps to solve the problem), OUTPUT (the model providing the final answer).

Output JSON Format:{
"step": "START" or "PLAN" or "OUTPUT" or "OBSERVE" or "TOOL",
"output": "<output>" or null,
}

Available Tools:
1. get_weather_info(city: str) -> str : Fetches the current weather information for the specified city.

Example 1:
START: Heym Can you solve 2+ 3 * 5 /10
PLAN: {"step": "PLAN", "output": "To solve the expression 2 + 3 * 5 / 10, I will first perform the multiplication and division operations, and then add the result to 2."}
PLAN: {"step": "PLAN", "output": "The BODMAS rule states that multiplication and division should be performed before addition and subtraction."}
PLAN: {"step": "PLAN", "output": "First, I will divide 3 by 10 to get 0.3."}
PLAN: {"step": "PLAN", "output": "Next, I will multiply the result (0.3) by 5 to get 1.5."}
PLAN: {"step": "PLAN", "output": "Finally, I will add 2 to the result (1.5) to get the final answer, 3.5."}
PLAN: {"step": "PLAN", "output": "3.5 is the final solution."}
PLAN: {"step": "PLAN", "output": "Great, I have the solution."}
OUTPUT: {"step": "OUTPUT", "output": "The final answer is 3.5."}

Example 2:
START: What's the weather like in Indore?
PLAN: {"step": "PLAN", "output": "Seems like the user wants to know the current weather in Indore"}
PLAN: {"step": "PLAN", "output": "To provide the current weather information for Indore, Let find the list of available tools."}
PLAN: {"step": "PLAN", "output": "I have found a tool named get_weather_info which fetches the current weather information for a specified city."}
PLAN: {"step": "PLAN", "output": "I will use the tool get_weather_info to fetch the current weather information for Indore."}
PLAN: {"step": "PLAN", "output": "I will call the tool now."}
TOOL: {"step": "TOOL", "output": "get_weather_info('Indore')"}
OBSERVE: {"step": "OBSERVE", "output": "I have received the weather information for Indore from the tool."}
OUTPUT: {"step": "OUTPUT", "output": "The current weather in Indore is Partly cloudy 35°C."}

"""

message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

user_query = input("👉")
message_history.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=message_history
    )

    raw_output = (response.choices[0].message.content)
    parsed_response = json.loads(raw_output)

    raw_output = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": raw_output})

    parsed_response = json.loads(raw_output)

    if parsed_response.get("step") == "START":
        print(f"💡 {parsed_response.get('output')}")
        continue
    elif parsed_response.get("step") == "PLAN":
        print(f"🧠 {parsed_response.get('output')}")
        continue
    elif parsed_response.get("step") == "TOOL":
        tool_call = parsed_response.get("output")
        if "get_weather_info" in tool_call:
            city_start = tool_call.find("('") + 2
            city_end = tool_call.find("')", city_start)
            city = tool_call[city_start:city_end]
            observation = get_weather_info(city)
            print(f"🛠️ Calling tool get_weather_info with argument: {city}")
            message_history.append({"role": "user", "content": f"Observation: {observation}"})
        continue
    elif parsed_response.get("step") == "OUTPUT":
        print(f"✅ {parsed_response.get('output')}")
        break


    print("\n\n\n\n")