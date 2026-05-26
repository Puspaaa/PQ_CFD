import csv
import json
from dataclasses import replace

import pytest

from pq_cfd import (
    RESOURCE_REQUIRED_ASSUMPTIONS,
    STUDY_RESULT_CSV_COLUMNS,
    LogicalResourceEstimate,
    PhysicalResourceEstimate,
    QuantumOperatorSpec,
    SimulationConfig,
    StudyResultRecord,
    default_algorithm_registry,
    default_benchmark_protocols,
    default_quantum_operator_specs,
    run_d2q9_barred_srt,
    validate_algorithm_registry,
    write_algorithm_registry_json,
    write_study_records_csv,
)


def test_algorithm_registry_cards_have_required_fields_and_status() -> None:
    registry = validate_algorithm_registry()

    assert len(registry) >= 10
    for card in registry:
        row = card.as_dict()
        assert row["algorithm_id"]
        assert row["name"]
        assert row["family"]
        assert row["status"]
        assert row["evidence_stage"]
        assert row["benchmarks"]
        assert row["resource_assumptions"]
        assert row["sources"]
        assert row["source_date"]
        assert row["core_claim"]
        assert row["assumptions"]
        assert row["benchmark_relevance"]
        assert row["bottlenecks"]
        assert row["caveats"]
        assert row["promotion_blockers"]

    no_reinit = next(card for card in registry if card.algorithm_id == "qlbm_no_reinit")
    assert no_reinit.benchmarks == ("d1q3_diffusion",)


def test_benchmark_protocols_have_stable_defaults() -> None:
    protocols = default_benchmark_protocols()
    ids = {protocol.benchmark_id for protocol in protocols}

    assert "d1q3_diffusion" in ids
    assert "d2q9_taylor_green" in ids
    assert all(protocol.promotion_metric for protocol in protocols)


def test_resource_estimate_requires_core_assumptions() -> None:
    valid_assumptions = {
        "state_preparation": "basis-state load only",
        "timestep": "one logical block per LBM step",
        "precision": "16 fixed-point bits",
        "readout": "density and velocity observables",
        "nonlinear_treatment": "linear D1Q3 benchmark",
        "error_budget": "single aggregate logical error budget",
        "classical_comparison": "compare against NumPy baseline runtime",
    }

    estimate = LogicalResourceEstimate(
        algorithm_id="d1q3_classical_operator_emulation",
        benchmark_id="d1q3_diffusion",
        lattice_bits=7,
        velocity_bits=2,
        ancilla_qubits=5,
        logical_qubits=20,
        circuit_depth=100,
        t_count=50,
        toffoli_count=10,
        ccz_count=0,
        rotation_count=5,
        measurement_count=4,
        timesteps=10,
        observable_repetitions=100,
        condition_number=1.0,
        block_encoding_normalization=1.0,
        postselection_success_probability=0.5,
        nonlinear_treatment="linear",
        carleman_truncation_order=None,
        precision_bits=16,
        error_budget=1e-6,
        observable_tolerance=1e-3,
        classical_baseline_cost=0.01,
        operator_spec_id="d1q3_classical_operator_emulation:d1q3_diffusion",
        logical_count_provenance="hand-estimate test fixture",
        assumptions=valid_assumptions,
    )

    assert tuple(valid_assumptions) == RESOURCE_REQUIRED_ASSUMPTIONS
    assert estimate.as_dict()["logical_qubits"] == 20

    incomplete = dict(valid_assumptions)
    incomplete.pop("readout")
    with pytest.raises(ValueError):
        LogicalResourceEstimate(
            algorithm_id="d1q3_classical_operator_emulation",
            benchmark_id="d1q3_diffusion",
            lattice_bits=7,
            velocity_bits=2,
            ancilla_qubits=5,
            logical_qubits=20,
            circuit_depth=100,
            t_count=50,
            toffoli_count=10,
            ccz_count=0,
            rotation_count=5,
            measurement_count=4,
            timesteps=10,
            observable_repetitions=100,
            condition_number=1.0,
            block_encoding_normalization=1.0,
            postselection_success_probability=0.5,
            nonlinear_treatment="linear",
            carleman_truncation_order=None,
            precision_bits=16,
            error_budget=1e-6,
            observable_tolerance=1e-3,
            classical_baseline_cost=0.01,
            operator_spec_id="d1q3_classical_operator_emulation:d1q3_diffusion",
            logical_count_provenance="hand-estimate test fixture",
            assumptions=incomplete,
        )


def test_resource_estimate_rejects_missing_bottleneck_values() -> None:
    assumptions = {
        "state_preparation": "basis-state load only",
        "timestep": "one logical block per LBM step",
        "precision": "16 fixed-point bits",
        "readout": "density and velocity observables",
        "nonlinear_treatment": "linear D1Q3 benchmark",
        "error_budget": "single aggregate logical error budget",
        "classical_comparison": "compare against NumPy baseline runtime",
    }

    with pytest.raises(ValueError):
        LogicalResourceEstimate(
            algorithm_id="d1q3_classical_operator_emulation",
            benchmark_id="d1q3_diffusion",
            lattice_bits=7,
            velocity_bits=2,
            ancilla_qubits=5,
            logical_qubits=20,
            circuit_depth=100,
            t_count=50,
            toffoli_count=10,
            ccz_count=0,
            rotation_count=5,
            measurement_count=4,
            timesteps=10,
            observable_repetitions=100,
            condition_number=0.0,
            block_encoding_normalization=1.0,
            postselection_success_probability=0.5,
            nonlinear_treatment="linear",
            carleman_truncation_order=None,
            precision_bits=16,
            error_budget=1e-6,
            observable_tolerance=1e-3,
            classical_baseline_cost=0.01,
            operator_spec_id="d1q3_classical_operator_emulation:d1q3_diffusion",
            logical_count_provenance="hand-estimate test fixture",
            assumptions=assumptions,
        )

    with pytest.raises(ValueError):
        LogicalResourceEstimate(
            algorithm_id="d1q3_classical_operator_emulation",
            benchmark_id="d1q3_diffusion",
            lattice_bits=7,
            velocity_bits=2,
            ancilla_qubits=5,
            logical_qubits=20,
            circuit_depth=100,
            t_count=50,
            toffoli_count=10,
            ccz_count=0,
            rotation_count=5,
            measurement_count=4,
            timesteps=10,
            observable_repetitions=100,
            condition_number=1.0,
            block_encoding_normalization=1.0,
            postselection_success_probability=1.2,
            nonlinear_treatment="linear",
            carleman_truncation_order=None,
            precision_bits=16,
            error_budget=1e-6,
            observable_tolerance=1e-3,
            classical_baseline_cost=0.01,
            operator_spec_id="d1q3_classical_operator_emulation:d1q3_diffusion",
            logical_count_provenance="hand-estimate test fixture",
            assumptions=assumptions,
        )


def test_physical_resource_estimate_and_operator_spec_validation() -> None:
    physical = PhysicalResourceEstimate(
        algorithm_id="d1q3_classical_operator_emulation",
        benchmark_id="d1q3_diffusion",
        physical_qubits=1000,
        logical_qubits=20,
        runtime_seconds=12.0,
        code_distance=15,
        t_factories=2,
        t_states=100,
        failure_budget=1e-3,
        physical_estimator="azure-quantum-resource-estimator",
        logical_estimate_provenance="test logical estimate",
    )
    assert physical.as_dict()["physical_qubits"] == 1000

    specs = default_quantum_operator_specs()
    d1_spec = specs[0]
    assert not d1_spec.circuit_ready
    assert d1_spec.reversible_embedding_status == "incomplete"
    assert d1_spec.block_encoding_status == "not_started"
    assert d1_spec.normalization is None
    assert d1_spec.success_probability is None
    assert d1_spec.known_gaps

    with pytest.raises(ValueError):
        QuantumOperatorSpec(
            algorithm_id="bad",
            benchmark_id="d1q3_diffusion",
            encoding="basis",
            reversible_embedding_status="complete",
            block_encoding_status="bad-status",
            fixed_point_status="complete",
            readout_status="complete",
            error_budget_status="complete",
            normalization=1.0,
            success_probability=1.0,
            fixed_point_model="16 bits",
            readout_model="samples",
            operator_provenance="test",
            known_gaps=(),
        )


def test_complete_quantum_operator_spec_requires_known_quantities() -> None:
    complete = QuantumOperatorSpec(
        algorithm_id="complete",
        benchmark_id="d1q3_diffusion",
        encoding="basis populations",
        reversible_embedding_status="complete",
        block_encoding_status="complete",
        fixed_point_status="complete",
        readout_status="complete",
        error_budget_status="complete",
        normalization=2.0,
        success_probability=0.25,
        fixed_point_model="16-bit signed fixed point",
        readout_model="amplitude-estimated density observable",
        operator_provenance="explicit block encoding derivation",
        known_gaps=(),
    )

    assert complete.circuit_ready

    with pytest.raises(ValueError):
        QuantumOperatorSpec(
            algorithm_id="bad-complete",
            benchmark_id="d1q3_diffusion",
            encoding="basis populations",
            reversible_embedding_status="complete",
            block_encoding_status="complete",
            fixed_point_status="complete",
            readout_status="complete",
            error_budget_status="complete",
            normalization=None,
            success_probability=0.25,
            fixed_point_model="16-bit signed fixed point",
            readout_model="amplitude-estimated density observable",
            operator_provenance="explicit block encoding derivation",
            known_gaps=(),
        )


def test_resource_estimates_are_gated_by_evidence_stage() -> None:
    assumptions = {
        "state_preparation": "basis-state load only",
        "timestep": "one logical block per LBM step",
        "precision": "16 fixed-point bits",
        "readout": "density and velocity observables",
        "nonlinear_treatment": "linear D1Q3 benchmark",
        "error_budget": "single aggregate logical error budget",
        "classical_comparison": "compare against NumPy baseline runtime",
    }
    logical = LogicalResourceEstimate(
        algorithm_id="d2q9_barred_srt",
        benchmark_id="d2q9_taylor_green",
        lattice_bits=7,
        velocity_bits=4,
        ancilla_qubits=5,
        logical_qubits=20,
        circuit_depth=100,
        t_count=50,
        toffoli_count=10,
        ccz_count=0,
        rotation_count=5,
        measurement_count=4,
        timesteps=10,
        observable_repetitions=100,
        condition_number=1.0,
        block_encoding_normalization=1.0,
        postselection_success_probability=0.5,
        nonlinear_treatment="linearized",
        carleman_truncation_order=None,
        precision_bits=16,
        error_budget=1e-6,
        observable_tolerance=1e-3,
        classical_baseline_cost=0.01,
        operator_spec_id="d2q9_barred_srt:d2q9_taylor_green",
        logical_count_provenance="test estimate",
        assumptions=assumptions,
    )
    physical = PhysicalResourceEstimate(
        algorithm_id="d2q9_barred_srt",
        benchmark_id="d2q9_taylor_green",
        physical_qubits=1000,
        logical_qubits=20,
        runtime_seconds=12.0,
        code_distance=15,
        t_factories=2,
        t_states=100,
        failure_budget=1e-3,
        physical_estimator="azure-quantum-resource-estimator",
        logical_estimate_provenance="test logical estimate",
    )
    base_card = next(
        card
        for card in default_algorithm_registry()
        if card.algorithm_id == "d2q9_barred_srt"
    )
    logical_card = replace(base_card, evidence_stage="logical_resource_counts")
    physical_card = replace(base_card, evidence_stage="physical_ft_estimate")
    config = SimulationConfig(
        grid_shape=(8, 8),
        steps=2,
        tau=0.8,
        initial_condition="taylor_green",
        sample_interval=None,
        amplitude=0.02,
    )
    result = run_d2q9_barred_srt(config)

    with pytest.raises(ValueError):
        StudyResultRecord.from_simulation(
            card=base_card,
            benchmark_id="d2q9_taylor_green",
            result=result,
            accuracy_metric="relative_l2_error_velocity",
            stable=True,
            resource_estimate=logical,
        )

    with pytest.raises(ValueError):
        StudyResultRecord.from_simulation(
            card=logical_card,
            benchmark_id="d2q9_taylor_green",
            result=result,
            accuracy_metric="relative_l2_error_velocity",
            stable=True,
            physical_estimate=physical,
        )

    with pytest.raises(ValueError):
        StudyResultRecord.from_simulation(
            card=logical_card,
            benchmark_id="d2q9_taylor_green",
            result=result,
            accuracy_metric="relative_l2_error_velocity",
            stable=True,
            resource_estimate=logical,
            physical_estimate=physical,
        )

    record = StudyResultRecord.from_simulation(
        card=physical_card,
        benchmark_id="d2q9_taylor_green",
        result=result,
        accuracy_metric="relative_l2_error_velocity",
        stable=True,
        resource_estimate=logical,
        physical_estimate=physical,
    )
    assert record.resource_estimate is logical
    assert record.physical_estimate is physical


def test_study_record_csv_has_stable_columns(tmp_path) -> None:
    card = next(
        card
        for card in default_algorithm_registry()
        if card.algorithm_id == "d2q9_barred_srt"
    )
    config = SimulationConfig(
        grid_shape=(8, 8),
        steps=2,
        tau=0.8,
        initial_condition="taylor_green",
        sample_interval=None,
        amplitude=0.02,
    )
    result = run_d2q9_barred_srt(config)
    record = StudyResultRecord.from_simulation(
        card=card,
        benchmark_id="d2q9_taylor_green",
        result=result,
        accuracy_metric="relative_l2_error_velocity",
        stable=True,
    )

    output = write_study_records_csv([record], tmp_path / "study.csv")

    with output.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert tuple(rows[0].keys()) == STUDY_RESULT_CSV_COLUMNS
    assert rows[0]["algorithm_id"] == "d2q9_barred_srt"
    assert rows[0]["grid_shape"] == "8x8"


def test_algorithm_registry_json_round_trip(tmp_path) -> None:
    output = write_algorithm_registry_json(
        default_algorithm_registry(),
        tmp_path / "registry.json",
    )

    payload = json.loads(output.read_text(encoding="utf-8"))

    assert isinstance(payload, list)
    assert payload[0]["algorithm_id"] == "d2q9_bgk_srt"
