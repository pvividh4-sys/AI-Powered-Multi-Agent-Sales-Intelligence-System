import pandas as pd

from agents.planner_agent import PlannerAgent


df = pd.read_csv("data/sample/Retail Sales Dataset.csv")

agent = PlannerAgent()

result = agent.run(df)

print("\n===== PLANNER AGENT =====")

print("\nStatus:")
print(result["status"])

print("\nSemantic Mapping:")

for key, value in result["semantic_mapping"].items():
    print(
        key,
        "→",
        value["column"],
        "| confidence:",
        value["confidence"]
    )

print("\nCapabilities:")

for key, value in result["capabilities"].items():
    print(key, ":", value)

print("\nForecasting:")
print(result["forecasting_eligibility"])