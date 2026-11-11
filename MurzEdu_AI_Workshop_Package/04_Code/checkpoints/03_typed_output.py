"""Checkpoint 3 (slide 15): typed output, not prose. Run from the code folder:
    python checkpoints/03_typed_output.py
"""
import os
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

plan_task = Task(
    description="Break the brief into tasks:\n{brief}",
    expected_output="A Plan object",
    agent=planner,
    output_pydantic=Plan,     # validated, typed output
)

crew = Crew(agents=[planner], tasks=[plan_task], process=Process.sequential)
result = crew.kickoff(inputs={"brief": open("brief.md", encoding="utf-8").read()})

plan = result.pydantic
print(f"\n{len(plan.tasks)} typed tasks:")
for t in plan.tasks:
    print(f"- {t.title} | {t.owner} | {t.estimate_days} days")
