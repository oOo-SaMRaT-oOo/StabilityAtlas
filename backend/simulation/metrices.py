import numpy as np

def extract_grid_metrices(time: np.ndarray ,states : np.ndarray ,
                          params : dict, condition_for_worst_nadir ) -> dict:

    omega_0 = params.get("omega_0", 2 * np.pi * 50)

    f1 = 50.0 + (states[:, 0] / (2 * np.pi))
    f2 = 50.0 + (states[:, 5] / (2 * np.pi))

    raw_nadir_a1 = np.min(f1)
    raw_nadir_a2 = np.min(f2)

    rocof_a1 = float(np.max(np.abs(np.gradient(f1, time))))
    rocof_a2 = float(np.max(np.abs(np.gradient(f2, time))))

    soc1_start, soc1_end = states[0, 4], states[-1, 4]
    soc2_start, soc2_end = states[0, 9], states[-1, 9]

    delta_soc1 = soc1_start - soc1_end
    delta_soc2 = soc2_start - soc2_end

    max_tie_flow = np.max(np.abs(states[:, 10]))
    tie_utilization_pct = (max_tie_flow / params["P_tie_max"]) * 100.0

    if (condition_for_worst_nadir) or (min(raw_nadir_a1,raw_nadir_a2) < 30.0):
        worst_nadir_hz = 30.0
        nadir_a1 = 30 if raw_nadir_a1 < 30 else raw_nadir_a1
        nadir_a2 = 30 if raw_nadir_a2 < 30 else raw_nadir_a2

    else:
        worst_nadir_hz = float(min(raw_nadir_a1,raw_nadir_a2))
        nadir_a1 = raw_nadir_a1
        nadir_a2 = raw_nadir_a2

    return {
        "nadir_a1_hz": nadir_a1,
        "nadir_a2_hz": nadir_a2,
        "worst_nadir_hz": worst_nadir_hz,
        "max_rocof_a1": rocof_a1,
        "max_rocof_a2": rocof_a2,
        "delta_soc1": delta_soc1,
        "delta_soc2": delta_soc2,
        "max_tie_flow_pu": max_tie_flow,
        "tie_utilization_pct": min(100.0, tie_utilization_pct),
        "is_unstable": 1 if worst_nadir_hz < 47.5 else 0  # TRIP LIMIT
    }