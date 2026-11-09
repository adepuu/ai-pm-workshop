# AI PM Workshop

**Build Your AI Project Manager**: workshop materials for the MurzEdu Program (ecommurz).
Everything is available in English (`_EN`) and Bahasa Indonesia (`_ID`), as editable Office files and PDFs.

## Contents

All materials are in [`MurzEdu_AI_Workshop_Package/`](MurzEdu_AI_Workshop_Package/):

| Folder | What's inside |
|---|---|
| [Pre-workshop setup](MurzEdu_AI_Workshop_Package/) | `Pre_Workshop_Setup`: install steps to finish before the session |
| [`00_Outline`](MurzEdu_AI_Workshop_Package/00_Outline/) | Workshop outline and agenda |
| [`01_Slide_Deck`](MurzEdu_AI_Workshop_Package/01_Slide_Deck/) | Main slide deck (.pptx and .pdf) |
| [`02_Presenter_Handout`](MurzEdu_AI_Workshop_Package/02_Presenter_Handout/) | Presenter guide |
| [`03_Audience_Handouts`](MurzEdu_AI_Workshop_Package/03_Audience_Handouts/) | Build guide and worksheet for participants |
| [`04_Code`](MurzEdu_AI_Workshop_Package/04_Code/) | Hands-on code: a local CrewAI + Ollama PM assistant |
| [`05_Extras`](MurzEdu_AI_Workshop_Package/05_Extras/) | Virtual backgrounds and QR code |

## Quick start (code)

```bash
ollama pull llama3.1
cd MurzEdu_AI_Workshop_Package/04_Code
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python pm_crew.py --brief brief.md
```

Everything runs locally, with no API keys. See [`04_Code/README.md`](MurzEdu_AI_Workshop_Package/04_Code/README.md) for details.

---
Prepared by Felix Yustian Setiono.
