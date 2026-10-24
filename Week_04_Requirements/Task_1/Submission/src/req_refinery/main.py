"""Command-line entry point."""

import argparse
import asyncio
import importlib
import sys
import time
import warnings
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from req_refinery.config import DEFAULT_MAX_ROUNDS, MODELS
from req_refinery.graph import build_graph
from req_refinery.llm import LLMClient, OpenAIClient
from req_refinery.state import GraphName, GraphState, TraceRecord, initial_state
from req_refinery.trace import Deps, TraceWriter, write_snapshot

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_mock_client() -> LLMClient:
    """Import the fake model from tests/ (mock code is kept out of src/)."""
    sys.path.insert(0, str(PROJECT_ROOT))
    module = importlib.import_module("tests.fake_llm")
    client: LLMClient = module.FakeLLM()
    return client


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Requirements refinement network")
    _ = parser.add_argument("--input", required=True, type=Path, help="corpus directory")
    _ = parser.add_argument("--output", required=True, type=Path, help="output directory")
    _ = parser.add_argument("--limit", type=int, default=None, help="use first N documents")
    _ = parser.add_argument("--max-rounds", type=int, default=DEFAULT_MAX_ROUNDS)
    _ = parser.add_argument(
        "--graph",
        choices=["network", "hybrid"],
        default="hybrid",
        help="hybrid (whole-corpus consolidation, default) or network (per-document merge)",
    )
    _ = parser.add_argument("--mock", action="store_true", help="use the fake LLM from tests/")
    return parser.parse_args(argv)


async def run_pipeline(
    input_dir: Path,
    output_dir: Path,
    client: LLMClient,
    limit: int | None = None,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    graph_name: GraphName = "network",
) -> tuple[GraphState, Path]:
    """Run the graph, saving a state snapshot after every superstep.

    Run dirs go to <output>/runs/<stamp>_<graph>/; the final documents are copied to
    <output>/<graph>/.
    """
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / "runs" / f"{stamp}_{graph_name}"
    suffix = 1
    while run_dir.exists():
        suffix += 1
        run_dir = output_dir / "runs" / f"{stamp}_{graph_name}_{suffix}"
    publish_dir = output_dir / graph_name
    publish_dir.mkdir(parents=True, exist_ok=True)
    state_dir = run_dir / "state"
    state_dir.mkdir(parents=True)
    tracer = TraceWriter(run_dir / "trace.jsonl")
    deps = Deps(llm=client, tracer=tracer, models=dict(MODELS))
    graph = build_graph(deps, graph_name)
    init = initial_state(
        str(input_dir.resolve()),
        str(publish_dir.resolve()),
        str(run_dir.resolve()),
        limit,
        max_rounds,
        graph_name,
    )
    final: dict[str, Any] = dict(init)
    step_nodes: list[str] = []
    index = 0
    try:
        async for mode, chunk in graph.astream(
            init, stream_mode=["updates", "values"], config={"recursion_limit": 100}
        ):
            if mode == "updates" and isinstance(chunk, dict):
                step_nodes.extend(n for n in chunk if n not in step_nodes)
            elif mode == "values" and isinstance(chunk, dict):
                final = chunk
                label = "+".join(step_nodes) if step_nodes else "input"
                write_snapshot(state_dir, index, label, final)
                index += 1
                step_nodes = []
    finally:
        tracer.close()
    return GraphState(**final), run_dir


def summarize(state: GraphState, run_dir: Path, wall_s: float) -> str:
    tokens: dict[str, dict[str, int]] = defaultdict(
        lambda: {"prompt": 0, "completion": 0, "total": 0}
    )
    routes: list[str] = []
    issue_counts: dict[str, int] = defaultdict(int)
    for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines():
        rec = TraceRecord.model_validate_json(line)
        calls: list[dict[str, Any]] = rec.payload.get("llm_calls", [])
        for call in calls:
            usage: dict[str, int] = call.get("usage") or {}
            for k in ("prompt", "completion", "total"):
                tokens[str(call["model"])][k] += usage.get(k, 0)
        if rec.node == "review":
            routes.append(
                f"r{rec.round}:{rec.payload.get('model_route')}->{rec.payload.get('route')}"
            )
            for issue in rec.payload.get("issues", []):
                issue_counts[str(issue["type"])] += 1
    lines = [
        f"graph: {state['graph']}",
        f"run dir: {run_dir}",
        f"wall time: {wall_s:.1f}s",
        f"documents: {len(state['documents'])}",
        f"review rounds: {state['round']}  routes: {', '.join(routes)}",
        f"issues by type: {dict(issue_counts)}",
        f"requirements: {len(state['requirements'])}",
        f"blacklist: {len(state['blacklist'])}",
        f"open issues: {len(state['open_issues'])}",
    ]
    lines += [f"tokens {m}: {t}" for m, t in sorted(tokens.items())]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    # langchain re-serialises streamed structured output and warns about the parsed field
    warnings.filterwarnings("ignore", message="Pydantic serializer warnings")
    _ = load_dotenv(PROJECT_ROOT / ".env")
    client: LLMClient = load_mock_client() if args.mock else OpenAIClient()
    output_dir: Path = args.output
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    state, run_dir = asyncio.run(
        run_pipeline(args.input, output_dir, client, args.limit, args.max_rounds, args.graph)
    )
    print(summarize(state, run_dir, time.perf_counter() - t0))


if __name__ == "__main__":
    main()
