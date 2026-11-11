"""Checkpoint 4 (slides 16-17): three specialists in one crew. Run from the code folder:
    python checkpoints/04_full_crew.py

pm_crew.py is this file plus a guardrail and a fuller saved state.
"""
import os
from pathlib import Path
from typing import List

from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process, LLM

llm = LLM(model=os.getenv("WORKSHOP_MODEL", "ollama/llama3.1"),
          base_url="http://localhost:11434")


class TaskItem(BaseModel):
    title: str
    owner: str
    estimate_days: int


class Plan(BaseModel):
    tasks: List[TaskItem]


planner = Agent(
    role="Project Planner",
    goal="Turn a project brief into a clear task list",
    backstory="A sharp PM who makes vague briefs actionable.",
    llm=llm, verbose=True,
)

risk = Agent(
    role="Risk Analyst",
    goal="Flag the top risks, with one mitigation each",
    backstory="A cautious PM who has watched projects slip.",
    llm=llm)

writer = Agent(
    role="Status Writer",
    goal="Draft a short status update for stakeholders",
    backstory="Writes clear, calm updates and never invents facts.",
    llm=llm)

plan_task = Task(
    description="Break the brief into tasks:\n{brief}",
    expected_output="A Plan object",
    agent=planner,
    output_pydantic=Plan,
)

risk_task = Task(description="Review the plan. List the top risks.",
                 expected_output="A risk register", agent=risk,
                 context=[plan_task])

status_task = Task(description="Write a kickoff update. Work has NOT started: claim no progress.",
                   expected_output="At most 5 lines", agent=writer,
                   context=[plan_task, risk_task])

crew = Crew(
    agents=[planner, risk, writer],
    tasks=[plan_task, risk_task, status_task],
    process=Process.sequential,     # planner -> risk -> writer
    verbose=True,
)

result = crew.kickoff(inputs={"brief": open("brief.md", encoding="utf-8").read()})
print(result)      # the final task's output: the status update

# save shared state from Python, so it can't depend on the model's choice
plan = result.tasks_output[0].pydantic
Path("project_state.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")
print("saved project_state.json")
