from openai import OpenAI
from dotenv import load_dotenv
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


def main():
    user_query = input("Enter your weather-related question: ")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": user_query},
        ]
    )

    print(f"{response.choices[0].message.content}")

# main()
print(get_weather_info("Goa"))