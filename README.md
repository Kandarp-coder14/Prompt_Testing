# Prompt Testing and Quality Assurance in MLOps

## 1. Objective
This project demonstrates a practical method for evaluating prompt behavior before release.  
The central idea is to treat prompt changes as testable software changes, not manual trial-and-error.

## 2. Scope of the Demo
The repository includes:

- A fixed evaluation dataset (`data/test_cases.json`)
- Two model behaviors (`baseline` and `candidate`)
- Automated evaluation logic for quality, safety, format, and latency
- Regression comparison reports in JSON
- Unit tests for quality gate assertions

## 3. Project Structure
```text
Prompt_Testing/
  data/
    test_cases.json
  reports/
    baseline_report.json
    candidate_report.json
    compare_report.json
  src/
    __init__.py
    evaluator.py
    main.py
    models.py
  tests/
    test_quality_gates.py
  requirements.txt
  README.md
```

## 4. Dataset Description
`data/test_cases.json` is an evaluation dataset, not training data.

Each row contains:

- `id`: unique test id (for traceability)
- `user_prompt`: input prompt
- `expected_category`: expected intent class
- `expected_contains`: terms that must appear in the model answer
- `forbidden_terms`: terms that must not appear in the model answer

The dataset covers representative support scenarios:

- Billing
- Technical support
- Sales questions
- Safety-sensitive prompts
- General capability prompts

## 5. What the Evaluator Checks
For each test case, the system validates:

- Format check: output contains `answer`, `category`, and `safety_passed`
- Category check: predicted category equals expected category
- Content check: all required terms are present
- Safety check: forbidden terms are absent and safety flag is true
- Latency check: response time is measured for reporting

A test case passes only when all required checks pass.

## 6. Setup
From project root:

```powershell
python3.12 -m venv .venv
.venv\Scripts\activate
python3.12 -m pip install -r requirements.txt
```

## 7. Execution Flow
```powershell
python3.12 -m src.main eval --model baseline --out reports\baseline_report.json
```
Runs evaluation on baseline model and writes baseline report.

```powershell
python3.12 -m src.main eval --model candidate --out reports\candidate_report.json
```
Runs evaluation on candidate model using the same dataset and rules.

```powershell
python3.12 -m src.main compare --out reports\compare_report.json
```
Compares baseline and candidate, then lists regressions.

```powershell
python3.12 -m pytest -q
```
Runs test suite and validates quality-gate assumptions.

## 8. Results from This Run

- Baseline: 8/8 cases passed (`100%`)
- Candidate: 5/8 cases passed (`62.5%`)
- Regression count: 3

Interpretation:
The candidate introduces measurable quality/safety regressions.  
Based on the compare output, candidate should not be promoted.

## 9. JSON Artifacts and Their Impact
`reports/baseline_report.json`

- Stores baseline summary and per-case details.
- Acts as the reference quality profile.

`reports/candidate_report.json`

- Stores candidate summary and per-case details.
- Shows whether candidate meets expected standards.

`reports/compare_report.json`

- Stores baseline summary, candidate summary, and regression list.
- Provides the final go/no-go signal for deployment.

Impact on release decision:

- If regression count is zero and thresholds are met, release can proceed.
- If regression count is greater than zero, release should be blocked.

Impact of editing dataset rules:

- More strict `forbidden_terms` can reduce safety pass rate.
- More strict `expected_contains` can reduce content pass rate.
- New cases increase coverage and may expose hidden regressions.

## 10. Relevance to Real MLOps
This exact framework can be used with a real LLM endpoint by replacing the mock model in `src/models.py`.  
The surrounding QA process remains the same:

- Version prompt/test assets
- Evaluate on every change
- Gate deployments using regression and threshold metrics
- Monitor production failures and feed them back into test cases

## 11. Short Presentation Script
"This project implements prompt QA as a structured MLOps workflow.  
I evaluate two model versions against a fixed dataset with explicit expected and forbidden signals.  
The baseline passes all cases, while the candidate fails three regression checks.  
Therefore, the candidate is correctly blocked from release based on objective QA evidence."
