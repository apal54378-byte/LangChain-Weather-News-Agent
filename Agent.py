import sys

import tools

missing = tools.missing_keys()

if missing:
    raise SystemExit("ERROR: missing key(s) in .env: " + ", ".join(missing))

MENU = {
    "1": ("news only", "get_city_news"),
    "news": ("news only", "get_city_news"),
    "2": ("temperature only", "get_weather"),
    "temperature": ("temperature only", "get_weather"),
    "temp": ("temperature only", "get_weather"),
    "3": ("both news and temperature", "get_weather and get_city_news"),
    "both": ("both news and temperature", "get_weather and get_city_news"),
}

print("=" * 60)
print("What would you like to know?")
print("1. News")
print("2. Temperature")
print("3. Both")
print("=" * 60)

choice = input("Enter your choice: ").lower().strip()

if choice not in MENU:
    raise SystemExit("Invalid choice.")

request_type, tools_hint = MENU[choice]

city = input(
    f"\nEnter city name (e.g. {', '.join(tools.SUGGESTED_CITIES[:3])}): "
).strip()

if not city:
    raise SystemExit("City name cannot be empty.")

agent = tools.build_agent(temperature=0.0)

instruction = (
    f"I want {request_type} for the city {city}.\n"
    f"Use only these tools: {tools_hint}.\n"
    f"Do not call any other tool."
)

print("\nFiling request...\n")

result = agent.invoke(
    {"messages": [{"role": "user", "content": instruction}]},
    {"recursion_limit": 25},
)

answer = result["messages"][-1]

for message in result["messages"]:
    for call in getattr(message, "tool_calls", None) or []:
        print(f"  wire call: {call['name']}({call.get('args', {})})")

print("\n" + "=" * 60)
print("FINAL RESULT")
print("=" * 60)
print(answer.content)
print("=" * 60)

sys.exit(0)
