"""Static Public API Surface & Contract Comparator (AST + inspect)."""

from __future__ import annotations

import difflib
from verdiff.models import (
    CallableContract,
    ParameterSpec,
    StaticChangeKind,
    StaticDiffEntry,
)


def _compare_parameters(
    params_v1: list[ParameterSpec],
    params_v2: list[ParameterSpec],
) -> tuple[bool, bool, list[str]]:
    """Return (strictly_identical, call_compatible, change_reasons)."""
    reasons: list[str] = []
    if len(params_v1) != len(params_v2):
        reasons.append(f"parameter count changed ({len(params_v1)} -> {len(params_v2)})")
        # Check if v2 only appended optional parameters with defaults
        if len(params_v2) > len(params_v1):
            prefix_match = all(
                p1.name == p2.name and p1.kind == p2.kind
                for p1, p2 in zip(params_v1, params_v2[: len(params_v1)])
            )
            tail_optional = all(p2.has_default for p2 in params_v2[len(params_v1) :])
            return False, (prefix_match and tail_optional), reasons
        return False, False, reasons

    call_compatible = True
    for p1, p2 in zip(params_v1, params_v2):
        if p1.name != p2.name:
            reasons.append(f"parameter '{p1.name}' renamed to '{p2.name}'")
            if p1.kind != "POSITIONAL_ONLY" or p2.kind != "POSITIONAL_ONLY":
                call_compatible = False
        if p1.kind != p2.kind:
            reasons.append(f"parameter '{p1.name}' kind changed ({p1.kind} -> {p2.kind})")
            call_compatible = False
        if p1.has_default != p2.has_default:
            reasons.append(
                f"parameter '{p1.name}' default {'added' if p2.has_default else 'removed'}"
            )
            if p1.has_default and not p2.has_default:
                call_compatible = False
        elif p1.has_default and p1.default_repr != p2.default_repr:
            reasons.append(
                f"parameter '{p1.name}' default value changed ({p1.default_repr} -> {p2.default_repr})"
            )
        if (p1.annotation or None) != (p2.annotation or None):
            reasons.append(
                f"parameter '{p1.name}' type annotation changed ({p1.annotation or 'untyped'} -> {p2.annotation or 'untyped'})"
            )

    return (len(reasons) == 0), call_compatible, reasons


class SurfaceComparator:
    """Compares extracted public API contracts between two versions of a package."""

    @staticmethod
    def compare(
        contracts_v1: list[CallableContract],
        contracts_v2: list[CallableContract],
    ) -> list[StaticDiffEntry]:
        map_v1 = {(c.module, c.qualname): c for c in contracts_v1}
        map_v2 = {(c.module, c.qualname): c for c in contracts_v2}

        common_keys = sorted(set(map_v1.keys()) & set(map_v2.keys()))
        removed_keys = sorted(set(map_v1.keys()) - set(map_v2.keys()))
        added_keys = sorted(set(map_v2.keys()) - set(map_v1.keys()))

        entries: list[StaticDiffEntry] = []

        for key in common_keys:
            c1 = map_v1[key]
            c2 = map_v2[key]
            sig1 = c1.signature_display()
            sig2 = c2.signature_display()

            identical, _, reasons = _compare_parameters(c1.parameters, c2.parameters)
            if (c1.return_annotation or None) != (c2.return_annotation or None):
                identical = False
                reasons.append(
                    f"return annotation changed ({c1.return_annotation or 'untyped'} -> {c2.return_annotation or 'untyped'})"
                )

            if identical:
                entries.append(
                    StaticDiffEntry(
                        kind=StaticChangeKind.UNCHANGED_SIGNATURE,
                        qualname_v1=c1.qualname,
                        qualname_v2=c2.qualname,
                        module=c1.module,
                        signature_v1=sig1,
                        signature_v2=sig2,
                        details="Identical public signature",
                        contract_v1=c1,
                        contract_v2=c2,
                        similarity_score=1.0,
                    )
                )
            else:
                entries.append(
                    StaticDiffEntry(
                        kind=StaticChangeKind.SIGNATURE_CHANGED,
                        qualname_v1=c1.qualname,
                        qualname_v2=c2.qualname,
                        module=c1.module,
                        signature_v1=sig1,
                        signature_v2=sig2,
                        details="; ".join(reasons),
                        contract_v1=c1,
                        contract_v2=c2,
                        similarity_score=0.85,
                    )
                )

        # Detect renames between removed_keys and added_keys
        matched_removed: set[tuple[str, str]] = set()
        matched_added: set[tuple[str, str]] = set()

        for r_key in removed_keys:
            c1 = map_v1[r_key]
            best_match: tuple[tuple[str, str], float, str] | None = None
            for a_key in added_keys:
                if a_key in matched_added:
                    continue
                c2 = map_v2[a_key]
                if c1.callable_kind != c2.callable_kind:
                    continue

                ast_exact = bool(
                    c1.body_ast_fingerprint
                    and c1.body_ast_fingerprint == c2.body_ast_fingerprint
                )
                param_types_1 = [(p.kind, p.annotation, p.has_default) for p in c1.parameters]
                param_types_2 = [(p.kind, p.annotation, p.has_default) for p in c2.parameters]
                params_exact = bool(
                    len(param_types_1) > 0
                    and param_types_1 == param_types_2
                    and c1.return_annotation == c2.return_annotation
                )
                name_sim = difflib.SequenceMatcher(
                    None, c1.qualname.lower(), c2.qualname.lower()
                ).ratio()

                if ast_exact and len(c1.parameters) == len(c2.parameters):
                    score = 0.98
                    reason = f"Renamed '{c1.qualname}' -> '{c2.qualname}' (identical AST body fingerprint)"
                elif params_exact and name_sim >= 0.72 and c1.module == c2.module:
                    score = round(0.50 + (name_sim * 0.50), 2)
                    reason = f"Renamed '{c1.qualname}' -> '{c2.qualname}' (similarity={score:.2f})"
                else:
                    continue

                if best_match is None or score > best_match[1]:
                    best_match = (a_key, score, reason)

            if best_match is not None:
                a_key, score, reason = best_match
                c2 = map_v2[a_key]
                matched_removed.add(r_key)
                matched_added.add(a_key)
                entries.append(
                    StaticDiffEntry(
                        kind=StaticChangeKind.RENAMED,
                        qualname_v1=c1.qualname,
                        qualname_v2=c2.qualname,
                        module=c1.module,
                        signature_v1=c1.signature_display(),
                        signature_v2=c2.signature_display(),
                        details=reason,
                        contract_v1=c1,
                        contract_v2=c2,
                        similarity_score=score,
                    )
                )

        for r_key in removed_keys:
            if r_key in matched_removed:
                continue
            c1 = map_v1[r_key]
            entries.append(
                StaticDiffEntry(
                    kind=StaticChangeKind.REMOVED,
                    qualname_v1=c1.qualname,
                    qualname_v2=None,
                    module=c1.module,
                    signature_v1=c1.signature_display(),
                    signature_v2=None,
                    details=f"Removed public {c1.callable_kind} '{c1.module}.{c1.qualname}'",
                    contract_v1=c1,
                    contract_v2=None,
                    similarity_score=0.0,
                )
            )

        for a_key in added_keys:
            if a_key in matched_added:
                continue
            c2 = map_v2[a_key]
            entries.append(
                StaticDiffEntry(
                    kind=StaticChangeKind.ADDED,
                    qualname_v1=None,
                    qualname_v2=c2.qualname,
                    module=c2.module,
                    signature_v1=None,
                    signature_v2=c2.signature_display(),
                    details=f"Added public {c2.callable_kind} '{c2.module}.{c2.qualname}'",
                    contract_v1=None,
                    contract_v2=c2,
                    similarity_score=0.0,
                )
            )

        return entries

    @staticmethod
    def select_fuzz_targets(
        static_diffs: list[StaticDiffEntry],
    ) -> list[tuple[CallableContract, CallableContract]]:
        """Select call-compatible pairs (v1, v2) for differential fuzzing."""
        targets: list[tuple[CallableContract, CallableContract]] = []
        for entry in static_diffs:
            if entry.contract_v1 is None or entry.contract_v2 is None:
                continue
            if entry.kind == StaticChangeKind.UNCHANGED_SIGNATURE:
                targets.append((entry.contract_v1, entry.contract_v2))
            elif entry.kind == StaticChangeKind.SIGNATURE_CHANGED:
                # Also fuzz functions whose positional/keyword invocation from v1 remains compatible
                _, compat, _ = _compare_parameters(
                    entry.contract_v1.parameters, entry.contract_v2.parameters
                )
                if compat:
                    targets.append((entry.contract_v1, entry.contract_v2))
                elif len(entry.contract_v1.parameters) == len(entry.contract_v2.parameters):
                    # Even if a default value changed, fuzzing with 0-arg or partial-arg inputs exposes the silent default change!
                    kinds_1 = [p.kind for p in entry.contract_v1.parameters]
                    kinds_2 = [p.kind for p in entry.contract_v2.parameters]
                    if kinds_1 == kinds_2:
                        targets.append((entry.contract_v1, entry.contract_v2))
        targets.sort(
            key=lambda pair: (
                0
                if (
                    pair[0].body_ast_fingerprint != pair[1].body_ast_fingerprint
                    or pair[0].callable_kind in ("class", "stateful_chain")
                    or pair[0].parameters != pair[1].parameters
                )
                else 1,
                pair[0].module.count("."),
                pair[0].module,
                pair[0].qualname,
            )
        )
        return targets
