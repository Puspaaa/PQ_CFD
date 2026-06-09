"""Private Bartiq/QREF learning resource skeletons.

Corpus IDs: QRE2, QRE4, IO4, IO5, IO7, IO8, PRIM14, PRIM15.

The formulas in this module are placeholder learning objects. They provide
resource-bookkeeping boxes for discussion and testing, not validated QRE2
resource estimates and not circuit implementations.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from bartiq import compile_routine, evaluate
from qref import SchemaV1

PLACEHOLDER_NOTICE = (
    "Learning placeholder only: formulas are not QRE2 claims, circuit costs, "
    "or dependency on a chosen encoding/loading/readout route."
)

_QRE2_TAYLOR_GREEN_ROUTE: dict[str, Any] = {
    "version": "v1",
    "program": {
        "name": "qre2_periodic_taylor_green_learning_skeleton",
        "type": "learning_placeholder",
        "input_params": [
            "N_x",
            "N_y",
            "N_t",
            "N_samples",
            "q_site",
            "q_velocity",
            "q_population",
            "q_work",
            "q_observable",
            "T_load",
            "T_stream",
            "T_collide",
            "T_success",
            "T_readout_sample",
            "p_load",
            "p_step",
            "p_readout",
        ],
        "resources": [
            {
                "name": "logical_qubits",
                "type": "qubits",
                "value": "q_site + q_velocity + q_population + q_work + q_observable",
            },
            {"name": "lattice_populations", "type": "other", "value": "9*N_x*N_y"},
            {
                "name": "success_probability_placeholder",
                "type": "other",
                "value": "p_load*p_step**N_t*p_readout",
            },
        ],
        "meta": {"notice": PLACEHOLDER_NOTICE},
        "children": [
            {
                "name": "load_state",
                "type": "learning_placeholder",
                "resources": [
                    {"name": "t_count", "type": "additive", "value": "T_load"},
                    {"name": "state_loads", "type": "additive", "value": 1},
                ],
            },
            {
                "name": "time_loop",
                "type": "learning_placeholder",
                "repetition": {
                    "count": "N_t",
                    "sequence": {"type": "constant", "multiplier": 1},
                },
                "children": [
                    {
                        "name": "one_periodic_taylor_green_timestep",
                        "type": "learning_placeholder",
                        "children": [
                            {
                                "name": "stream_periodic_shift",
                                "type": "learning_placeholder",
                                "resources": [
                                    {
                                        "name": "t_count",
                                        "type": "additive",
                                        "value": "T_stream",
                                    }
                                ],
                            },
                            {
                                "name": "collide_update",
                                "type": "learning_placeholder",
                                "resources": [
                                    {
                                        "name": "t_count",
                                        "type": "additive",
                                        "value": "T_collide",
                                    }
                                ],
                            },
                            {
                                "name": "success_or_normalization_control",
                                "type": "learning_placeholder",
                                "resources": [
                                    {
                                        "name": "t_count",
                                        "type": "additive",
                                        "value": "T_success",
                                    }
                                ],
                            },
                        ],
                    }
                ],
            },
            {
                "name": "observable_readout",
                "type": "learning_placeholder",
                "resources": [
                    {"name": "samples", "type": "additive", "value": "N_samples"},
                    {
                        "name": "t_count",
                        "type": "additive",
                        "value": "N_samples*T_readout_sample",
                    },
                ],
            },
        ],
    },
}


def qre2_taylor_green_route_tree() -> dict[str, Any]:
    """Return the QREF route tree as plain data for inspection or serialization."""

    return deepcopy(_QRE2_TAYLOR_GREEN_ROUTE)


def qre2_taylor_green_qref() -> SchemaV1:
    """Return the placeholder route tree validated as QREF schema v1."""

    return SchemaV1.model_validate(qre2_taylor_green_route_tree())


def compile_qre2_taylor_green_route():
    """Compile the placeholder route tree with Bartiq."""

    return compile_routine(qre2_taylor_green_qref()).routine


def evaluate_qre2_taylor_green_route(assignments: Mapping[str, Any] | None = None):
    """Evaluate the placeholder route tree with optional symbolic assignments."""

    return evaluate(compile_qre2_taylor_green_route(), assignments or {}).routine
