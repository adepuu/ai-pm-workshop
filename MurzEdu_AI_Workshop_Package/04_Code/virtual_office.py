"""
Intermezzo — the Virtual Office (NexaPaw-style).

A *hierarchical* crew modelled on a NexaPaw project team: a named Project Lead
plans and delegates to specialist engineers. You define the staff (the agents);
the Lead decides who does what, and when.

In the real NexaPaw office, every Claude Code role is an agent with a job, a
project and tasks; a CEO and CTO sit above many project teams like this one,
and the whole office is visualized live in a 3D HQ.

Run:
    python virtual_office.py

Scale the roles to your hardware: every extra agent means more local model calls
(slower, more nondeterministic).
"""
from crewai import Agent, Task, Crew, Process, LLM

llm = LLM(model="ollama/llama3.1", base_url="http://localhost:11434")


def staff(role: str, goal: str, backstory: str) -> Agent:
    return Agent(role=role, goal=goal, backstory=backstory, llm=llm, verbose=True)


# --- the Lead (manager) and the specialist "staff" -------------------------
lead = staff("Project Lead",
             "Deliver the feature end to end; assign work to the right specialist",
             "Runs a NexaPaw project team; delegates and reviews.")

cv_engineer = staff("CV Engineer", "Build and evaluate the model", "A pragmatic CV engineer.")
backend = staff("Backend Engineer", "Build the APIs and data pipeline", "A careful backend engineer.")
frontend = staff("Frontend Engineer", "Build the user interface", "A tidy frontend engineer.")
qa = staff("QA Engineer", "Test the work against the spec", "A sharp, fair tester.")

# --- one high-level goal; the Lead routes the work -------------------------
deliver = Task(
    description="Deliver this goal end to end: {brief}",
    expected_output="A finished deliverable plus a short write-up of what was done.",
)

office = Crew(
    agents=[cv_engineer, backend, frontend, qa],
    tasks=[deliver],
    process=Process.hierarchical,   # the Lead delegates
    manager_agent=lead,             # a named manager agent, not just an LLM
    verbose=True,
)

if __name__ == "__main__":
    result = office.kickoff(inputs={"brief": "Ship cross-camera re-ID v2"})
    print("\n=== OFFICE RESULT ===\n")
    print(result)
