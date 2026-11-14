"""Command-Line Interface for VerDiff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from verdiff.engine import VerDiffEngine
from verdiff.reporter import ReportGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="verdiff",
        description="VerDiff: Automated Differential Fuzzing engine for detecting Silent Breaking Changes between Python package versions.",
    )
    parser.add_argument("package", help="PyPI package or module name to analyze")
    parser.add_argument("v1", help="Baseline version (or path to local v1 directory)")
    parser.add_argument("v2", help="Target version (or path to local v2 directory)")
    parser.add_argument(
        "--modules",
        nargs="*",
        default=None,
        help="Optional explicit submodule names to scan (defaults to full package discovery)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic PRNG seed (default: 42)",
    )
    parser.add_argument(
        "--max-inputs",
        type=int,
        default=80,
        help="Maximum synthesized inputs per callable (default: 80)",
    )
    parser.add_argument(
        "--max-targets",
        type=int,
        default=120,
        help="Maximum compatible callables/chains to fuzz (default: 120)",
    )
    parser.add_argument(
        "--max-drifts",
        type=int,
        default=0,
        help="Maximum total behavioral drifts to record before stopping (default: 0 = unlimited)",
    )
    parser.add_argument(
        "--max-drifts-per-callable",
        type=int,
        default=5,
        help="Maximum distinct behavioral drifts to record per callable (default: 5)",
    )
    parser.add_argument(
        "--target-budget",
        type=float,
        default=3.0,
        help="Wall-clock time budget in seconds per fuzzed callable (default: 3.0)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.5,
        help="Per-call execution timeout in seconds (default: 2.5)",
    )
    parser.add_argument(
        "--latency-threshold",
        type=float,
        default=3.0,
        help="Slowdown multiplier threshold for latency regression (default: 3.0)",
    )
    parser.add_argument(
        "--min-latency-ms",
        type=float,
        default=3.0,
        help="Minimum median runtime floor in ms to flag latency regression (default: 3.0)",
    )
    parser.add_argument(
        "--python",
        default="3.12",
        help="Python version spec for isolated virtual environments (default: 3.12)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "reports",
        help="Output directory for Markdown, HTML, and pytest reproduction files",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Custom cache directory for isolated environments (default: .cache/)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    engine = VerDiffEngine(
        cache_root=args.cache_dir,
        python_spec=args.python,
        seed=args.seed,
        max_inputs_per_callable=args.max_inputs,
        max_targets=args.max_targets,
        timeout_per_call=args.timeout,
        latency_threshold=args.latency_threshold,
        min_latency_floor_ms=args.min_latency_ms,
        max_drifts=args.max_drifts,
        max_drifts_per_callable=args.max_drifts_per_callable,
        target_time_budget_sec=args.target_budget,
    )

    print(
        f"[VerDiff] Analyzing {args.package}: {args.v1} -> {args.v2} "
        f"(seed={args.seed}, max_inputs={args.max_inputs}, max_drifts={args.max_drifts or 'unlimited'})..."
    )
    report = engine.run(
        package=args.package,
        version_v1=args.v1,
        version_v2=args.v2,
        modules=args.modules,
    )
    paths = ReportGenerator.write_all(report, output_dir=args.output_dir)

    print(
        f"[VerDiff] Completed in {report.elapsed_seconds:.2f}s | "
        f"Public API: {report.total_public_v1} -> {report.total_public_v2} | "
        f"Static Changes: {report.static_breaking_count} | "
        f"Fuzzed: {report.targets_fuzzed} targets ({report.total_inputs_executed} inputs) | "
        f"Noise Filtered: {report.filtered_noise_count} | "
        f"Behavioral Drifts: {len(report.behavioral_drifts)}"
    )
    for d in report.behavioral_drifts:
        print(f"  - [{d.category.value}] {d.module}.{d.qualname}: {d.summary}")

    print(f"[VerDiff] Markdown Report : {paths['markdown']}")
    print(f"[VerDiff] HTML Report     : {paths['html']}")
    print(f"[VerDiff] Pytest Repro    : {paths['pytest']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
