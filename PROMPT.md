This file preserves the v2 build prompt used to define the SysA scaffold.

Key enforced constraints:

- Step-based task chain instead of one-shot prompt
- Each step is independently rerunnable
- Each step reads only required inputs and named prior outputs
- All intermediate results are persisted to disk
- Evidence is fully preserved; memory is compressed long-term knowledge only
- Python is deterministic glue only
- No trading, no order generation, no LLM API integration
- Single-symbol output directories
- Hard contracts for `evidence_id`, `state.json`, and `final_rating.json`

The repo contents below are the executed result of that prompt.
