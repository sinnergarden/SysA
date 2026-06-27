# SysA Design

## System Goal

`SysA` is a minimal research-agent scaffold for reviewing `Qsys` stock candidates with a deterministic file-system workflow. Its purpose is to turn model candidates plus supporting materials into structured research evidence, step outputs, final research ratings, and memory update suggestions.

## Non-Goal

- No trading instruction generation
- No portfolio action automation
- No market data ingestion framework
- No LLM API integration
- No hidden reasoning in Python
- No database, queue, or web service

## Inputs

Primary input is `tasks/<task_id>/task.json`, which contains:

- Task metadata
- Candidate universe
- Relative paths to supporting input files

Optional supporting inputs per symbol include:

- Financial template JSON
- Company memory JSON
- Industry memory JSON
- News search results JSON
- Announcement JSON

## Outputs

Per symbol, each step writes one JSON file under:

- `outputs/<task_id>/<ts_code>/01_model_explain.json`
- `outputs/<task_id>/<ts_code>/02_financial_check.json`
- `outputs/<task_id>/<ts_code>/03_news_catalyst.json`
- `outputs/<task_id>/<ts_code>/04_industry_check.json`
- `outputs/<task_id>/<ts_code>/05_bear_case.json`
- `outputs/<task_id>/<ts_code>/06_final_rating.json`
- `outputs/<task_id>/<ts_code>/07_memory_update.json`

This single-symbol directory design keeps reruns and failure recovery simple.

## Evidence, Memory, Output

### Evidence

Evidence is the fact layer. It may come from filings, announcements, financial templates, news, industry notes, or memory documents. Evidence should preserve source reference, extracted fact, and reliability metadata. Evidence is not a rating.

### Memory

Memory is compressed long-term knowledge. It should only keep stable, reusable knowledge, such as repeated business patterns, recurring risk flags, or structural industry traits. Short-term price action, single-day sentiment, and unverified rumor should not be written into memory.

### Output

Output is the step conclusion layer. Every step must emit JSON only. Any key conclusion must cite one or more `evidence_id` values, or explicitly mark `evidence_insufficient`.

## Task Chain

The chain is step-based and restartable:

1. `01_model_explain`
2. `02_financial_check`
3. `03_news_catalyst`
4. `04_industry_check`
5. `05_bear_case`
6. `06_final_rating`
7. `07_memory_update`

Each step reads only the current symbol, required inputs, and explicitly listed prior outputs. It does not reload all raw materials by default.

## Step Boundaries

### 01 Model Explain

Explains why the model selected the symbol based on score and feature contribution only.

### 02 Financial Check

Checks whether financial template data supports or contradicts the model logic. It does not analyze news or industry conditions.

### 03 News Catalyst

Reviews recent news, announcements, report headlines, and similar near-term information. It must separate fundamental catalyst from sentiment heat.

### 04 Industry Check

Judges supply-demand, industry cycle, chain position, and concept-hype risk. It does not replace industry reasoning with stock-price performance.

### 05 Bear Case

Builds the counter-case and highlights vulnerabilities, contradictions, and weak links in prior reasoning.

### 06 Final Rating

Aggregates step `01` to `05` into a final research rating and confidence. It cannot invent new evidence or output trading instructions.

### 07 Memory Update

Produces proposed long-term memory updates only. It does not rewrite evidence and does not auto-commit memory changes.

## Failure Recovery

`tasks/<task_id>/state.json` tracks current symbol, next step, completed steps, and failure status. Recovery rule:

- If a step fails, stop immediately.
- Write `failed_step`, `failure_reason`, and `status=failed`.
- Resume from `current_symbol + next_step` after fixing the issue.
- If an output file already exists and passes schema validation, rerun may skip it.

## JSON Persistence Rules

- All outputs must be valid JSON.
- All paths should be relative to repo root.
- Every step writes exactly one JSON file per symbol.
- Evidence references use `evidence_id`.
- Missing or weak inputs must map to `insufficient` or `unknown`, never fabrication.

## Evidence ID Rule

Recommended format:

- `{ts_code}_{step}_{index}`

Example:

- `000001.SZ_news_001`

Within the same task date, each `evidence_id` must be unique.

## Rating Standard

- `A`: model logic is clear, validation is strong, catalyst is usable, and bear case is limited. High manual research priority.
- `B`: some support exists, but important uncertainty remains. Worth tracking.
- `C`: support is average, incomplete, or weak. Lower priority.
- `D`: the main evidence does not support the logic, or risk outweighs research value.

These ratings express research priority and manual attention level only. They are not trading instructions.

## Confidence Standard

- `high`: multiple reliable pieces of evidence support the core judgment with limited conflict
- `medium`: partial support exists, but gaps or conflicts remain
- `low`: evidence is insufficient, weak, or unresolved

## Trading Boundary

This system must not generate automatic trade instructions, order suggestions, position sizing, or execution advice. It outputs research ratings only.
