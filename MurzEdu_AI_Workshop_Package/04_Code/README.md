# Build Your AI Project Manager — workshop code

A minimal, fully-local agentic PM assistant built with **CrewAI** and **Ollama**.
No API keys; the model runs on your machine.

## 1. Install a local model (once)
Install Ollama from https://ollama.com, then:
```
ollama pull llama3.1        # ~4.7 GB
# or: ollama pull qwen2.5
```

## 2. Python environment
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Run the PM assistant
```
python pm_crew.py --brief brief.md
```
It plans tasks, flags risks, drafts a status update, and writes `project_state.json`.

## 4. Run the virtual office (intermezzo)
```
python virtual_office.py
```
A hierarchical crew: a manager delegates to Planner / Researcher / Developer / QA / Writer.

## Notes
- CrewAI's API changes between releases — if an import or argument fails, check the
  version you installed against the current CrewAI docs, or adjust the pinned versions.
- Local models are slower than hosted APIs. Smaller models (e.g. `llama3.2:3b`) are
  faster but weaker; size the model and the crew to your hardware.
- Keep irreversible actions (send, pay, delete) behind human approval — see the
  `send_email` guardrail pattern in the slides.

Prepared by Felix Yustian Setiono for the MurzEdu Program (ecommurz).
