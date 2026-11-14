"""Core data models for VerDiff API extraction, input synthesis, and behavioral diffing."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StaticChangeKind(str, Enum):
    """Classification of static API surface changes between v1 and v2."""

    UNCHANGED_SIGNATURE = "unchanged_signature"
    SIGNATURE_CHANGED = "signature_changed"
    ADDED = "added"
    REMOVED = "removed"
    RENAMED = "renamed"


class DriftCategory(str, Enum):
    """Classification of runtime behavioral discrepancies between v1 and v2."""

    RETURN_VALUE_DRIFT = "return_value_drift"
    EXCEPTION_TYPE_DRIFT = "exception_type_drift"
    INPUT_MUTATION_DRIFT = "input_mutation_drift"
    LATENCY_REGRESSION = "latency_regression"


class ExceptionDriftSubkind(str, Enum):
    """Sub-classification when an exception drift occurs."""

    PASS_TO_FAIL = "pass_to_fail"
    FAIL_TO_PASS = "fail_to_pass"
    EXCEPTION_CLASS_CHANGED = "exception_class_changed"
    CRASH_OR_TIMEOUT = "crash_or_timeout"


@dataclass(frozen=True)
class ParameterSpec:
    """Specification of a single callable parameter."""

    name: str
    kind: str  # POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, VAR_POSITIONAL, KEYWORD_ONLY, VAR_KEYWORD
    annotation: str | None = None
    has_default: bool = False
    default_repr: str | None = None
    default_value_tagged: Any = None


@dataclass
class CallableContract:
    """Extracted contract of a public function, method, class constructor, or stateful call chain."""

    qualname: str
    module: str
    callable_kind: str  # "function", "class", "staticmethod", "classmethod", "method", "stateful_chain"
    parameters: list[ParameterSpec] = field(default_factory=list)
    return_annotation: str | None = None
    docstring_summary: str | None = None
    ast_constants: list[Any] = field(default_factory=list)
    raised_exceptions: list[str] = field(default_factory=list)
    body_ast_fingerprint: str = ""
    class_init_params: list[ParameterSpec] = field(default_factory=list)
    chain_methods: list[dict[str, Any]] = field(default_factory=list)

    @property
    def full_id(self) -> str:
        return f"{self.module}:{self.qualname}"

    def signature_display(self) -> str:
        if self.callable_kind == "stateful_chain":
            m_names = [m.get("name", "?") for m in self.chain_methods[:4]]
            return f"[stateful chain: {', '.join(m_names)}]"

        parts: list[str] = []
        pos_only_seen = False
        kw_only_started = False
        for idx, p in enumerate(self.parameters):
            if p.kind == "POSITIONAL_ONLY":
                pos_only_seen = True
            elif pos_only_seen:
                parts.append("/")
                pos_only_seen = False

            if p.kind == "KEYWORD_ONLY" and not kw_only_started:
                if not any(prev.kind == "VAR_POSITIONAL" for prev in self.parameters[:idx]):
                    parts.append("*")
                kw_only_started = True

            prefix = ""
            if p.kind == "VAR_POSITIONAL":
                prefix = "*"
            elif p.kind == "VAR_KEYWORD":
                prefix = "**"

            piece = f"{prefix}{p.name}"
            if p.annotation:
                piece += f": {p.annotation}"
            if p.has_default and p.default_repr is not None:
                piece += f" = {p.default_repr}"
            parts.append(piece)

        if pos_only_seen:
            parts.append("/")

        ret = f" -> {self.return_annotation}" if self.return_annotation else ""
        return f"({', '.join(parts)}){ret}"


@dataclass
class StaticDiffEntry:
    """Represents a static contract comparison between v1 and v2."""

    kind: StaticChangeKind
    qualname_v1: str | None
    qualname_v2: str | None
    module: str
    signature_v1: str | None
    signature_v2: str | None
    details: str
    contract_v1: CallableContract | None = None
    contract_v2: CallableContract | None = None
    similarity_score: float = 1.0


@dataclass
class SynthesizedInput:
    """A deterministic call vector (or multi-step stateful method chain) for fuzzing."""

    input_id: str
    args: list[Any]
    kwargs: dict[str, Any]
    instance_args: list[Any] = field(default_factory=list)
    instance_kwargs: dict[str, Any] = field(default_factory=dict)
    method_chain: list[tuple[str, list[Any], dict[str, Any]]] = field(default_factory=list)
    source_strategy: str = "edge_case"
    description: str = ""


@dataclass
class ExecutionOutcome:
    """Outcome of executing a single callable or stateful chain in an isolated worker."""

    status: str  # "ok", "exception", "timeout", "crash"
    return_type: str | None = None
    return_repr: str | None = None
    return_canonical: Any = None
    exception_type: str | None = None
    exception_module: str | None = None
    exception_message: str | None = None
    mutated_args_after: Any = None
    mutated_kwargs_after: Any = None
    mutated_instance_after: Any = None
    duration_ms: float = 0.0
    median_duration_ms: float | None = None


@dataclass
class BehavioralDrift:
    """A confirmed runtime behavioral discrepancy between v1 and v2 on identical input."""

    callable_id: str
    module: str
    qualname: str
    signature: str
    category: DriftCategory
    subkind: str | None
    original_input: SynthesizedInput
    minimal_input: SynthesizedInput
    shrink_steps: int
    outcome_v1: ExecutionOutcome
    outcome_v2: ExecutionOutcome
    summary: str
    callable_kind: str = "function"


@dataclass
class DiffReport:
    """Complete differential analysis report for a package across two versions."""

    package: str
    version_v1: str
    version_v2: str
    python_version: str
    seed: int
    total_public_v1: int
    total_public_v2: int
    static_diffs: list[StaticDiffEntry] = field(default_factory=list)
    behavioral_drifts: list[BehavioralDrift] = field(default_factory=list)
    targets_fuzzed: int = 0
    total_inputs_executed: int = 0
    filtered_noise_count: int = 0
    max_drifts_limit: int = 0
    elapsed_seconds: float = 0.0

    @property
    def unchanged_signatures_count(self) -> int:
        return sum(
            1
            for d in self.static_diffs
            if d.kind == StaticChangeKind.UNCHANGED_SIGNATURE
            and (d.contract_v1 is None or d.contract_v1.callable_kind != "stateful_chain")
        )

    @property
    def static_breaking_count(self) -> int:
        return sum(
            1
            for d in self.static_diffs
            if d.kind in (StaticChangeKind.REMOVED, StaticChangeKind.RENAMED, StaticChangeKind.SIGNATURE_CHANGED)
            and (d.contract_v1 is None or d.contract_v1.callable_kind != "stateful_chain")
        )
