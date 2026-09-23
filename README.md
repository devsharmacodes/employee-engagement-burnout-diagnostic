# Employee Engagement & Burnout Diagnostic

A preventive workforce analytics platform for identifying engagement gaps, burnout risks, and career-stage disengagement — built on Palo Alto Networks' HR dataset (1,470 employees).

Instead of analyzing attrition after employees leave, this project builds an early-warning layer: an **Engagement Index** (composite of involvement, job, environment, and relationship satisfaction) and a **Burnout Risk score** (overtime + work-life balance + engagement), so HR can act before disengagement turns into a resignation.

## Deliverables

- **Research paper** — [`reports/research_paper.docx`](reports/research_paper.docx): methodology, findings, and recommendations.
- **Interactive dashboard** — [`dashboard/app.py`](dashboard/app.py): Streamlit app with engagement overview, burnout risk breakdowns, career-stage analysis, and a manager action panel.
- **Analysis notebooks** — [`notebooks/`](notebooks): the full pipeline from raw data to scored dataset, step by step.

## Project structure

```
├── data/
│   ├── raw/                  # Original, untouched HR dataset
│   └── processed/            # Cleaned → engagement-scored → fully-scored CSVs
├── notebooks/                # 01-06: validation → engagement index → burnout risk → EDA
├── src/                      # Reusable scoring modules, shared by notebooks & dashboard
│   ├── data_loader.py
│   ├── engagement.py
│   ├── burnout.py
│   └── metrics.py
├── dashboard/
│   ├── app.py                # Streamlit app
│   └── .streamlit/config.toml
├── reports/
│   └── research_paper.docx
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Run the dashboard

```bash
streamlit run dashboard/app.py
```

## Run the notebooks

Open any notebook in `notebooks/` — they run in order (01 → 06) and each stage writes its output to `data/processed/` for the next one to use.

## Key findings

- Organization-wide Engagement Index: **0.536** / 1.00
- **13.0%** of employees are at High burnout risk
- Employees combining frequent travel with overtime (5.9% of the workforce) hit **32.6%** High burnout risk and **41.9%** attrition — more than double the org-wide rate
- Low-engagement employees leave at **34.1%**, vs. **10.2%** for highly engaged employees — validating the Engagement Index as a leading indicator

See [`reports/research_paper.docx`](reports/research_paper.docx) for full methodology and discussion.

## Roadmap

- Naive retrieval-augmented (RAG) question answering over the project's written documentation.