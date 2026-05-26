"""End-to-end study registry and resource-estimation schemas."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from pq_cfd.analysis import format_grid_shape
from pq_cfd.types import SimulationResult

EVIDENCE_LADDER = (
    "literature_card",
    "classical_benchmark",
    "operator_state_emulation",
    "explicit_circuit",
    "logical_resource_counts",
    "physical_ft_estimate",
    "end_to_end_classical_comparison",
)
EVIDENCE_STAGE_RANK = {
    stage: index for index, stage in enumerate(EVIDENCE_LADDER)
}

QUANTUM_OPERATOR_STATUSES = ("not_started", "incomplete", "prototype", "complete")

RESOURCE_REQUIRED_ASSUMPTIONS = (
    "state_preparation",
    "timestep",
    "precision",
    "readout",
    "nonlinear_treatment",
    "error_budget",
    "classical_comparison",
)

STUDY_RESULT_CSV_COLUMNS = (
    "algorithm_id",
    "algorithm_name",
    "family",
    "status",
    "evidence_stage",
    "benchmark_id",
    "model",
    "grid_shape",
    "grid_points",
    "steps",
    "tau",
    "amplitude",
    "accuracy_metric",
    "relative_error",
    "mass_drift_relative",
    "stable",
    "runtime_seconds",
    "logical_qubits",
    "circuit_depth",
    "t_count",
    "toffoli_count",
    "ccz_count",
    "rotation_count",
    "measurement_count",
    "timesteps",
    "observable_repetitions",
    "condition_number",
    "block_encoding_normalization",
    "postselection_success_probability",
    "nonlinear_treatment",
    "carleman_truncation_order",
    "precision_bits",
    "error_budget",
    "observable_tolerance",
    "classical_baseline_cost",
    "operator_spec_id",
    "logical_count_provenance",
    "physical_qubits",
    "physical_runtime_seconds",
    "code_distance",
    "t_factories",
    "t_states",
    "failure_budget",
    "physical_estimator",
    "logical_estimate_provenance",
    "state_preparation_assumption",
    "timestep_assumption",
    "precision_assumption",
    "readout_assumption",
    "nonlinear_treatment_assumption",
    "error_budget_assumption",
    "classical_comparison_assumption",
)


@dataclass(frozen=True, slots=True)
class AlgorithmCard:
    """Comparable literature card for a CFD-to-quantum algorithm option."""

    algorithm_id: str
    name: str
    family: str
    route: str
    status: str
    evidence_stage: str
    summary: str
    benchmarks: tuple[str, ...]
    resource_assumptions: tuple[str, ...]
    sources: tuple[str, ...]
    source_date: str
    core_claim: str
    assumptions: tuple[str, ...]
    benchmark_relevance: str
    bottlenecks: tuple[str, ...]
    caveats: tuple[str, ...]
    promotion_blockers: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in (
            "algorithm_id",
            "name",
            "family",
            "route",
            "status",
            "summary",
            "source_date",
            "core_claim",
            "benchmark_relevance",
        ):
            _require_text(name, getattr(self, name))
        if self.evidence_stage not in EVIDENCE_LADDER:
            raise ValueError(f"Unsupported evidence stage: {self.evidence_stage!r}")
        for name in (
            "benchmarks",
            "resource_assumptions",
            "sources",
            "assumptions",
            "bottlenecks",
            "caveats",
            "promotion_blockers",
        ):
            _require_nonempty_sequence(name, getattr(self, name), self.algorithm_id)

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly algorithm-card representation."""

        return {
            "algorithm_id": self.algorithm_id,
            "name": self.name,
            "family": self.family,
            "route": self.route,
            "status": self.status,
            "evidence_stage": self.evidence_stage,
            "summary": self.summary,
            "benchmarks": list(self.benchmarks),
            "resource_assumptions": list(self.resource_assumptions),
            "sources": list(self.sources),
            "source_date": self.source_date,
            "core_claim": self.core_claim,
            "assumptions": list(self.assumptions),
            "benchmark_relevance": self.benchmark_relevance,
            "bottlenecks": list(self.bottlenecks),
            "caveats": list(self.caveats),
            "promotion_blockers": list(self.promotion_blockers),
        }


@dataclass(frozen=True, slots=True)
class BenchmarkProtocol:
    """A benchmark definition shared by classical, operator, and circuit studies."""

    benchmark_id: str
    name: str
    model: str
    initial_condition: str
    purpose: str
    default_grid_shape: tuple[int, ...]
    promotion_metric: str

    def __post_init__(self) -> None:
        _require_text("benchmark_id", self.benchmark_id)
        _require_text("name", self.name)
        _require_text("model", self.model)
        _require_text("initial_condition", self.initial_condition)
        _require_text("purpose", self.purpose)
        _require_text("promotion_metric", self.promotion_metric)
        if any(size <= 0 for size in self.default_grid_shape):
            raise ValueError("default_grid_shape values must be positive.")

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly benchmark-protocol representation."""

        return {
            "benchmark_id": self.benchmark_id,
            "name": self.name,
            "model": self.model,
            "initial_condition": self.initial_condition,
            "purpose": self.purpose,
            "default_grid_shape": list(self.default_grid_shape),
            "promotion_metric": self.promotion_metric,
        }


@dataclass(frozen=True, slots=True)
class QuantumOperatorSpec:
    """Circuit-readiness metadata for a classical or quantum operator model."""

    algorithm_id: str
    benchmark_id: str
    encoding: str
    reversible_embedding_status: str
    block_encoding_status: str
    fixed_point_status: str
    readout_status: str
    error_budget_status: str
    normalization: float | None
    success_probability: float | None
    fixed_point_model: str
    readout_model: str
    operator_provenance: str
    known_gaps: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in (
            "algorithm_id",
            "benchmark_id",
            "encoding",
            "fixed_point_model",
            "readout_model",
            "operator_provenance",
        ):
            _require_text(name, getattr(self, name))
        _validate_status("reversible_embedding_status", self.reversible_embedding_status)
        _validate_status("block_encoding_status", self.block_encoding_status)
        _validate_status("fixed_point_status", self.fixed_point_status)
        _validate_status("readout_status", self.readout_status)
        _validate_status("error_budget_status", self.error_budget_status)
        if self.normalization is None:
            if self.block_encoding_status == "complete":
                raise ValueError("complete block encoding requires normalization.")
        else:
            _require_positive("normalization", self.normalization)
        if self.success_probability is None:
            if self.block_encoding_status == "complete":
                raise ValueError(
                    "complete block encoding requires success_probability."
                )
        else:
            _require_probability("success_probability", self.success_probability)
        if not self.circuit_ready:
            _require_nonempty_sequence("known_gaps", self.known_gaps, self.algorithm_id)

    @property
    def circuit_ready(self) -> bool:
        """Return whether the operator is ready for explicit circuit design."""

        return (
            self.reversible_embedding_status == "complete"
            and self.block_encoding_status == "complete"
            and self.fixed_point_status == "complete"
            and self.readout_status == "complete"
            and self.error_budget_status == "complete"
            and self.normalization is not None
            and self.success_probability is not None
            and not _is_unspecified(self.fixed_point_model)
            and not _is_unspecified(self.readout_model)
            and not self.known_gaps
        )

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly operator specification."""

        return {
            "algorithm_id": self.algorithm_id,
            "benchmark_id": self.benchmark_id,
            "encoding": self.encoding,
            "reversible_embedding_status": self.reversible_embedding_status,
            "block_encoding_status": self.block_encoding_status,
            "fixed_point_status": self.fixed_point_status,
            "readout_status": self.readout_status,
            "error_budget_status": self.error_budget_status,
            "normalization": self.normalization,
            "success_probability": self.success_probability,
            "fixed_point_model": self.fixed_point_model,
            "readout_model": self.readout_model,
            "operator_provenance": self.operator_provenance,
            "known_gaps": list(self.known_gaps),
            "circuit_ready": self.circuit_ready,
        }


@dataclass(frozen=True, slots=True)
class LogicalResourceEstimate:
    """Architecture-independent logical counts plus QCFD bottleneck metadata."""

    algorithm_id: str
    benchmark_id: str
    lattice_bits: int
    velocity_bits: int
    ancilla_qubits: int
    logical_qubits: int
    circuit_depth: int
    t_count: int
    toffoli_count: int
    ccz_count: int
    rotation_count: int
    measurement_count: int
    timesteps: int
    observable_repetitions: int
    condition_number: float
    block_encoding_normalization: float
    postselection_success_probability: float
    nonlinear_treatment: str
    carleman_truncation_order: int | None
    precision_bits: int
    error_budget: float
    observable_tolerance: float
    classical_baseline_cost: float
    operator_spec_id: str
    logical_count_provenance: str
    assumptions: Mapping[str, str]

    def __post_init__(self) -> None:
        _require_text("algorithm_id", self.algorithm_id)
        _require_text("benchmark_id", self.benchmark_id)
        _require_text("nonlinear_treatment", self.nonlinear_treatment)
        _require_text("operator_spec_id", self.operator_spec_id)
        _require_text("logical_count_provenance", self.logical_count_provenance)
        for name in (
            "lattice_bits",
            "velocity_bits",
            "ancilla_qubits",
            "logical_qubits",
            "circuit_depth",
            "t_count",
            "toffoli_count",
            "ccz_count",
            "rotation_count",
            "measurement_count",
            "timesteps",
            "observable_repetitions",
            "precision_bits",
        ):
            _require_nonnegative_int(name, getattr(self, name))
        _require_positive("condition_number", self.condition_number)
        _require_positive(
            "block_encoding_normalization",
            self.block_encoding_normalization,
        )
        _require_probability(
            "postselection_success_probability",
            self.postselection_success_probability,
        )
        if self.carleman_truncation_order is not None:
            _require_nonnegative_int(
                "carleman_truncation_order",
                self.carleman_truncation_order,
            )
        _require_positive("error_budget", self.error_budget)
        _require_positive("observable_tolerance", self.observable_tolerance)
        if self.classical_baseline_cost < 0.0:
            raise ValueError("classical_baseline_cost must be non-negative.")
        missing = [
            key
            for key in RESOURCE_REQUIRED_ASSUMPTIONS
            if not str(self.assumptions.get(key, "")).strip()
        ]
        if missing:
            raise ValueError(
                "resource estimates require assumptions for: "
                + ", ".join(missing)
            )

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly logical resource estimate."""

        return {
            "algorithm_id": self.algorithm_id,
            "benchmark_id": self.benchmark_id,
            "lattice_bits": self.lattice_bits,
            "velocity_bits": self.velocity_bits,
            "ancilla_qubits": self.ancilla_qubits,
            "logical_qubits": self.logical_qubits,
            "circuit_depth": self.circuit_depth,
            "t_count": self.t_count,
            "toffoli_count": self.toffoli_count,
            "ccz_count": self.ccz_count,
            "rotation_count": self.rotation_count,
            "measurement_count": self.measurement_count,
            "timesteps": self.timesteps,
            "observable_repetitions": self.observable_repetitions,
            "condition_number": self.condition_number,
            "block_encoding_normalization": self.block_encoding_normalization,
            "postselection_success_probability": (
                self.postselection_success_probability
            ),
            "nonlinear_treatment": self.nonlinear_treatment,
            "carleman_truncation_order": self.carleman_truncation_order,
            "precision_bits": self.precision_bits,
            "error_budget": self.error_budget,
            "observable_tolerance": self.observable_tolerance,
            "classical_baseline_cost": self.classical_baseline_cost,
            "operator_spec_id": self.operator_spec_id,
            "logical_count_provenance": self.logical_count_provenance,
            "assumptions": dict(self.assumptions),
        }


@dataclass(frozen=True, slots=True)
class PhysicalResourceEstimate:
    """Azure-style physical resource-estimator output fields."""

    algorithm_id: str
    benchmark_id: str
    physical_qubits: int
    logical_qubits: int
    runtime_seconds: float
    code_distance: int
    t_factories: int
    t_states: int
    failure_budget: float
    physical_estimator: str
    logical_estimate_provenance: str

    def __post_init__(self) -> None:
        _require_text("algorithm_id", self.algorithm_id)
        _require_text("benchmark_id", self.benchmark_id)
        _require_text("physical_estimator", self.physical_estimator)
        _require_text("logical_estimate_provenance", self.logical_estimate_provenance)
        for name in ("physical_qubits", "logical_qubits", "code_distance"):
            _require_positive_int(name, getattr(self, name))
        for name in ("t_factories", "t_states"):
            _require_nonnegative_int(name, getattr(self, name))
        if self.runtime_seconds <= 0.0:
            raise ValueError("runtime_seconds must be positive.")
        _require_probability("failure_budget", self.failure_budget)

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly physical resource estimate."""

        return {
            "algorithm_id": self.algorithm_id,
            "benchmark_id": self.benchmark_id,
            "physical_qubits": self.physical_qubits,
            "logical_qubits": self.logical_qubits,
            "runtime_seconds": self.runtime_seconds,
            "code_distance": self.code_distance,
            "t_factories": self.t_factories,
            "t_states": self.t_states,
            "failure_budget": self.failure_budget,
            "physical_estimator": self.physical_estimator,
            "logical_estimate_provenance": self.logical_estimate_provenance,
        }


@dataclass(frozen=True, slots=True)
class StudyResultRecord:
    """Unified row for classical diagnostics and optional resource counts."""

    algorithm_id: str
    algorithm_name: str
    family: str
    status: str
    evidence_stage: str
    benchmark_id: str
    model: str
    grid_shape: tuple[int, ...]
    grid_points: int
    steps: int
    tau: float
    amplitude: float
    accuracy_metric: str
    relative_error: float
    mass_drift_relative: float
    stable: bool
    runtime_seconds: float
    resource_estimate: LogicalResourceEstimate | None = None
    physical_estimate: PhysicalResourceEstimate | None = None

    @classmethod
    def from_simulation(
        cls,
        *,
        card: AlgorithmCard,
        benchmark_id: str,
        result: SimulationResult,
        accuracy_metric: str,
        stable: bool,
        resource_estimate: LogicalResourceEstimate | None = None,
        physical_estimate: PhysicalResourceEstimate | None = None,
    ) -> "StudyResultRecord":
        """Create a study row from a solver result."""

        _validate_estimate_stage(
            card,
            resource_estimate=resource_estimate,
            physical_estimate=physical_estimate,
        )
        return cls(
            algorithm_id=card.algorithm_id,
            algorithm_name=card.name,
            family=card.family,
            status=card.status,
            evidence_stage=card.evidence_stage,
            benchmark_id=benchmark_id,
            model=result.model,
            grid_shape=tuple(result.config.grid_shape),
            grid_points=int(np.prod(result.config.grid_shape)),
            steps=result.config.steps,
            tau=result.config.tau,
            amplitude=result.config.amplitude,
            accuracy_metric=accuracy_metric,
            relative_error=float(result.metrics[accuracy_metric]),
            mass_drift_relative=float(result.metrics["mass_drift_relative"]),
            stable=stable,
            runtime_seconds=float(result.metrics["runtime_seconds"]),
            resource_estimate=resource_estimate,
            physical_estimate=physical_estimate,
        )

    def as_dict(self) -> dict[str, Any]:
        """Return a CSV-friendly row with stable columns."""

        estimate = self.resource_estimate
        physical = self.physical_estimate
        assumptions = estimate.assumptions if estimate is not None else {}
        return {
            "algorithm_id": self.algorithm_id,
            "algorithm_name": self.algorithm_name,
            "family": self.family,
            "status": self.status,
            "evidence_stage": self.evidence_stage,
            "benchmark_id": self.benchmark_id,
            "model": self.model,
            "grid_shape": format_grid_shape(self.grid_shape),
            "grid_points": self.grid_points,
            "steps": self.steps,
            "tau": self.tau,
            "amplitude": self.amplitude,
            "accuracy_metric": self.accuracy_metric,
            "relative_error": self.relative_error,
            "mass_drift_relative": self.mass_drift_relative,
            "stable": self.stable,
            "runtime_seconds": self.runtime_seconds,
            "logical_qubits": _resource_value(estimate, "logical_qubits"),
            "circuit_depth": _resource_value(estimate, "circuit_depth"),
            "t_count": _resource_value(estimate, "t_count"),
            "toffoli_count": _resource_value(estimate, "toffoli_count"),
            "ccz_count": _resource_value(estimate, "ccz_count"),
            "rotation_count": _resource_value(estimate, "rotation_count"),
            "measurement_count": _resource_value(estimate, "measurement_count"),
            "timesteps": _resource_value(estimate, "timesteps"),
            "observable_repetitions": _resource_value(
                estimate,
                "observable_repetitions",
            ),
            "condition_number": _resource_value(estimate, "condition_number"),
            "block_encoding_normalization": _resource_value(
                estimate,
                "block_encoding_normalization",
            ),
            "postselection_success_probability": _resource_value(
                estimate,
                "postselection_success_probability",
            ),
            "nonlinear_treatment": _resource_value(estimate, "nonlinear_treatment"),
            "carleman_truncation_order": _resource_value(
                estimate,
                "carleman_truncation_order",
            ),
            "precision_bits": _resource_value(estimate, "precision_bits"),
            "error_budget": _resource_value(estimate, "error_budget"),
            "observable_tolerance": _resource_value(
                estimate,
                "observable_tolerance",
            ),
            "classical_baseline_cost": _resource_value(
                estimate,
                "classical_baseline_cost",
            ),
            "operator_spec_id": _resource_value(estimate, "operator_spec_id"),
            "logical_count_provenance": _resource_value(
                estimate,
                "logical_count_provenance",
            ),
            "physical_qubits": _resource_value(physical, "physical_qubits"),
            "physical_runtime_seconds": _resource_value(physical, "runtime_seconds"),
            "code_distance": _resource_value(physical, "code_distance"),
            "t_factories": _resource_value(physical, "t_factories"),
            "t_states": _resource_value(physical, "t_states"),
            "failure_budget": _resource_value(physical, "failure_budget"),
            "physical_estimator": _resource_value(physical, "physical_estimator"),
            "logical_estimate_provenance": _resource_value(
                physical,
                "logical_estimate_provenance",
            ),
            "state_preparation_assumption": assumptions.get("state_preparation", ""),
            "timestep_assumption": assumptions.get("timestep", ""),
            "precision_assumption": assumptions.get("precision", ""),
            "readout_assumption": assumptions.get("readout", ""),
            "nonlinear_treatment_assumption": assumptions.get(
                "nonlinear_treatment",
                "",
            ),
            "error_budget_assumption": assumptions.get("error_budget", ""),
            "classical_comparison_assumption": assumptions.get(
                "classical_comparison",
                "",
            ),
        }


def default_algorithm_registry() -> tuple[AlgorithmCard, ...]:
    """Return the initial registry of classical and quantum CFD options."""

    return (
        _card(
            algorithm_id="d2q9_bgk_srt",
            name="D2Q9 BGK/SRT",
            family="classical_lbm",
            route="classical_baseline",
            status="implemented",
            evidence_stage="classical_benchmark",
            summary="Baseline periodic Taylor-Green D2Q9 solver.",
            benchmarks=("d2q9_taylor_green",),
            resource_assumptions=("streaming permutation", "local SRT collision"),
            sources=("https://docs.tclb.io/models/flow/d2q9/d2q9/",),
            source_date="living documentation",
            core_claim="Simple validated LBM baseline for periodic low-Mach flow.",
            assumptions=("periodic boundaries", "low Mach", "single relaxation time"),
            benchmark_relevance="Reference implementation for D2Q9 Taylor-Green.",
            bottlenecks=("weak observed velocity order", "compressibility artifacts"),
            caveats=("not a quantum algorithm", "not boundary validated"),
            promotion_blockers=("operator/resource model not specified",),
        ),
        _card(
            algorithm_id="d2q9_barred_srt",
            name="D2Q9 barred-variable SRT",
            family="classical_lbm",
            route="classical_variant",
            status="implemented",
            evidence_stage="classical_benchmark",
            summary="Trapezoidal transformed-distribution SRT formulation.",
            benchmarks=("d2q9_taylor_green",),
            resource_assumptions=("barred populations", "local SRT collision"),
            sources=("https://www.mcs.anl.gov/uploads/cels/papers/P1515.pdf",),
            source_date="2006 reference report",
            core_claim="Barred variables remove implicit trapezoidal collision terms.",
            assumptions=("unforced periodic flow in current implementation",),
            benchmark_relevance="Bookkeeping prototype for transformed distributions.",
            bottlenecks=("forcing and boundary terms not implemented",),
            caveats=("BGK-equivalent for current equilibrium-initialized benchmark",),
            promotion_blockers=("needs forced or non-equilibrium validation",),
        ),
        _card(
            algorithm_id="d2q9_trt",
            name="D2Q9 TRT",
            family="classical_lbm",
            route="classical_variant",
            status="implemented",
            evidence_stage="classical_benchmark",
            summary="Two-relaxation-time D2Q9 collision with tunable odd modes.",
            benchmarks=("d2q9_taylor_green",),
            resource_assumptions=("even/odd mode split", "local collision"),
            sources=("https://www.sciencedirect.com/science/article/pii/S0378437117311275",),
            source_date="2018 article",
            core_claim="Separating symmetric and antisymmetric relaxation can improve stability.",
            assumptions=("magic-parameter odd relaxation",),
            benchmark_relevance="Smallest implemented step beyond SRT.",
            bottlenecks=("odd-mode choice affects stability and boundaries",),
            caveats=("not yet boundary validated",),
            promotion_blockers=("needs mode-relaxation and convergence evidence",),
        ),
        _card(
            algorithm_id="d2q9_mrt",
            name="D2Q9 MRT",
            family="classical_lbm",
            route="classical_variant",
            status="implemented",
            evidence_stage="classical_benchmark",
            summary="Raw-moment multiple-relaxation-time D2Q9 collision.",
            benchmarks=("d2q9_taylor_green",),
            resource_assumptions=("moment transform", "mode-wise relaxation"),
            sources=("https://pubmed.ncbi.nlm.nih.gov/11088335/",),
            source_date="2000 article",
            core_claim="Moment-space relaxation improves stability through independent modes.",
            assumptions=("Lallemand-Luo-style raw moments",),
            benchmark_relevance="Tests whether extra local transforms help enough to justify cost.",
            bottlenecks=("moment transforms complicate future reversible circuits",),
            caveats=("relaxation spectrum is a default, not optimized",),
            promotion_blockers=("needs moment-regression and convergence evidence",),
        ),
        _card(
            algorithm_id="d2q9_incompressible_equilibrium",
            name="D2Q9 incompressible equilibrium",
            family="classical_lbm",
            route="classical_variant",
            status="literature_card",
            evidence_stage="literature_card",
            summary="Low-Mach equilibrium variant aimed at reducing density artifacts.",
            benchmarks=("d2q9_taylor_green",),
            resource_assumptions=("modified equilibrium", "macroscopic reconstruction"),
            sources=("https://www.sciencedirect.com/science/article/abs/pii/S0021999120304873",),
            source_date="2020 article",
            core_claim="Incompressible-equilibrium forms can reduce compressibility error.",
            assumptions=("low-Mach hydrodynamic regime",),
            benchmark_relevance="Relevant if density fluctuations dominate TGV error.",
            bottlenecks=("changes equilibrium and observables",),
            caveats=("not implemented",),
            promotion_blockers=("needs evidence density error is the bottleneck",),
        ),
        _card(
            algorithm_id="d2q9_central_moment_cumulant",
            name="D2Q9 central-moment/cumulant LBM",
            family="classical_lbm",
            route="classical_variant",
            status="literature_card",
            evidence_stage="literature_card",
            summary="Moment-space stabilization route for accuracy and stability studies.",
            benchmarks=("d2q9_taylor_green",),
            resource_assumptions=("central moments", "moment transforms", "relaxation map"),
            sources=("https://www.sciencedirect.com/science/article/pii/S0045793018301889",),
            source_date="2018 article",
            core_claim="Central moments and cumulants can improve stability and Galilean behavior.",
            assumptions=("more complex local transforms",),
            benchmark_relevance="Relevant only after MRT/TRT show a concrete gap.",
            bottlenecks=("higher arithmetic cost", "harder reversible embedding"),
            caveats=("not implemented",),
            promotion_blockers=("needs identified stability bottleneck",),
        ),
        _card(
            algorithm_id="d2q9_entropic_regularized",
            name="D2Q9 entropic/regularized LBM",
            family="classical_lbm",
            route="classical_variant",
            status="literature_card",
            evidence_stage="literature_card",
            summary="Stabilized LBM family to revisit if SRT/TRT/MRT fail at target regimes.",
            benchmarks=("d2q9_taylor_green",),
            resource_assumptions=("entropy solve or regularization", "extra local work"),
            sources=("https://www.sciencedirect.com/science/article/pii/S0045793023001093",),
            source_date="2023 article",
            core_claim="Entropy or regularization can stabilize non-equilibrium modes.",
            assumptions=("nonlinear local stabilization",),
            benchmark_relevance="Relevant for unstable regimes, not current low-Mach TGV.",
            bottlenecks=("nonlinear local solves", "precision sensitivity"),
            caveats=("not implemented",),
            promotion_blockers=("needs target regime where simpler schemes fail",),
        ),
        _card(
            algorithm_id="d1q3_classical_operator_emulation",
            name="D1Q3 classical operator emulation",
            family="operator_emulation",
            route="quantum_prep",
            status="implemented",
            evidence_stage="operator_state_emulation",
            summary="Flattened populations with classical collision and streaming operators.",
            benchmarks=("d1q3_diffusion",),
            resource_assumptions=("statevector populations", "permutation streaming"),
            sources=("https://arxiv.org/abs/2411.19439",),
            source_date="2024-11 arXiv preprint",
            core_claim="D1Q3 exposes the minimal streaming/collision structure.",
            assumptions=("classical dense dissipative collision matrix",),
            benchmark_relevance="First equivalence target before reversible embedding.",
            bottlenecks=("not unitary", "not block encoded", "no readout model"),
            caveats=("not a quantum operator model yet",),
            promotion_blockers=("needs reversible or block-encoded construction",),
        ),
        _card(
            algorithm_id="qlbm",
            name="Quantum Lattice Boltzmann Method",
            family="quantum_algorithm",
            route="qlbm",
            status="literature_card",
            evidence_stage="literature_card",
            summary="Quantum circuit route based on lattice streaming/collision structure.",
            benchmarks=("d1q3_diffusion", "d2q9_taylor_green"),
            resource_assumptions=("state preparation", "readout", "timestep depth"),
            sources=("https://arxiv.org/abs/2411.19439",),
            source_date="2024-11 arXiv preprint",
            core_claim="LBM structure can be mapped to quantum circuit components.",
            assumptions=("efficient encoding", "manageable readout", "repeatable timesteps"),
            benchmark_relevance="Primary quantum route for lattice formulations.",
            bottlenecks=("data encoding", "observable readout", "timestep depth"),
            caveats=("resource advantage not established",),
            promotion_blockers=("needs operator spec and logical counts",),
        ),
        _card(
            algorithm_id="qlbm_no_reinit",
            name="No-reinitialization QLBM",
            family="quantum_algorithm",
            route="qlbm",
            status="literature_card",
            evidence_stage="literature_card",
            summary="QLBM branch focused on avoiding repeated state reinitialization.",
            benchmarks=("d1q3_diffusion",),
            resource_assumptions=("state reuse", "readout", "observable extraction"),
            sources=("https://arxiv.org/abs/2510.05965",),
            source_date="2025-10 arXiv preprint",
            core_claim="Avoiding repeated reinitialization can reduce cost for linear transport.",
            assumptions=("linear advection-diffusion scope",),
            benchmark_relevance="Applicable to D1Q3-style linear transport only for now.",
            bottlenecks=("not yet nonlinear D2Q9 evidence", "readout still required"),
            caveats=("not registered for D2Q9 Taylor-Green until supported",),
            promotion_blockers=("needs nonlinear-flow applicability evidence",),
        ),
        _card(
            algorithm_id="carleman_lbm",
            name="Carleman-LBM",
            family="quantum_algorithm",
            route="linearized_nonlinear_dynamics",
            status="literature_card",
            evidence_stage="literature_card",
            summary="Linear embedding route for nonlinear LBM dynamics.",
            benchmarks=("d2q9_taylor_green",),
            resource_assumptions=("Carleman truncation", "condition number", "readout"),
            sources=("https://arxiv.org/abs/2303.16550",),
            source_date="2023-03 arXiv preprint",
            core_claim="Carleman linearization may expose quantum advantage regimes.",
            assumptions=("finite truncation", "controlled condition number"),
            benchmark_relevance="Candidate nonlinear D2Q9 quantum route.",
            bottlenecks=("truncation order", "condition number", "readout"),
            caveats=("end-to-end advantage depends on regime and observables",),
            promotion_blockers=("needs truncation and conditioning estimates",),
        ),
        _card(
            algorithm_id="direct_navier_stokes",
            name="Direct Navier-Stokes quantum algorithm",
            family="quantum_algorithm",
            route="direct_pde",
            status="literature_card",
            evidence_stage="literature_card",
            summary="Direct governing-equation route with stronger oracle assumptions.",
            benchmarks=("future_pressure_flow",),
            resource_assumptions=("oracles", "linearization", "readout"),
            sources=("https://www.nature.com/articles/s41534-020-00291-0",),
            source_date="2020 article",
            core_claim="Direct quantum treatment of Navier-Stokes can solve restricted flows.",
            assumptions=("problem-specific oracle structure", "restricted nonlinearity"),
            benchmark_relevance="Longer-term comparison branch, not current LBM route.",
            bottlenecks=("oracle assumptions", "nonlinearity", "readout"),
            caveats=("not a general CFD workflow",),
            promotion_blockers=("needs benchmark-specific formulation",),
        ),
        _card(
            algorithm_id="hybrid_pressure_poisson",
            name="Hybrid pressure-Poisson solve",
            family="hybrid_quantum_classical",
            route="linear_subproblem",
            status="literature_card",
            evidence_stage="literature_card",
            summary="Use quantum linear solvers for pressure or elliptic substeps.",
            benchmarks=("future_cavity",),
            resource_assumptions=("linear-system encoding", "iterations", "readout"),
            sources=("https://arxiv.org/abs/2406.00280",),
            source_date="2024-06 arXiv preprint",
            core_claim="Quantum linear solvers may accelerate pressure-like subproblems.",
            assumptions=("efficient matrix encoding", "conditioned linear systems"),
            benchmark_relevance="Relevant when boundaries and pressure solves are added.",
            bottlenecks=("state preparation", "condition number", "classical coupling"),
            caveats=("not used by current periodic LBM benchmark",),
            promotion_blockers=("needs pressure-flow benchmark",),
        ),
        _card(
            algorithm_id="spectral_transport",
            name="Spectral quantum transport",
            family="quantum_algorithm",
            route="spectral_transport",
            status="literature_card",
            evidence_stage="literature_card",
            summary="Spectral route for passive scalar or transport subproblems.",
            benchmarks=("d1q3_diffusion",),
            resource_assumptions=("Fourier encoding", "Hamiltonian simulation", "readout"),
            sources=("https://www.nature.com/articles/s41598-025-27219-y",),
            source_date="2025 article",
            core_claim="Spectral encodings can target simple transport dynamics.",
            assumptions=("Fourier-friendly boundary conditions",),
            benchmark_relevance="Alternative for D1Q3-like linear transport.",
            bottlenecks=("state preparation", "observable reconstruction"),
            caveats=("not a full nonlinear CFD route",),
            promotion_blockers=("needs direct comparison to D1Q3 operator emulation",),
        ),
    )


def default_benchmark_protocols() -> tuple[BenchmarkProtocol, ...]:
    """Return the starting benchmark protocols for the study framework."""

    return (
        BenchmarkProtocol(
            benchmark_id="d1q3_diffusion",
            name="D1Q3 periodic diffusion/advection-diffusion",
            model="D1Q3",
            initial_condition="sinusoidal",
            purpose="Minimal streaming/collision/operator mapping benchmark.",
            default_grid_shape=(128,),
            promotion_metric="relative_l2_error_density",
        ),
        BenchmarkProtocol(
            benchmark_id="d2q9_taylor_green",
            name="D2Q9 periodic Taylor-Green vortex",
            model="D2Q9",
            initial_condition="taylor_green",
            purpose="Periodic 2D flow validation without boundary-condition ambiguity.",
            default_grid_shape=(64, 64),
            promotion_metric="relative_l2_error_velocity",
        ),
        BenchmarkProtocol(
            benchmark_id="future_cavity",
            name="Future lid-driven cavity or pressure-flow benchmark",
            model="D2Q9/D3Q19",
            initial_condition="boundary_driven",
            purpose="Deferred boundary-condition and pressure-solve comparison.",
            default_grid_shape=(64, 64),
            promotion_metric="velocity_profile_error",
        ),
        BenchmarkProtocol(
            benchmark_id="future_pressure_flow",
            name="Future pressure-driven flow benchmark",
            model="D2Q9/D3Q19/Navier-Stokes",
            initial_condition="pressure_driven",
            purpose="Deferred direct-PDE and hybrid pressure-solve comparison.",
            default_grid_shape=(64, 64),
            promotion_metric="pressure_velocity_profile_error",
        ),
    )


def default_quantum_operator_specs() -> tuple[QuantumOperatorSpec, ...]:
    """Return current operator specs and explicit quantum-readiness gaps."""

    return (
        QuantumOperatorSpec(
            algorithm_id="d1q3_classical_operator_emulation",
            benchmark_id="d1q3_diffusion",
            encoding="classical velocity-major population vector",
            reversible_embedding_status="incomplete",
            block_encoding_status="not_started",
            fixed_point_status="not_started",
            readout_status="not_started",
            error_budget_status="not_started",
            normalization=None,
            success_probability=None,
            fixed_point_model="not specified",
            readout_model="direct classical array readout only",
            operator_provenance="classical D1Q3 step-equivalence tests only",
            known_gaps=(
                "collision matrix is dissipative rather than unitary",
                "no reversible dilation or block encoding",
                "no fixed-point arithmetic or observable readout cost",
            ),
        ),
    )


def promotion_rules() -> tuple[str, ...]:
    """Return the promotion gates for moving options up the evidence ladder."""

    return (
        "Every serious option receives a literature card before implementation.",
        "Classical variants must solve a shared benchmark with finite diagnostics.",
        "Operator emulation must distinguish classical equivalence from quantum readiness.",
        "Circuit work requires a reversible or block-encoded operator specification.",
        "Resource estimation requires state-prep, timestep, precision, readout, conditioning, normalization, success-probability, and classical-comparison assumptions.",
    )


def validate_algorithm_registry(
    cards: tuple[AlgorithmCard, ...] | list[AlgorithmCard] | None = None,
) -> tuple[AlgorithmCard, ...]:
    """Validate registry uniqueness and return cards."""

    registry = tuple(default_algorithm_registry() if cards is None else cards)
    seen: set[str] = set()
    for card in registry:
        if card.algorithm_id in seen:
            raise ValueError(f"Duplicate algorithm_id: {card.algorithm_id}")
        seen.add(card.algorithm_id)
    return registry


def write_algorithm_registry_json(
    cards: tuple[AlgorithmCard, ...] | list[AlgorithmCard],
    path: str | Path,
) -> Path:
    """Write algorithm cards to JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [card.as_dict() for card in cards]
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def write_study_records_csv(
    records: list[StudyResultRecord] | tuple[StudyResultRecord, ...],
    path: str | Path,
) -> Path:
    """Write unified study records to CSV."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=STUDY_RESULT_CSV_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(record.as_dict())
    return output_path


def _validate_estimate_stage(
    card: AlgorithmCard,
    *,
    resource_estimate: LogicalResourceEstimate | None,
    physical_estimate: PhysicalResourceEstimate | None,
) -> None:
    evidence_rank = EVIDENCE_STAGE_RANK[card.evidence_stage]
    if resource_estimate is not None:
        if evidence_rank < EVIDENCE_STAGE_RANK["logical_resource_counts"]:
            raise ValueError(
                "logical resource estimates require evidence stage "
                "'logical_resource_counts' or later."
            )
        if resource_estimate.algorithm_id != card.algorithm_id:
            raise ValueError("logical resource estimate algorithm_id mismatch.")
    if physical_estimate is not None:
        if resource_estimate is None:
            raise ValueError("physical estimates require a logical estimate.")
        if evidence_rank < EVIDENCE_STAGE_RANK["physical_ft_estimate"]:
            raise ValueError(
                "physical estimates require evidence stage "
                "'physical_ft_estimate' or later."
            )
        if physical_estimate.algorithm_id != card.algorithm_id:
            raise ValueError("physical resource estimate algorithm_id mismatch.")


def _card(**kwargs: Any) -> AlgorithmCard:
    return AlgorithmCard(**kwargs)


def _resource_value(
    estimate: object | None,
    attribute: str,
) -> int | float | str:
    if estimate is None:
        return ""
    value = getattr(estimate, attribute)
    return "" if value is None else value


def _validate_status(name: str, value: str) -> None:
    if value not in QUANTUM_OPERATOR_STATUSES:
        raise ValueError(f"{name} must be one of {QUANTUM_OPERATOR_STATUSES}.")


def _require_text(name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must be non-empty.")


def _require_nonempty_sequence(
    name: str,
    values: tuple[str, ...],
    algorithm_id: str,
) -> None:
    if not values or any(not str(value).strip() for value in values):
        raise ValueError(f"{algorithm_id} must declare non-empty {name}.")


def _require_nonnegative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer.")


def _require_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")


def _require_positive(name: str, value: float) -> None:
    if value <= 0.0:
        raise ValueError(f"{name} must be positive.")


def _require_probability(name: str, value: float) -> None:
    if value <= 0.0 or value > 1.0:
        raise ValueError(f"{name} must be in (0, 1].")


def _is_unspecified(value: str) -> bool:
    return value.strip().lower() in {"", "not specified", "unknown", "none"}
