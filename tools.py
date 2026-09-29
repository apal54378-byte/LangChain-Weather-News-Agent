import os
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain.agents import create_agent

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

SUGGESTED_CITIES = ["Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai"]

SYSTEM_PROMPT = (
    "You are a concise field correspondent. You report on a city's current "
    "conditions and recent news. Always call the relevant tool before "
    "answering a factual question, never guess, and keep answers short and "
    "plain-spoken. Do not use emojis or markdown headers."
)


def missing_keys() -> list[str]:
    names = {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY,
        "TAVILY_API_KEY": TAVILY_API_KEY,
    }
    return [name for name, value in names.items() if not value]


def _tavily() -> TavilyClient:
    return TavilyClient(api_key=TAVILY_API_KEY)


@tool
def get_weather(city: str) -> str:
    """
    Get the current temperature, weather condition, humidity, wind speed,
    date and local time of a city.
    """

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as error:
        return f"Weather API error for {city}: {error}"

    if response.status_code != 200:
        return f"Weather information not found for {city}."

    try:
        data = response.json()
    except ValueError:
        return f"Weather API returned a malformed response for {city}."

    main = data.get("main", {})
    weather = data.get("weather") or [{}]
    condition = weather[0].get("description", "unknown")
    local_time = datetime.now(
        timezone(timedelta(seconds=data.get("timezone", 0)))
    )

    return (
        f"Weather Information\n"
        f"City        : {data.get('name', city)}, "
        f"{data.get('sys', {}).get('country', '')}\n"
        f"Date        : {local_time.strftime('%d %B %Y')}\n"
        f"Local Time  : {local_time.strftime('%I:%M:%S %p')}\n"
        f"Temperature : {main.get('temp', 'n/a')} C\n"
        f"Feels Like  : {main.get('feels_like', 'n/a')} C\n"
        f"Condition   : {condition}\n"
        f"Humidity    : {main.get('humidity', 'n/a')}%\n"
        f"Wind Speed  : {data.get('wind', {}).get('speed', 'n/a')} m/s"
    )


@tool
def get_city_news(city: str) -> str:
    """
    Get the 5 latest news articles related to a city.
    """

    try:
        response = _tavily().search(
            query=f"latest news about {city}",
            topic="news",
            search_depth="advanced",
            max_results=5,
        )
    except Exception as error:
        return f"News API error for {city}: {error}"

    results = response.get("results", [])

    if not results:
        return f"No recent news found for {city}."

    news = f"Latest News about {city}\n\n"

    for index, article in enumerate(results[:5], start=1):
        news += (
            f"{index}. {article.get('title', 'No title')}\n"
            f"   Published: {article.get('published_date', 'Date not available')}\n"
            f"   URL: {article.get('url', 'No URL')}\n\n"
        )

    return news


TOOLS = [get_weather, get_city_news]


def build_agent(temperature: float = 0.0):
    return create_agent(
        model=ChatGroq(model="openai/gpt-oss-20b", temperature=temperature),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )
