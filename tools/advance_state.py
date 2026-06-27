#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


STEP_ORDER = [
    "01_model_explain",
    "02_financial_check",
    "03_news_catalyst",
    "04_industry_check",
    "05_bear_case",
    "06_final_rating",
    "07_memory_update",
]


def next_step_for(step: str) -> str:
    try:
        idx = STEP_ORDER.index(step)
    except ValueError as exc:
        raise SystemExit(f"Unknown step: {step}") from exc
    return STEP_ORDER[idx + 1] if idx + 1 < len(STEP_ORDER) else "done"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def load_task_symbols(task_path: Path) -> tuple[str, list[str]]:
    task = load_json(task_path)
    return task["task_id"], [item["ts_code"] for item in task["universe"]]


def all_symbols_completed(completed_steps: dict, symbols: list[str]) -> bool:
    return all("07_memory_update" in completed_steps.get(symbol, []) for symbol in symbols)


def next_incomplete_symbol(symbols: list[str], completed_steps: dict, current_symbol: str) -> str | None:
    if current_symbol in symbols:
        start_index = symbols.index(current_symbol) + 1
        ordered = symbols[start_index:] + symbols[:start_index]
    else:
        ordered = symbols

    for symbol in ordered:
        if "07_memory_update" not in completed_steps.get(symbol, []):
            return symbol
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True, help="Path to state.json")
    parser.add_argument("--task", required=True, help="Path to task.json")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--ts-code", required=True)
    parser.add_argument("--step", required=True, choices=STEP_ORDER)
    parser.add_argument("--status", required=True, choices=["success", "failed"])
    parser.add_argument("--reason", default=None)
    args = parser.parse_args()

    state_path = Path(args.state)
    task_path = Path(args.task)
    state = load_json(state_path)
    task_id, symbols = load_task_symbols(task_path)

    if task_id != args.task_id:
        raise SystemExit(f"--task-id ({args.task_id}) does not match task.json ({task_id})")
    if args.ts_code not in symbols:
        raise SystemExit(f"{args.ts_code} is not present in {task_path}")

    state["task_id"] = args.task_id
    state["current_symbol"] = args.ts_code
    state["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    completed = state.setdefault("completed_steps", {})
    completed.setdefault(args.ts_code, [])

    if args.status == "success":
        if args.step not in completed[args.ts_code]:
            completed[args.ts_code].append(args.step)
        state["failed_step"] = None
        state["failure_reason"] = None

        if args.step == "07_memory_update":
            if all_symbols_completed(completed, symbols):
                state["status"] = "completed"
                state["current_symbol"] = args.ts_code
                state["next_step"] = "done"
            else:
                state["status"] = "running"
                state["current_symbol"] = next_incomplete_symbol(symbols, completed, args.ts_code)
                state["next_step"] = "01_model_explain"
        else:
            state["status"] = "running"
            state["current_symbol"] = args.ts_code
            state["next_step"] = next_step_for(args.step)
    else:
        state["status"] = "failed"
        state["current_symbol"] = args.ts_code
        state["next_step"] = args.step
        state["failed_step"] = args.step
        state["failure_reason"] = args.reason or "unknown failure"

    dump_json(state_path, state)
    print(f"Updated {state_path} for {args.ts_code} {args.step} -> {args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
