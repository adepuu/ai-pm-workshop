# Build Your AI Project Manager — workshop code

A minimal, fully-local agentic PM assistant built with **CrewAI** and **Ollama**.
No API keys; the model runs on your machine.

## 1. Install a local model (once)
Install Ollama from https://ollama.com, then:
```
ollama pull llama3.1        # ~4.7 GB
# weaker laptop: ollama pull llama3.2:3b   # ~2 GB
```

## 2. Python environment (Python 3.10-3.13; 3.14 is not supported)
On macOS, use `python3` for the first command if `python` isn't found.
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python check_setup.py
```

## 3. Run the PM assistant
```
python pm_crew.py --brief brief.md
```
It plans tasks, flags risks, drafts a status update, and writes `project_state.json`.

To use another model or tag: `WORKSHOP_MODEL=ollama/llama3.2:3b python pm_crew.py --brief brief.md`
(Windows PowerShell: `$env:WORKSHOP_MODEL="ollama/llama3.2:3b"`, then run the command. PowerShell may also need
`.venv\Scripts\Activate.ps1` to activate the venv.)

To see a model choosing whether to call a tool: `python tool_demo.py`. Run it a few times.

## Fell behind? Use a checkpoint
Each build stage has a working file. Run it from this folder, e.g. `python checkpoints/03_typed_output.py`.

| File | Slide |
|---|---|
| `checkpoints/01_first_agent.py` | 12 |
| `checkpoints/02_add_a_tool.py` | 13 |
| `checkpoints/03_typed_output.py` | 15 |
| `checkpoints/04_full_crew.py` | 16-17 |

## 4. Run the virtual office (intermezzo)
```
python virtual_office.py
```
A Project Lead returns a typed work plan, and Python dispatches it to CV / Backend / Frontend / QA engineers.

Why not `Process.hierarchical`? In testing with Llama 3.1 and 3.2, the manager wrote its delegation as text
and no specialist ever ran, yet the script exited successfully. Always check who actually ran.

## Notes
- Tested on `crewai==1.15.35`. CrewAI's API changes between releases, so keep the pin for the workshop.
- Local models are slower than hosted APIs. Smaller models (e.g. `llama3.2:3b`) are
  faster but weaker; size the model and the crew to your hardware.
- Keep irreversible actions (send, pay, delete) behind human approval — see the
  `send_email` guardrail pattern in the slides.

Prepared by Felix Yustian Setiono for the MurzEdu Program (ecommurz).
