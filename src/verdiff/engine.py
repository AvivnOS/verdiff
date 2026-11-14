"""End-to-end Differential Fuzzing Engine orchestrating environments, extraction, synthesis, and oracle."""

from __future__ import annotations

import time
from pathlib import Path

from verdiff.env_manager import IsolatedEnvManager
from verdiff.extractor import SurfaceComparator
from verdiff.models import BehavioralDrift, DiffReport, StaticChangeKind
from verdiff.oracle import BehavioralOracle
from verdiff.synthesizer import InputSynthesizer


class VerDiffEngine:
    """Orchestrates dual-environment provisioning, API extraction, input synthesis, and behavioral diffing."""

    def __init__(
        self,
        cache_root: Path | None = None,
        python_spec: str = "3.12",
        seed: int = 42,
        max_inputs_per_callable: int = 80,
        max_targets: int = 180,
        timeout_per_call: float = 2.5,
        latency_threshold: float = 3.0,
        min_latency_floor_ms: float = 3.0,
        max_drifts: int = 0,
        max_drifts_per_callable: int = 5,
        target_time_budget_sec: float = 3.0,
    ) -> None:
        self.env_manager = IsolatedEnvManager(
            cache_root=cache_root,
            python_spec=python_spec,
            timeout_per_call=timeout_per_call,
        )
        self.python_spec = python_spec
        self.seed = seed
        self.max_inputs_per_callable = max_inputs_per_callable
        self.max_targets = max_targets
        self.latency_threshold = latency_threshold
        self.min_latency_floor_ms = min_latency_floor_ms
        self.max_drifts = max_drifts
        self.max_drifts_per_callable = max_drifts_per_callable
        self.target_time_budget_sec = target_time_budget_sec

    def run(
        self,
        package: str,
        version_v1: str,
        version_v2: str,
        modules: list[str] | None = None,
    ) -> DiffReport:
        t0 = time.perf_counter()

        worker_v1 = self.env_manager.ensure_environment(package, version_v1)
        worker_v2 = self.env_manager.ensure_environment(package, version_v2)

        try:
            ping_resp = worker_v1.request({"cmd": "ping"}, timeout=10.0)
            py_ver = str(ping_resp.get("python_version", self.python_spec))

            contracts_v1 = worker_v1.extract_surface(package, modules=modules)
            contracts_v2 = worker_v2.extract_surface(package, modules=modules)

            public_v1_count = sum(1 for c in contracts_v1 if c.callable_kind != "stateful_chain")
            public_v2_count = sum(1 for c in contracts_v2 if c.callable_kind != "stateful_chain")

            static_diffs = SurfaceComparator.compare(contracts_v1, contracts_v2)
            fuzz_pairs = SurfaceComparator.select_fuzz_targets(static_diffs)
            if self.max_targets > 0:
                fuzz_pairs = fuzz_pairs[: self.max_targets]

            synthesizer = InputSynthesizer(
                seed=self.seed,
                max_inputs_per_callable=self.max_inputs_per_callable,
            )
            oracle = BehavioralOracle(
                worker_v1=worker_v1,
                worker_v2=worker_v2,
                version_v1=version_v1,
                version_v2=version_v2,
                latency_threshold=self.latency_threshold,
                min_latency_floor_ms=self.min_latency_floor_ms,
                max_drifts_per_callable=self.max_drifts_per_callable,
                target_time_budget_sec=self.target_time_budget_sec,
            )

            all_drifts: list[BehavioralDrift] = []
            total_executed = 0

            for c1, c2 in fuzz_pairs:
                if self.max_drifts > 0 and len(all_drifts) >= self.max_drifts:
                    break
                inputs = synthesizer.synthesize_for_pair(c1, c2)
                drifts, count = oracle.fuzz_callable_pair(c1, c2, inputs)
                for d in drifts:
                    all_drifts.append(d)
                    if self.max_drifts > 0 and len(all_drifts) >= self.max_drifts:
                        break
                total_executed += count

            elapsed = time.perf_counter() - t0
            return DiffReport(
                package=package,
                version_v1=version_v1,
                version_v2=version_v2,
                python_version=py_ver,
                seed=self.seed,
                total_public_v1=public_v1_count,
                total_public_v2=public_v2_count,
                static_diffs=static_diffs,
                behavioral_drifts=all_drifts,
                targets_fuzzed=len(fuzz_pairs),
                total_inputs_executed=total_executed,
                filtered_noise_count=oracle.filtered_noise_count,
                max_drifts_limit=self.max_drifts,
                elapsed_seconds=elapsed,
            )
        finally:
            worker_v1.close()
            worker_v2.close()
