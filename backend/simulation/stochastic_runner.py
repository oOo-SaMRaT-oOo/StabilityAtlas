import sys
import os
# Force Python to add the root project folder (StabilityAtlas) to its search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

from backend.physics.engine import Stability_Atlas_Engine
from backend.simulation.classifying_data import SimulationResult
from backend.simulation.metrices import extract_grid_metrices
from backend.simulation.scenario_factory import generate_grid_scenario
from essential_functions_used import compute_pffr_history
from backend.simulation_inspector import save_simulation_trajectory

def clear_screen():
    import subprocess
    command = "clear"
    subprocess.run(command, shell=True)
    print("\033[3J\033[H\033[2J", end="", flush=True)


def run_single_simulation(sim_id,t_span = (0.0,30.0),t_steps = 3000):

    params,y0,dist1,dist2 = generate_grid_scenario(seed=sim_id)
    t_eval = np.linspace(t_span[0],t_span[1],t_steps)

    def frequency_collaspe_event(t,y):
        f1 = 50.0 + (y[0] / (2 * np.pi))
        f2 = 50.0 + (y[5] / (2 * np.pi))
        worst_freq = min(f1,f2)
        return worst_freq - 30.0

    frequency_collaspe_event.terminal = True
    frequency_collaspe_event.direction = -1

    sol = solve_ivp(
        fun=lambda t,y:Stability_Atlas_Engine(t,y,params,dist1,dist2),
        t_span=t_span,
        y0 = y0,
        t_eval=t_eval,
        method="RK45",
        events=[frequency_collaspe_event],
        max_step = 0.02
    )

    # # ------------------ DEBUG PURPOSE ONLY ----------------------- #

    # # 3. Calculate Trajectory Minimum Frequency (50 Hz Nominal)
    # f1 = 50.0 + (sol.y[0] / (2 * np.pi))
    # f2 = 50.0 + (sol.y[5] / (2 * np.pi))
    # min_freq = float(min(np.min(f1), np.min(f2)))

    # # 4. Print the 4 Key Diagnostics
    # print("\n=" * 40)
    # print("      SOLVER DIAGNOSTIC RESULTS      ")
    # print("=" * 40)
    # print(f"Solver Status Code (sol.status) : {sol.status}")
    # print(f"Solver Termination Message     : {sol.message}")
    # print(f"Final Integrated Time (sol.t[-1]): {sol.t[-1]:.4f} s")
    # print(f"Min Frequency Reached in Array  : {min_freq:.2f} Hz")
    # print(f"Events Triggered (sol.t_events) : {sol.t_events}")
    # print("=" * 40 + "\n")


    # # ------------------ DEBUG PURPOSE ONLY ----------------------- #

    if not sol.success:
        return None
    
    P_ffr1_hist, P_ffr2_hist = compute_pffr_history(sol, params, dist1, dist2)
    
    states = sol.y.T

    metrics = extract_grid_metrices(sol.t, states, params, sol.status)

    save_simulation_trajectory(sim_id, sol, params, P_ffr1_hist, P_ffr2_hist)


    return SimulationResult(
        sim_id= sim_id,
        time=sol.t,
        states=states,
        parameters=params,
        metrics=metrics
    )

    

if __name__=="__main__" :

    clear_screen()
    print("\n\n--- LAUNCHING SIMULATION PROTOTYPE ---\n")

    dataset_rows = []

    for i in range(1,10+1):
        res = run_single_simulation(sim_id=i)
        if res:
            row = {"sim_id":res.sim_id, **res.metrics}
            dataset_rows.append(row)

            print(
                    f"  [Run {res.sim_id:02d}] Success | "
                    f"Worst Nadir: {res.metrics['worst_nadir_hz']:.3f} Hz | "
                    f"Max RoCoF: {res.metrics['max_rocof_a1']:.3f} Hz/s | "
                    f"Tie Util: {res.metrics['tie_utilization_pct']:.1f}%"
                )
            
        else :
            print(f"  [ RUN {i:02d} ] FAILURE | SIMULATION CRASH")

    df_features = pd.DataFrame(dataset_rows)

    print("\n--- SIMULATION COMPLETE ---\n")

    print(df_features[["sim_id", "worst_nadir_hz", 
                    "max_rocof_a1", "delta_soc1", 
                    "tie_utilization_pct", 
                    "is_unstable"]])

    print("\n\n")




