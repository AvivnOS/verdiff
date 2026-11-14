"""Behavioral Oracle, Smart Object Noise Filter, Diff Classifier & Deterministic Input Shrinker."""

from __future__ import annotations

import copy
import math
import time
from typing import Any

from verdiff.codec import normalize_sentinel_repr
from verdiff.env_manager import WorkerClient
from verdiff.models import (
    BehavioralDrift,
    CallableContract,
    DriftCategory,
    ExceptionDriftSubkind,
    ExecutionOutcome,
    SynthesizedInput,
)


class ObjectNoiseFilter:
    """Filters out non-breaking internal representation noise and backward-compatible attribute additions.

    Why this exists:
    1. **Backward-Compatible Attribute Addition:** When `v2` adds a new attribute or property to a class
       (e.g. `Retry.backoff_jitter` in `urllib3 2.0`), while every public attribute that existed in `v1`
       retains its exact value and type, existing callers of `v1` are not broken.
    2. **Internal Sentinel Representation:** Libraries frequently replace bare `object()` default sentinels
       with internal `_TYPE_DEFAULT.token` enums (e.g. `urllib3.Timeout()`). When all public properties
       (`connect_timeout`, `read_timeout`, `total`) are identical and the only difference is an internal
       sentinel token inside `repr` or state, it is a non-breaking implementation detail.
    """

    @classmethod
    def values_semantically_equivalent(
        cls,
        c1: Any,
        c2: Any,
        version_v1: str = "",
        version_v2: str = "",
    ) -> tuple[bool, bool]:
        """Return (is_equivalent, was_filtered_by_noise_rule)."""
        if c1 == c2:
            return True, False

        if not (isinstance(c1, dict) and isinstance(c2, dict)):
            return False, False

        t1 = c1.get("__t__")
        t2 = c2.get("__t__")

        # Both are internal sentinel objects (<object object> vs <_TYPE_DEFAULT.token>)
        if t1 == "sentinel" and t2 == "sentinel":
            return True, True

        # Package self-version strings embedded in string outputs
        if t1 == "str" and t2 == "str" and version_v1 and version_v2:
            s1 = str(c1.get("v", "")).replace(version_v1, "<PKG_VER>")
            s2 = str(c2.get("v", "")).replace(version_v2, "<PKG_VER>")
            if s1 == s2:
                return True, True

        # Recursive list/tuple comparison with noise rules
        if t1 in ("list", "tuple") and t1 == t2:
            items1 = c1.get("v", [])
            items2 = c2.get("v", [])
            if len(items1) != len(items2):
                return False, False
            any_filtered = False
            for x1, x2 in zip(items1, items2):
                eq, filt = cls.values_semantically_equivalent(x1, x2, version_v1, version_v2)
                if not eq:
                    return False, False
                any_filtered = any_filtered or filt
            return True, any_filtered

        # Custom object comparison with Backward-Compatible Attribute Addition & Sentinel Filter
        if t1 == "object" and t2 == "object":
            if c1.get("cls") != c2.get("cls"):
                return False, False

            st1 = c1.get("state", {})
            st2 = c2.get("state", {})
            if not isinstance(st1, dict) or not isinstance(st2, dict):
                return False, False

            repr_norm_eq = normalize_sentinel_repr(str(c1.get("repr", ""))) == normalize_sentinel_repr(
                str(c2.get("repr", ""))
            )
            if st1 or st2:
                for k in st1:
                    if k not in st2:
                        return False, False
                    eq, _ = cls.values_semantically_equivalent(st1[k], st2[k], version_v1, version_v2)
                    if not eq:
                        t_pair = {
                            st1[k].get("__t__") if isinstance(st1[k], dict) else None,
                            st2[k].get("__t__") if isinstance(st2[k], dict) else None,
                        }
                        if repr_norm_eq and t_pair <= {"sentinel", "none"}:
                            continue
                        return False, False

                str1 = normalize_sentinel_repr(str(c1.get("str", "")))
                str2 = normalize_sentinel_repr(str(c2.get("str", "")))
                repr1 = normalize_sentinel_repr(str(c1.get("repr", "")))
                repr2 = normalize_sentinel_repr(str(c2.get("repr", "")))
                if str1 == str2 or repr1 == repr2:
                    return True, True

            if normalize_sentinel_repr(str(c1.get("repr", ""))) == normalize_sentinel_repr(str(c2.get("repr", ""))):
                return True, True

        return False, False


def _generate_smaller_values(val: Any) -> list[Any]:
    """Generate simpler candidate values in increasing order of complexity for delta-debugging shrinking."""
    candidates: list[Any] = []

    if val is None or val is False or val == 0 or val == "" or val == b"" or val == [] or val == {} or val == ():
        return candidates

    if val is True:
        return [False]

    if type(val) is int:
        for c in (0, 1, -1, abs(val) if val < 0 else None, val // 2):
            if c is not None and c != val and abs(c) <= abs(val) and c not in candidates:
                candidates.append(c)
        return candidates

    if type(val) is float:
        if math.isnan(val) or math.isinf(val) or (val == 0.0 and math.copysign(1.0, val) < 0):
            return [0.0, 1.0, -1.0]
        for c in (0.0, 1.0, -1.0, float(int(val)), round(val / 2.0, 2)):
            if c != val and abs(c) <= abs(val) and c not in candidates:
                candidates.append(c)
        return candidates

    if type(val) is str:
        n = len(val)
        raw_cands = [""]
        if n > 1:
            mid = n // 2
            raw_cands.extend([val[:mid], val[mid:], val.strip(), val[:-1], val[1:]])
        for c in raw_cands:
            if c != val and len(c) < n and c not in candidates:
                candidates.append(c)
        return candidates

    if type(val) is bytes:
        n = len(val)
        raw_cands_b = [b""]
        if n > 1:
            mid = n // 2
            raw_cands_b.extend([val[:mid], val[mid:], val[:-1], val[1:]])
        for c in raw_cands_b:
            if c != val and len(c) < n and c not in candidates:
                candidates.append(c)
        return candidates

    if type(val) is list:
        n = len(val)
        candidates.append([])
        if n > 1:
            mid = n // 2
            for sub in (val[:mid], val[mid:], val[:-1], val[1:]):
                if sub not in candidates:
                    candidates.append(sub)
        for idx, item in enumerate(val[:6]):
            for smaller_item in _generate_smaller_values(item)[:3]:
                mut = list(val)
                mut[idx] = smaller_item
                if mut not in candidates:
                    candidates.append(mut)
        return candidates

    if type(val) is tuple:
        n = len(val)
        candidates.append(())
        if n > 1:
            mid = n // 2
            for sub in (val[:mid], val[mid:], val[:-1], val[1:]):
                if sub not in candidates:
                    candidates.append(sub)
        for idx, item in enumerate(val[:6]):
            for smaller_item in _generate_smaller_values(item)[:3]:
                mut = list(val)
                mut[idx] = smaller_item
                tup = tuple(mut)
                if tup not in candidates:
                    candidates.append(tup)
        return candidates

    if type(val) is dict:
        items = list(val.items())
        n = len(items)
        candidates.append({})
        if n > 1:
            mid = n // 2
            for sub_items in (items[:mid], items[mid:], items[:-1], items[1:]):
                d = dict(sub_items)
                if d not in candidates:
                    candidates.append(d)
        for k, v in items[:6]:
            for smaller_v in _generate_smaller_values(v)[:2]:
                d = dict(val)
                d[k] = smaller_v
                if d not in candidates:
                    candidates.append(d)
        return candidates

    return candidates


class BehavioralOracle:
    """Executes synthesized inputs across v1 and v2 workers, filters object noise, classifies drifts, and shrinks inputs."""

    def __init__(
        self,
        worker_v1: WorkerClient,
        worker_v2: WorkerClient,
        version_v1: str = "",
        version_v2: str = "",
        latency_threshold: float = 3.0,
        min_latency_floor_ms: float = 3.0,
        max_shrink_evals: int = 28,
        max_drifts_per_callable: int = 5,
        target_time_budget_sec: float = 3.0,
    ) -> None:
        self.worker_v1 = worker_v1
        self.worker_v2 = worker_v2
        self.version_v1 = version_v1
        self.version_v2 = version_v2
        self.latency_threshold = latency_threshold
        self.min_latency_floor_ms = min_latency_floor_ms
        self.max_shrink_evals = max_shrink_evals
        self.max_drifts_per_callable = max_drifts_per_callable
        self.target_time_budget_sec = target_time_budget_sec
        self.filtered_noise_count: int = 0

    def classify_pair(
        self,
        contract_v1: CallableContract,
        contract_v2: CallableContract,
        synth_input: SynthesizedInput,
        outcome_v1: ExecutionOutcome,
        outcome_v2: ExecutionOutcome,
        allow_benchmark: bool = True,
    ) -> tuple[DriftCategory, str | None, str] | None:
        """Compare outcomes of v1 and v2 and return (DriftCategory, subkind, summary) if a genuine breaking change occurred."""
        s1 = outcome_v1.status
        s2 = outcome_v2.status

        # 1. Crash or Timeout Discrepancies
        if s1 != s2 and ("timeout" in (s1, s2) or "crash" in (s1, s2)):
            summary = (
                f"v1 ended with '{s1}' ({outcome_v1.exception_type or outcome_v1.return_repr}), "
                f"while v2 ended with '{s2}' ({outcome_v2.exception_type or outcome_v2.return_repr})"
            )
            return (
                DriftCategory.EXCEPTION_TYPE_DRIFT,
                ExceptionDriftSubkind.CRASH_OR_TIMEOUT.value,
                summary,
            )

        # 2. Exception vs Return Discrepancies
        if s1 == "ok" and s2 == "exception":
            summary = (
                f"v1 returned {outcome_v1.return_repr} ({outcome_v1.return_type}), "
                f"but v2 raised {outcome_v2.exception_type}: {outcome_v2.exception_message}"
            )
            return (
                DriftCategory.EXCEPTION_TYPE_DRIFT,
                ExceptionDriftSubkind.PASS_TO_FAIL.value,
                summary,
            )

        if s1 == "exception" and s2 == "ok":
            summary = (
                f"v1 raised {outcome_v1.exception_type} ({outcome_v1.exception_message}), "
                f"but v2 returned {outcome_v2.return_repr} ({outcome_v2.return_type})"
            )
            return (
                DriftCategory.EXCEPTION_TYPE_DRIFT,
                ExceptionDriftSubkind.FAIL_TO_PASS.value,
                summary,
            )

        if s1 == "exception" and s2 == "exception":
            if outcome_v1.exception_type != outcome_v2.exception_type:
                summary = (
                    f"Exception type changed from {outcome_v1.exception_type} "
                    f"('{outcome_v1.exception_message}') in v1 to {outcome_v2.exception_type} "
                    f"('{outcome_v2.exception_message}') in v2"
                )
                return (
                    DriftCategory.EXCEPTION_TYPE_DRIFT,
                    ExceptionDriftSubkind.EXCEPTION_CLASS_CHANGED.value,
                    summary,
                )
            return None

        # Both succeeded ("ok"):
        # 3. Check In-Place Input or Stateful Instance Mutation Drift (with noise filtering on instance state)
        args_eq, _ = ObjectNoiseFilter.values_semantically_equivalent(
            outcome_v1.mutated_args_after, outcome_v2.mutated_args_after, self.version_v1, self.version_v2
        )
        kwargs_eq, _ = ObjectNoiseFilter.values_semantically_equivalent(
            outcome_v1.mutated_kwargs_after, outcome_v2.mutated_kwargs_after, self.version_v1, self.version_v2
        )
        inst_eq, inst_filt = ObjectNoiseFilter.values_semantically_equivalent(
            outcome_v1.mutated_instance_after, outcome_v2.mutated_instance_after, self.version_v1, self.version_v2
        )
        if inst_filt:
            self.filtered_noise_count += 1

        if not args_eq or not kwargs_eq or not inst_eq:
            if not args_eq or not kwargs_eq:
                summary = (
                    f"In-place argument mutation drift: v1 post-call args={outcome_v1.mutated_args_after is not None}, "
                    f"v2 post-call args={outcome_v2.mutated_args_after is not None}"
                )
            else:
                state_diff_desc = self._describe_object_state_diff(
                    outcome_v1.mutated_instance_after, outcome_v2.mutated_instance_after
                )
                if not state_diff_desc and isinstance(outcome_v1.mutated_instance_after, dict) and isinstance(outcome_v2.mutated_instance_after, dict):
                    r1 = outcome_v1.mutated_instance_after.get("repr") or outcome_v1.mutated_instance_after.get("state")
                    r2 = outcome_v2.mutated_instance_after.get("repr") or outcome_v2.mutated_instance_after.get("state")
                    state_diff_desc = f"post-call instance diverged ({r1!r} -> {r2!r})"
                summary = f"Stateful instance mutation drift: {state_diff_desc or 'post-call instance state diverged'}"
            return (DriftCategory.INPUT_MUTATION_DRIFT, "in_place_mutation", summary)

        # 4. Check Return Value Drift (with ObjectNoiseFilter)
        ret_eq, ret_filt = ObjectNoiseFilter.values_semantically_equivalent(
            outcome_v1.return_canonical,
            outcome_v2.return_canonical,
            self.version_v1,
            self.version_v2,
        )
        if ret_filt:
            self.filtered_noise_count += 1

        if not ret_eq:
            state_diff = self._describe_object_state_diff(
                outcome_v1.return_canonical, outcome_v2.return_canonical
            )
            if state_diff and outcome_v1.return_repr == outcome_v2.return_repr:
                summary = (
                    f"Return object state drift on {outcome_v1.return_repr} ({outcome_v1.return_type}): "
                    f"{state_diff}"
                )
            else:
                summary = (
                    f"Return value drift: v1 returned {outcome_v1.return_repr} ({outcome_v1.return_type}) "
                    f"!= v2 returned {outcome_v2.return_repr} ({outcome_v2.return_type})"
                )
            return (DriftCategory.RETURN_VALUE_DRIFT, "value_or_type_mismatch", summary)

        # 5. Check Latency Regression (confirmed via 5-run median benchmark)
        if allow_benchmark:
            slow_v2 = (
                outcome_v2.duration_ms >= self.min_latency_floor_ms
                and outcome_v2.duration_ms >= max(outcome_v1.duration_ms, 0.05) * self.latency_threshold
            )
            slow_v1 = (
                outcome_v1.duration_ms >= self.min_latency_floor_ms
                and outcome_v1.duration_ms >= max(outcome_v2.duration_ms, 0.05) * self.latency_threshold
            )
            if slow_v2 or slow_v1:
                med1 = self.worker_v1.benchmark_callable(contract_v1, synth_input, repeats=5)
                med2 = self.worker_v2.benchmark_callable(contract_v2, synth_input, repeats=5)
                if med1 is not None and med2 is not None:
                    if med2 >= self.min_latency_floor_ms and med2 >= max(med1, 0.05) * self.latency_threshold:
                        outcome_v1.median_duration_ms = med1
                        outcome_v2.median_duration_ms = med2
                        ratio = med2 / max(med1, 0.05)
                        summary = (
                            f"Latency regression ({ratio:.1f}x slower in v2): "
                            f"v1 median {med1:.2f}ms -> v2 median {med2:.2f}ms"
                        )
                        return (DriftCategory.LATENCY_REGRESSION, f"{ratio:.1f}x_slowdown", summary)
                    if med1 >= self.min_latency_floor_ms and med1 >= max(med2, 0.05) * self.latency_threshold:
                        outcome_v1.median_duration_ms = med1
                        outcome_v2.median_duration_ms = med2
                        ratio = med1 / max(med2, 0.05)
                        summary = (
                            f"Latency shift ({ratio:.1f}x faster in v2 / pathological in v1): "
                            f"v1 median {med1:.2f}ms -> v2 median {med2:.2f}ms"
                        )
                        return (DriftCategory.LATENCY_REGRESSION, f"{ratio:.1f}x_latency_shift", summary)

        return None

    @classmethod
    def _describe_object_state_diff(cls, c1: Any, c2: Any, prefix: str = "", _depth: int = 0) -> str | None:
        if _depth > 3 or not (isinstance(c1, dict) and isinstance(c2, dict)):
            return None
        if c1.get("__t__") in ("list", "tuple") and c2.get("__t__") in ("list", "tuple"):
            v1_list, v2_list = c1.get("v", []), c2.get("v", [])
            item_diffs: list[str] = []
            for idx, (i1, i2) in enumerate(zip(v1_list[:8], v2_list[:8])):
                eq, _ = ObjectNoiseFilter.values_semantically_equivalent(i1, i2)
                if not eq:
                    sub = cls._describe_object_state_diff(i1, i2, prefix=f"{prefix}[{idx}]", _depth=_depth + 1)
                    item_diffs.append(sub or f"{prefix}[{idx}] ({cls._format_tagged_brief(i1)} -> {cls._format_tagged_brief(i2)})")
            return "; ".join(item_diffs[:3]) if item_diffs else None
        if c1.get("__t__") != "object" or c2.get("__t__") != "object":
            return None
        st1 = c1.get("state", {})
        st2 = c2.get("state", {})
        if not isinstance(st1, dict) or not isinstance(st2, dict):
            return None
        diffs: list[str] = []
        all_keys = sorted(set(st1.keys()) | set(st2.keys()))
        for k in all_keys:
            attr_path = f"{prefix}.{k}" if prefix else k
            if k not in st2:
                diffs.append(f"removed public attribute '{attr_path}'")
            elif k not in st1:
                # Only report added attributes if we are inspecting a mutation delta where only one version mutated k
                if prefix == "" and not st1:
                    diffs.append(f"mutated attribute '{attr_path}' in v2 only")
            else:
                eq, _ = ObjectNoiseFilter.values_semantically_equivalent(st1[k], st2[k])
                if not eq:
                    sub1, sub2 = st1[k], st2[k]
                    if (
                        isinstance(sub1, dict)
                        and isinstance(sub2, dict)
                        and sub1.get("__t__") in ("object", "list", "tuple")
                        and sub2.get("__t__") in ("object", "list", "tuple")
                    ):
                        nested = cls._describe_object_state_diff(sub1, sub2, prefix=attr_path, _depth=_depth + 1)
                        if nested:
                            diffs.append(nested)
                            continue
                    v1_s = cls._format_tagged_brief(sub1)
                    v2_s = cls._format_tagged_brief(sub2)
                    diffs.append(f"attribute '{attr_path}' changed ({v1_s} -> {v2_s})")
        if not diffs and c1.get("repr") != c2.get("repr"):
            return f"{prefix or 'object'} repr changed ({c1.get('repr')!r} -> {c2.get('repr')!r})"
        return "; ".join(diffs[:4]) if diffs else None

    @staticmethod
    def _format_tagged_brief(tagged: Any) -> str:
        if not isinstance(tagged, dict):
            return repr(tagged)
        t = tagged.get("__t__")
        if t in ("int", "float", "bool", "str", "decimal"):
            return repr(tagged.get("v"))
        if t == "none":
            return "None"
        if t in ("set", "frozenset", "list", "tuple"):
            items = [
                x.get("v") if isinstance(x, dict) and "v" in x else x
                for x in tagged.get("v", [])
            ]
            return f"{t}({items!r})"
        if "repr" in tagged and tagged["repr"]:
            return repr(tagged["repr"])
        return repr(tagged.get("v", tagged))

    def shrink_input(
        self,
        contract_v1: CallableContract,
        contract_v2: CallableContract,
        failing_input: SynthesizedInput,
        target_category: DriftCategory,
        target_subkind: str | None,
        initial_v1: ExecutionOutcome,
        initial_v2: ExecutionOutcome,
    ) -> tuple[SynthesizedInput, ExecutionOutcome, ExecutionOutcome, int]:
        """Minimize a drift-triggering input to the smallest input that still triggers the same drift."""
        current_input = copy.deepcopy(failing_input)
        best_v1 = initial_v1
        best_v2 = initial_v2
        shrink_steps = 0
        evals_used = 0

        if target_category == DriftCategory.LATENCY_REGRESSION:
            return current_input, best_v1, best_v2, 0

        required_pos_count = sum(
            1
            for p in contract_v1.parameters
            if p.kind in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD") and not p.has_default
        )

        def _test_candidate(cand: SynthesizedInput) -> tuple[bool, ExecutionOutcome, ExecutionOutcome]:
            nonlocal evals_used
            evals_used += 1
            o1 = self.worker_v1.execute_callable(contract_v1, cand)
            o2 = self.worker_v2.execute_callable(contract_v2, cand)
            classification = self.classify_pair(
                contract_v1, contract_v2, cand, o1, o2, allow_benchmark=False
            )
            if classification is not None:
                cat, sub, _ = classification
                if cat == target_category and sub == target_subkind:
                    return True, o1, o2
            return False, o1, o2

        # Phase 0: If stateful method_chain, try shortening the chain first
        while len(current_input.method_chain) > 1 and evals_used < self.max_shrink_evals:
            shortened = False
            for drop_idx in (len(current_input.method_chain) - 1, 0):
                if evals_used >= self.max_shrink_evals:
                    break
                cand = copy.deepcopy(current_input)
                cand.method_chain.pop(drop_idx)
                ok, o1, o2 = _test_candidate(cand)
                if ok:
                    current_input = cand
                    best_v1, best_v2 = o1, o2
                    shrink_steps += 1
                    shortened = True
                    break
            if not shortened:
                break

        # Shrink arguments inside method_chain steps
        for step_idx in range(len(current_input.method_chain)):
            m_name, m_args, m_kw = current_input.method_chain[step_idx]
            for arg_idx in range(len(m_args)):
                for smaller_val in _generate_smaller_values(m_args[arg_idx])[:3]:
                    if evals_used >= self.max_shrink_evals:
                        break
                    cand = copy.deepcopy(current_input)
                    cand.method_chain[step_idx][1][arg_idx] = smaller_val
                    ok, o1, o2 = _test_candidate(cand)
                    if ok:
                        current_input = cand
                        best_v1, best_v2 = o1, o2
                        shrink_steps += 1
                        break

        # Phase 1: Try dropping optional trailing positional args
        while (
            len(current_input.args) > required_pos_count
            and evals_used < self.max_shrink_evals
        ):
            cand = copy.deepcopy(current_input)
            cand.args = cand.args[:-1]
            ok, o1, o2 = _test_candidate(cand)
            if ok:
                current_input = cand
                best_v1, best_v2 = o1, o2
                shrink_steps += 1
            else:
                break

        # Phase 2: Try dropping optional keyword args
        for k in list(current_input.kwargs.keys()):
            if evals_used >= self.max_shrink_evals:
                break
            p_spec = next((p for p in contract_v1.parameters if p.name == k), None)
            if p_spec and p_spec.has_default:
                cand = copy.deepcopy(current_input)
                del cand.kwargs[k]
                ok, o1, o2 = _test_candidate(cand)
                if ok:
                    current_input = cand
                    best_v1, best_v2 = o1, o2
                    shrink_steps += 1

        # Phase 3: Iteratively shrink each positional argument value
        for idx in range(len(current_input.args)):
            improved = True
            while improved and evals_used < self.max_shrink_evals:
                improved = False
                for smaller_val in _generate_smaller_values(current_input.args[idx]):
                    if evals_used >= self.max_shrink_evals:
                        break
                    cand = copy.deepcopy(current_input)
                    cand.args[idx] = smaller_val
                    ok, o1, o2 = _test_candidate(cand)
                    if ok:
                        current_input = cand
                        best_v1, best_v2 = o1, o2
                        shrink_steps += 1
                        improved = True
                        break

        # Phase 4: Iteratively shrink each keyword argument value
        for k in list(current_input.kwargs.keys()):
            improved = True
            while improved and evals_used < self.max_shrink_evals:
                improved = False
                for smaller_val in _generate_smaller_values(current_input.kwargs[k]):
                    if evals_used >= self.max_shrink_evals:
                        break
                    cand = copy.deepcopy(current_input)
                    cand.kwargs[k] = smaller_val
                    ok, o1, o2 = _test_candidate(cand)
                    if ok:
                        current_input = cand
                        best_v1, best_v2 = o1, o2
                        shrink_steps += 1
                        improved = True
                        break

        return current_input, best_v1, best_v2, shrink_steps

    def fuzz_callable_pair(
        self,
        contract_v1: CallableContract,
        contract_v2: CallableContract,
        inputs: list[SynthesizedInput],
    ) -> tuple[list[BehavioralDrift], int]:
        """Run synthesized inputs on (contract_v1, contract_v2) within time budget and record deduplicated drifts."""
        drifts: list[BehavioralDrift] = []
        seen_drift_keys: set[tuple[DriftCategory, str | None, str | None, str | None]] = set()
        executed = 0
        t_start = time.perf_counter()

        for synth_in in inputs:
            if (time.perf_counter() - t_start) > self.target_time_budget_sec:
                break
            if self.max_drifts_per_callable > 0 and len(drifts) >= self.max_drifts_per_callable:
                break

            executed += 1
            out1 = self.worker_v1.execute_callable(contract_v1, synth_in)
            out2 = self.worker_v2.execute_callable(contract_v2, synth_in)

            classification = self.classify_pair(
                contract_v1, contract_v2, synth_in, out1, out2, allow_benchmark=True
            )
            if classification is None:
                continue

            cat, subkind, _ = classification
            dedup_key = (
                cat,
                subkind,
                out1.exception_type or out1.return_type,
                out2.exception_type or out2.return_type,
            )
            if dedup_key in seen_drift_keys:
                continue
            seen_drift_keys.add(dedup_key)

            min_in, min_o1, min_o2, steps = self.shrink_input(
                contract_v1,
                contract_v2,
                synth_in,
                cat,
                subkind,
                out1,
                out2,
            )
            final_class = self.classify_pair(
                contract_v1, contract_v2, min_in, min_o1, min_o2, allow_benchmark=False
            )
            final_summary = final_class[2] if final_class is not None else classification[2]

            drifts.append(
                BehavioralDrift(
                    callable_id=contract_v1.full_id,
                    module=contract_v1.module,
                    qualname=contract_v1.qualname,
                    signature=contract_v1.signature_display(),
                    category=cat,
                    subkind=subkind,
                    original_input=synth_in,
                    minimal_input=min_in,
                    shrink_steps=steps,
                    outcome_v1=min_o1,
                    outcome_v2=min_o2,
                    summary=final_summary,
                    callable_kind=contract_v1.callable_kind,
                )
            )

        return drifts, executed
