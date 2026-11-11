"""Checkpoint 2 (slide 13): give the agent a tool. Run from the code folder:
    python checkpoints/02_add_a_tool.py

The model decides whether to call the tool, so tasks.json may take a few runs.
"""
import json
import os
from pathlib import Path

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

llm = LLM(model=os.getenv("WORKSHOP_MODEL", "ollama/llama3.1"),
          base_url="http://localhost:11434")


@tool("save_tasks", max_usage_count=1)
def save_tasks(tasks_json: str) -> str:
    "Save a JSON list of task titles to tasks.json."
    data = json.loads(tasks_json)
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return f"saved {len(data)} tasks"


planner = Agent(
    role="Project Planner",
    goal="Turn a project brief into a short task list and save it",
    backstory="A sharp PM who makes vague briefs actionable.",
    llm=llm, verbose=True,
    tools=[save_tasks],   # the agent may now decide to call this tool
)

task = Task(
    description="List 3 to 5 task titles for this brief, then save them with the "
                "save_tasks tool as a JSON list of strings:\n{brief}",
    expected_output="One sentence confirming how many tasks were saved",
    agent=planner,
)

Path("tasks.json").unlink(missing_ok=True)   # start clean, so the check below is honest
crew = Crew(agents=[planner], tasks=[task], process=Process.sequential)
print(crew.kickoff(inputs={"brief": open("brief.md", encoding="utf-8").read()}))
print("tasks.json written:", Path("tasks.json").exists())
