"""Checkpoint 1 (slide 12): one agent, one task, one crew. Run from the code folder:
    python checkpoints/01_first_agent.py
"""
import os

from crewai import Agent, Task, Crew, Process, LLM

llm = LLM(model=os.getenv("WORKSHOP_MODEL", "ollama/llama3.1"),
          base_url="http://localhost:11434")

planner = Agent(
    role="Project Planner",
    goal="Turn a project brief into a clear task list",
    backstory="A sharp PM who makes vague briefs actionable.",
    llm=llm, verbose=True,
)

task = Task(
    description="Break down this brief into tasks:\n{brief}",
    expected_output="A numbered task list with an owner each",
    agent=planner,
)

crew = Crew(agents=[planner], tasks=[task], process=Process.sequential)
print(crew.kickoff(inputs={"brief": open("brief.md", encoding="utf-8").read()}))
