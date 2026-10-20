import sys
import os

# Add root project folder (StabilityAtlas) to Python search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def clear_screen():
    import subprocess
    command = "clear"
    subprocess.run(command, shell=True)
    print("\033[3J\033[H\033[2J", end="", flush=True)

import time
import concurrent.futures
import pandas as pd
from tqdm import tqdm

from backend.simulation.stochastic_runner import run_single_simulation
from essential_functions_used import save_dataset


def generate_batch(num_simulations: int = 10):

    num_workers = os.cpu_count() or 4

    tqdm.write("\n--- LAUNCHING SIMULATIONS ---\n")
    tqdm.write(f"TARGET NUMBER OF SIMULATIONS   : {num_simulations}")
    tqdm.write(f"CURRENT CPU CORES WORKING      : {num_workers}\n\n\n")

    start_time = time.time()
    dataset_rows = []

    sim_ids = list(range(1, num_simulations + 1))

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:

        tqdm.write("  ► SIMULATING GRID SCENARIO:\n")
        results = tqdm(
            iterable=executor.map(run_single_simulation, sim_ids),
            total=num_simulations,
            desc="",
            unit=" Simulations",
            ncols=100
        )

        for res in results:
            if res is not None:
                row = {
                    "sim_id": res.sim_id,
                    **res.parameters,
                    **res.metrics
                }
                dataset_rows.append(row)

    elapsed_time = time.time() - start_time

    df = pd.DataFrame(dataset_rows)

    print(f"\n   BATCH COMPLETED IN {elapsed_time:.2f} SECONDS")
    print(f"   SUCCESSFUL SIMULATIONS : {len(df)} / {num_simulations}")
    print(f"   FEATURE MATRIX SHAPE   : {df.shape}\n")

    return df


# MANDATORY FOR PYTHON MULTIPROCESSING ON macOS/PYTHON 3.13

if __name__ == "__main__":
    # clear_screen()
    number_of_simulations = 300
    df_batch = generate_batch(num_simulations=number_of_simulations)

    # Automatically save dataset to data/raw in CSV & Parquet
    save_dataset(df_batch)

    # Health check for scenario environment distributions
    if not df_batch.empty and "scenario_type" in df_batch.columns:
        print("\n--- SIMULATION ENVIRONMENT BREAKDOWN ---\n\n")
        print(df_batch["scenario_type"].value_counts().to_string())
        print("\n")