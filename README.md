# SysA

`SysA` is a minimal file-system-based research agent scaffold for `Qsys` candidate review. It does not call any LLM API by itself. Code agents execute markdown task files step by step and write JSON outputs to disk.

## What It Does

- Takes a daily `task.json` from `Qsys`
- Runs a seven-step research chain for each symbol
- Stores evidence, per-step outputs, final rating, and memory update suggestions
- Supports failure stop, schema validation, and resume from `state.json`

## What It Does Not Do

- No trading connection
- No order generation
- No crawler framework
- No database or service layer
- No embedded LLM orchestration in Python

## Layout

- `prompts/`: research rules for each step
- `steps/`: execution task files for code agents
- `schemas/`: JSON schema contracts
- `tasks/`: task packages and sample inputs
- `outputs/`: per-symbol step outputs
- `evidence/`: raw, parsed, and agent-produced evidence artifacts
- `memory/`: compressed long-term company and industry memory
- `tools/`: thin local helpers

## How To Use

1. Let `Qsys` generate a task package like `tasks/<task_id>/task.json`.
2. Initialize `tasks/<task_id>/state.json`.
3. Run `steps/run_chain.task.md` with a code agent, or execute steps `01` to `07` manually per symbol.
4. After each step, write JSON output to `outputs/<task_id>/<ts_code>/`.
5. Validate each output with `tools/validate_json.py`.
6. Update `state.json` with `tools/advance_state.py`.
7. Final result for each symbol is `outputs/<task_id>/<ts_code>/06_final_rating.json`.
8. `07_memory_update.json` is only a suggested memory patch, not an automatic write-back.

## Sample Run

The sample task lives in `tasks/sample_2026-06-27/`.

Example validation command:

```bash
python3 tools/validate_json.py \
  schemas/final_rating.schema.json \
  outputs/sample_2026-06-27/000001.SZ/06_final_rating.json
```

Example state advance command:

```bash
python3 tools/advance_state.py \
  --state tasks/sample_2026-06-27/state.json \
  --task-id sample_2026-06-27 \
  --ts-code 000001.SZ \
  --step 01_model_explain \
  --status success
```

## Evidence And Memory

- Evidence is the full research trace. Keep raw material references and structured extracted facts.
- Memory is compressed long-term knowledge. Do not write short-term noise into it.
- Outputs are step conclusions. Every important judgment must cite `evidence_id` or mark `evidence_insufficient`.

## Sample Data Notice

All sample symbol data and sample inputs in this repo are fictional placeholders for framework demonstration only. They are not investment advice.
