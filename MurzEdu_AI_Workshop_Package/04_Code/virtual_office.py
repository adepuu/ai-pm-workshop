"""
Intermezzo — the Virtual Office (NexaPaw-style).

A named Project Lead decides who does what; specialists do the work. You define the
staff, not the steps. The Lead returns a typed work plan and Python dispatches it,
so every assignment really runs and you can see exactly who did what.

Run:
    python virtual_office.py

Weak laptop, or a different model tag?
    WORKSHOP_MODEL=ollama/llama3.2:3b python virtual_office.py

Scale the roles to your hardware: every extra agent means more local model calls.
"""
import os
from typing import List, Literal

from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process, LLM

MODEL = os.getenv("WORKSHOP_MODEL", "ollama/llama3.1")
llm = LLM(model=MODEL, base_url="http://localhost:11434")


def staff(role: str, goal: str, backstory: str) -> Agent:
    return Agent(role=role, goal=goal, backstory=backstory, llm=llm, verbose=True)


# --- the Lead and the specialist "staff" ------------------------------------
lead = staff("Project Lead",
             "Deliver the feature end to end; assign work to the right specialist",
             "Runs a NexaPaw project team; delegates and reviews.")

team = {
    "CV Engineer": staff("CV Engineer", "Build and evaluate the model", "A pragmatic CV engineer."),
    "Backend Engineer": staff("Backend Engineer", "Build the APIs and data pipeline", "A careful backend engineer."),
    "Frontend Engineer": staff("Frontend Engineer", "Build the user interface", "A tidy frontend engineer."),
    "QA Engineer": staff("QA Engineer", "Test the work against the spec", "A sharp, fair tester."),
}


# --- typed delegation: an assignment can only name a real staff member -------
class Assignment(BaseModel):
    role: Literal["CV Engineer", "Backend Engineer", "Frontend Engineer", "QA Engineer"]
    work: str


class WorkPlan(BaseModel):
    assignments: List[Assignment]


def run_office(brief: str) -> str:
    # 1. the Lead decides who does what
    planning = Task(
        description=(
            f"Goal: {brief}\nAssign this goal to your team: "
            f"{', '.join(team)}. Give each person you use one concrete piece of work, "
            "in the order it should happen. Use 3 assignments at most."
        ),
        expected_output="A WorkPlan: an ordered list of assignments (role, work)",
        agent=lead,
        output_pydantic=WorkPlan,
    )
    plan = Crew(agents=[lead], tasks=[planning]).kickoff().pydantic
    if plan is None:
        raise SystemExit("The Lead did not return a valid WorkPlan.")

    # 2. Python dispatches the Lead's decisions; each specialist sees earlier work
    tasks: List[Task] = []
    for a in plan.assignments[:3]:
        tasks.append(Task(
            description=f"Goal: {brief}\nYour assignment: {a.work}\nIn at most 4 short bullet points, say how you would do it.",
            expected_output="At most 4 short bullet points",
            agent=team[a.role],
            context=list(tasks),
        ))

    # 3. the Lead reviews everything and reports
    tasks.append(Task(
        description=f"Review your team's notes on the goal: {brief}. Write a short summary of who "
                    "proposes what, naming people only by role (never invent names). This is a plan: "
                    "do not claim that anything has shipped.",
        expected_output="A summary of at most 6 lines",
        agent=lead,
        context=list(tasks),
    ))
    agents = list({id(t.agent): t.agent for t in tasks}.values())
    result = Crew(agents=agents, tasks=tasks, process=Process.sequential).kickoff()

    print("\n=== WHO DID WHAT ===")
    for a in plan.assignments[:3]:
        print(f"- {a.role}: {a.work}")
    return result.raw


if __name__ == "__main__":
    print("\n=== OFFICE RESULT ===\n")
    print(run_office("Ship cross-camera re-ID v2"))
