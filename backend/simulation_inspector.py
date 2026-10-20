import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Directory where individual simulation trajectory files are stored
TRAJ_DIR = os.path.join(os.path.dirname(__file__), "data", "trajectories")


def save_simulation_trajectory(sim_id: int, sol, params, p_ffr1_hist: list, p_ffr2_hist: list):

    os.makedirs(TRAJ_DIR, exist_ok=True)

    f1 = 50.0 + (sol.y[0] / (2 * np.pi))
    f2 = 50.0 + (sol.y[5] / (2 * np.pi))

    df_traj = pd.DataFrame({
        "time": sol.t,
        "f1": f1,
        "f2": f2,
        "dw1": sol.y[0],
        "P_m1_A": sol.y[1],
        "P_m1_B": sol.y[2],
        "P_agc1": sol.y[3],
        "SoC1": sol.y[4],
        "dw2": sol.y[5],
        "P_m2_A": sol.y[6],
        "P_m2_B": sol.y[7],
        "P_agc2": sol.y[8],
        "SoC2": sol.y[9],
        "dP_tie": sol.y[10],
        "P_ffr1": p_ffr1_hist,
        "P_ffr2": p_ffr2_hist
    })

    file_path = os.path.join(TRAJ_DIR, f"sim_{sim_id:06d}.parquet")
    df_traj.to_parquet(file_path, index=False)


def inspect_simulation(sim_id: int, params: dict = None):
    
    file_path = os.path.join(TRAJ_DIR, f"sim_{sim_id:06d}.parquet")
    
    if not os.path.exists(file_path):
        print(f"ERROR : NO DATA FOUND\nSIMULATION ID : {sim_id}\nFILE PATH : {file_path}")
        return

    df = pd.read_parquet(file_path)

    # Use default limits if params dict is not passed
    p_max1_a = params.get("P_max1_A", 0.65) if params else 0.65
    p_max1_b = params.get("P_max1_B", 0.40) if params else 0.40
    p_max2_a = params.get("P_max2_A", 0.80) if params else 0.80
    p_max2_b = params.get("P_max2_B", 0.60) if params else 0.60
    p_tie_max = params.get("P_tie_max", 0.10) if params else 0.10

    # 4-Subplot Research Dashboard
    fig, axs = plt.subplots(4, 1, figsize=(11, 12), sharex=True)

    # Plot 1: Frequencies (Hz) & Limits
    axs[0].plot(df["time"], df["f1"], label="Area 1 Frequency (Hz)", color="crimson", linewidth=2)
    axs[0].plot(df["time"], df["f2"], label="Area 2 Frequency (Hz)", color="navy", linewidth=2, linestyle="--")
    axs[0].axhline(50.0, color="black", linestyle="-", alpha=0.6, label="Nominal (50.0 Hz)")
    axs[0].axhline(49.00, color="red", linestyle="-.", linewidth=1.5, label="Lower Limit (49.0 Hz)")
    axs[0].axhline(51.00, color="red", linestyle="-.", linewidth=1.5, label="Upper Limit (51.0 Hz)")
    axs[0].set_ylabel("Frequency [Hz]")
    axs[0].set_title(f"Grid Frequency Response & Boundaries (Sim ID: #{sim_id})")
    axs[0].legend(loc="upper right")
    axs[0].grid(True)

    # Plot 2: Generator Mechanical Power Output & Limits
    axs[1].plot(df["time"], df["P_m1_A"], label="P_m1_A (Area 1)", color="darkred")
    axs[1].plot(df["time"], df["P_m1_B"], label="P_m1_B (Area 1)", color="red")
    axs[1].axhline(p_max1_a, color="darkred", linestyle=":", label="P_max1_A Limit")
    axs[1].axhline(p_max1_b, color="red", linestyle=":", label="P_max1_B Limit")
    axs[1].plot(df["time"], df["P_m2_A"], label="P_m2_A (Area 2)", color="darkblue", linestyle="--")
    axs[1].plot(df["time"], df["P_m2_B"], label="P_m2_B (Area 2)", color="blue", linestyle="--")
    axs[1].set_ylabel("Power [p.u.]")
    axs[1].set_title("Generator Output & Capacity Limits")
    axs[1].legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    axs[1].grid(True)

    # Plot 3: Tie-Line Interconnection Flow
    axs[2].plot(df["time"], df["dP_tie"], label="Tie-Line Flow (dP_tie)", color="purple", linewidth=2)
    axs[2].axhline(p_tie_max, color="purple", linestyle=":", label="+P_tie_max Limit")
    axs[2].axhline(-p_tie_max, color="purple", linestyle=":", label="-P_tie_max Limit")
    axs[2].set_ylabel("Power [p.u.]")
    axs[2].set_title("Inter-Area Tie-Line Power Flow & Thermal Limits")
    axs[2].legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    axs[2].grid(True)

    # Plot 4: Battery FFR Power & State of Charge (SoC) for BOTH Areas
    ax4_soc = axs[3].twinx()
    
    # FFR Active Power Outputs
    line1 = axs[3].plot(df["time"], df["P_ffr1"], label="P_ffr1 (Area 1 Power)", color="forestgreen", linewidth=2)
    line2 = axs[3].plot(df["time"], df["P_ffr2"], label="P_ffr2 (Area 2 Power)", color="teal", linewidth=2, linestyle="--")
    
    # State-of-Charge Curves (Darker, thicker lines for high visibility)
    line3 = ax4_soc.plot(df["time"], df["SoC1"], label="SoC Area 1", color="darkgreen", linestyle=":", linewidth=2.2)
    line4 = ax4_soc.plot(df["time"], df["SoC2"], label="SoC Area 2", color="darkcyan", linestyle=":", linewidth=2.2)
    
    # Combine legends cleanly
    lines = line1 + line2 + line3 + line4
    labels = [l.get_label() for l in lines]
    axs[3].legend(lines, labels, loc="upper left", bbox_to_anchor=(1.08, 1))

    axs[3].set_ylabel("FFR Power [p.u.]", color="forestgreen")
    ax4_soc.set_ylabel("SoC [0.0 - 1.0]", color="darkcyan")
    axs[3].set_xlabel("Time [seconds]")
    axs[3].set_title("Fast Frequency Response (FFR) & Battery State of Charge (Both Areas)")
    axs[3].grid(True)

    plt.tight_layout()
    plt.show()