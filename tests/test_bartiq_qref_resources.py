from pq_cfd import _bartiq_qref_resources as resources


def test_bartiq_qref_route_tree_compiles_and_has_expected_formula() -> None:
    routine = resources.evaluate_qre2_taylor_green_route()

    assert routine.name == "qre2_periodic_taylor_green_learning_skeleton"
    assert list(routine.children) == ["load_state", "time_loop", "observable_readout"]
    assert str(routine.resources["t_count"].value) == (
        "N_samples*T_readout_sample + "
        "N_t*(T_collide + T_stream + T_success) + T_load"
    )
    assert str(routine.resources["state_loads"].value) == "1"
    assert str(routine.resources["samples"].value) == "N_samples"
    assert resources.PLACEHOLDER_NOTICE in resources.qre2_taylor_green_route_tree()[
        "program"
    ]["meta"]["notice"]


def test_bartiq_qref_route_tree_numeric_placeholder_evaluation() -> None:
    routine = resources.evaluate_qre2_taylor_green_route(
        {
            "N_x": 32,
            "N_y": 32,
            "N_t": 10,
            "N_samples": 1000,
            "q_site": 10,
            "q_velocity": 4,
            "q_population": 8,
            "q_work": 20,
            "q_observable": 5,
            "T_load": 10_000,
            "T_stream": 200,
            "T_collide": 1_000,
            "T_success": 50,
            "T_readout_sample": 25,
            "p_load": 0.99,
            "p_step": 0.999,
            "p_readout": 0.99,
        }
    )

    assert routine.resources["lattice_populations"].value == 9216
    assert routine.resources["logical_qubits"].value == 47
    assert routine.resources["state_loads"].value == 1
    assert routine.resources["t_count"].value == 47500
    assert routine.resources["samples"].value == 1000


def test_bartiq_qref_route_helpers_stay_private() -> None:
    import pq_cfd

    assert "_bartiq_qref_resources" not in pq_cfd.__all__
    assert not hasattr(pq_cfd, "compile_qre2_taylor_green_route")
