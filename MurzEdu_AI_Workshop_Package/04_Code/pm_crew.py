"""
Build Your AI Project Manager — a minimal CrewAI + Ollama PM assistant.

A sequential crew of three specialists:
    Planner  ->  Risk Analyst  ->  Status Writer

Run:
    ollama pull llama3.1          # once
    pip install -r requirements.txt
    python pm_crew.py --brief brief.md

Everything runs locally through Ollama — no API keys, no data leaving the machine.
Note: CrewAI's API evolves; pin versions (see requirements.txt) for a reproducible run.
"""
import argparse
import json
from pathlib import Path
from typing import List

from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

# --- the local model, served by Ollama -------------------------------------
llm = LLM(model="ollama/llama3.1", base_url="http://localhost:11434")


# --- typed output: the planner returns structured data, not prose ----------
class TaskItem(BaseModel):
    title: str
    owner: str
    estimate_days: int


class Plan(BaseModel):
    tasks: List[TaskItem]


# --- a tool is just a Python function the agent may choose to call ----------
@tool("save_tasks")
def save_tasks(tasks_json: str) -> str:
    """Save a JSON task list to project_state.json."""
    data = json.loads(tasks_json)
    Path("project_state.json").write_text(json.dumps(data, indent=2))
    return f"saved {len(data)} tasks"


# --- three specialists, each with one job ----------------------------------
planner = Agent(
    role="Project Planner",
    goal="Turn a project brief into a clear, ordered task list",
    backstory="A sharp PM who makes vague briefs actionable.",
    llm=llm,
    tools=[save_tasks],
    verbose=True,
)

risk = Agent(
    role="Risk Analyst",
    goal="Flag the top risks, each with one mitigation",
    backstory="A cautious PM who has watched projects slip.",
    llm=llm,
    verbose=True,
)

writer = Agent(
    role="Status Writer",
    goal="Draft a short, calm status update for stakeholders",
    backstory="Writes clear, honest updates.",
    llm=llm,
    verbose=True,
)


def build_crew() -> Crew:
    plan_task = Task(
        description="Break this brief into tasks, each with an owner and a day estimate:\n{brief}",
        expected_output="A Plan object (title, owner, estimate_days per task)",
        agent=planner,
        output_pydantic=Plan,
    )
    risk_task = Task(
        description="Review the plan and list the top 3 risks, each with one mitigation.",
        expected_output="A short risk register",
        agent=risk,
        context=[plan_task],      # pass the plan forward
    )
    status_task = Task(
        description="Write a 5-line status update for stakeholders from the plan and risks.",
        expected_output="A 5-line status update",
        agent=writer,
        context=[plan_task, risk_task],
    )
    return Crew(
        agents=[planner, risk, writer],
        tasks=[plan_task, risk_task, status_task],
        process=Process.sequential,
        verbose=True,
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", default="brief.md", help="path to a project brief")
    args = ap.parse_args()

    brief = Path(args.brief).read_text()
    result = build_crew().kickoff(inputs={"brief": brief})

    print("\n=== RESULT ===\n")
    print(result)
    print("\n(tasks also written to project_state.json)")
