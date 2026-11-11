"""
Build Your AI Project Manager — a minimal CrewAI + Ollama PM assistant.

A sequential crew of three specialists:
    Planner  ->  Risk Analyst  ->  Status Writer

Run:
    ollama pull llama3.1          # once
    pip install -r requirements.txt
    python pm_crew.py --brief brief.md

Weak laptop, or a different model tag?
    WORKSHOP_MODEL=ollama/llama3.2:3b python pm_crew.py --brief brief.md

Everything runs locally through Ollama — no API keys, no data leaving the machine.
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, List

from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process, LLM, TaskOutput

# --- the local model, served by Ollama -------------------------------------
MODEL = os.getenv("WORKSHOP_MODEL", "ollama/llama3.1")
llm = LLM(model=MODEL, base_url="http://localhost:11434")


# --- typed output: the planner returns structured data, not prose ----------
class TaskItem(BaseModel):
    title: str
    owner: str
    estimate_days: int


class Plan(BaseModel):
    tasks: List[TaskItem]


# --- a guardrail: Python validates the output; failures go back to the agent --
def short_update(output: TaskOutput) -> tuple[bool, Any]:
    words = len(output.raw.split())
    if words > 120:
        return (False, f"Too long ({words} words). Keep the update under 120 words.")
    return (True, output.raw)


# --- three specialists, each with one job ----------------------------------
planner = Agent(
    role="Project Planner",
    goal="Turn a project brief into a clear, ordered task list",
    backstory="A sharp PM who makes vague briefs actionable.",
    llm=llm,
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
    backstory="Writes clear, honest updates and never invents facts.",
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
        description=(
            "Write a kickoff status update for stakeholders from the plan and risks. "
            "Work has NOT started yet: do not claim any progress or completed work."
        ),
        expected_output="A status update of at most 5 lines and under 120 words",
        agent=writer,
        context=[plan_task, risk_task],
        guardrail=short_update,
        guardrail_max_retries=2,
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

    brief = Path(args.brief).read_text(encoding="utf-8")
    result = build_crew().kickoff(inputs={"brief": brief})

    # Shared state is written by Python from the validated Plan, so it can't be
    # skipped by the model. Saving is too important to leave to the model's choice.
    plan_out, risk_out, status_out = result.tasks_output
    if plan_out.pydantic is None:
        sys.exit("The planner did not return a valid Plan; project_state.json was not written.")

    state = {
        "tasks": [t.model_dump() for t in plan_out.pydantic.tasks],
        "risks": risk_out.raw,
        "status_update": status_out.raw,
    }
    Path("project_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    print("\n=== RESULT ===\n")
    print(f"{len(state['tasks'])} tasks planned\n")
    print(state["risks"], "\n")
    print(state["status_update"])
    print("\n(saved to project_state.json)")
