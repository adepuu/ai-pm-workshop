"""
Tools are plain Python functions the agent may choose to call.

One agent, one tool. CrewAI shows the model the tool's name and description; the
model decides whether to call it. Run this a few times: the choice is the model's,
which is why pm_crew.py saves its state from Python instead of relying on a tool.

Run:
    python tool_demo.py
"""
import json
import os
from pathlib import Path

from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

MODEL = os.getenv("WORKSHOP_MODEL", "ollama/llama3.1")
llm = LLM(model=MODEL, base_url="http://localhost:11434")


@tool("save_tasks", max_usage_count=1)
def save_tasks(tasks_json: str) -> str:
    """Save a JSON list of task titles to tasks.json. Call this once, with the full list."""
    data = json.loads(tasks_json)
    Path("tasks.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return f"saved {len(data)} tasks"


planner = Agent(
    role="Project Planner",
    goal="Turn a project brief into a short task list and save it",
    backstory="A sharp PM who makes vague briefs actionable.",
    llm=llm,
    tools=[save_tasks],
    verbose=True,
)

task = Task(
    description=(
        "List 3 to 5 task titles for this brief, then save them with the save_tasks "
        "tool as a JSON list of strings:\n{brief}"
    ),
    expected_output="One sentence confirming how many tasks were saved",
    agent=planner,
)

if __name__ == "__main__":
    Path("tasks.json").unlink(missing_ok=True)   # start clean, so the check below is honest
    brief = Path("brief.md").read_text(encoding="utf-8")
    print(Crew(agents=[planner], tasks=[task]).kickoff(inputs={"brief": brief}))
    print("tasks.json written:", Path("tasks.json").exists())
