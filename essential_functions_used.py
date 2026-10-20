from pathlib import Path
from datetime import datetime
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split,cross_val_score
import numpy as np
import matplotlib.pyplot as plt
import subprocess

def clear_screen():
    command = "clear"
    subprocess.run(command, shell=True)
    print("\033[3J\033[H\033[2J", end="", flush=True)

def save_dataset(df: pd.DataFrame, output_dir : str = "data/raw"):
    print("\n\n")
    if df.empty:
        print("WARNING : DATA FRAME IS EMPTY : SKIPING SAVE ")

    # Creat directory path relative to project root
    project_root = Path(__file__).resolve().parent
    target_dir = project_root / output_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"sim_batch_{len(df)}runs_{timestamp}"

    csv_path = target_dir/f"{base_filename}.csv"
    parquet_path = target_dir / f"{base_filename}.parquet"

    df.to_csv(csv_path,index = False)
    df.to_parquet(parquet_path,index = False)

    print(f" SAVED CSV     : {csv_path}")
    print(f" SAVED PARQUET : {parquet_path}\n")

def compute_pffr_history(sol,params,disturbance_func1,disturbance_func2):

    P_ffr1_hist, P_ffr2_hist = [], []
    
    for i in range(len(sol.t)):
        # Area 1
        dw1_pu = sol.y[0][i] / params["omega_0"]
        swing1 = (sol.y[1][i] + sol.y[2][i] - sol.y[10][i]) - disturbance_func1(sol.t[i]) - (params["D1"] * dw1_pu)
        if (sol.y[4][i] > 0.001 and swing1 < 0.0) or (sol.y[4][i] < 0.999 and swing1 > 0.0):
            ddw1_dt = (params["omega_0"] * swing1) / (2 * (params["H1_A"] + params["H1_B"]) + params["K_virtual1"])
            p_ffr1 = -params["K_virtual1"] * (ddw1_dt / params["omega_0"])
        else:
            p_ffr1 = 0.0
        P_ffr1_hist.append(p_ffr1)

        # Area 2
        dw2_pu = sol.y[5][i] / params["omega_0"]
        swing2 = (sol.y[6][i] + sol.y[7][i] + sol.y[10][i]) - disturbance_func2(sol.t[i]) - (params["D2"] * dw2_pu)
        if (sol.y[9][i] > 0.001 and swing2 < 0.0) or (sol.y[9][i] < 0.999 and swing2 > 0.0):
            ddw2_dt = (params["omega_0"] * swing2) / (2 * (params["H2_A"] + params["H2_B"]) + params["K_virtual2"])
            p_ffr2 = -params["K_virtual2"] * (ddw2_dt / params["omega_0"])
        else:
            p_ffr2 = 0.0
        P_ffr2_hist.append(p_ffr2)

    return P_ffr1_hist,P_ffr2_hist


def cluster_profile(df : pd.DataFrame ,labels : list):
    df["cluster"] = labels
    df["H_system"] = df['H1_A'] + df['H1_B'] + df['H2_A'] + df['H2_B']
    grouped = df.groupby("cluster")
    summary = grouped[["worst_nadir_hz","tie_utilization_pct","max_tie_flow_pu","is_unstable"]].mean()
    print(summary)



def light_weight_cluster(df:pd.DataFrame,labels):
    df["cluster"] = labels
    clean_index = df["cluster"]!=-1
    clean_df = df[clean_index]
    df = clean_df

    ignore_cols = [
    "sim_id", "scenario_type", "cluster", "is_unstable",
    "nadir_a1_hz", "nadir_a2_hz", "worst_nadir_hz", 
    "max_rocof_a1", "max_rocof_a2"
    ]

    feature_cols = [col for col in df.columns if col not in ignore_cols]

    x = pd.get_dummies(df[feature_cols])
    y = df["cluster"]

    model = RandomForestClassifier(n_estimators=100,
                                   max_depth=6,
                                   random_state=42,
                                   n_jobs=-1)

    x_train,x_test,y_train,y_test = train_test_split(x,y,random_state=42,stratify=y )
    model.fit(x_train,y_train)
    cv_score = cross_val_score(model,x_train,y_train,scoring = "accuracy",cv = 5)
    cv_score =  np.abs(np.mean(cv_score))
    model_prediction_value = model.predict(x_test)

    clear_screen()
    print("\n\n--- MODEL REPORT ---")
    print("MODEL TYPE :",model)
    print("CV SCORE :",cv_score)

    print("\nCLASSIFICATION REPORT :")
    report = classification_report(y_test,model_prediction_value,zero_division=0)
    print(report)

    importances = pd.Series(model.feature_importances_,index = x.columns)
    top_physics = importances.sort_values(ascending=False).head(10)
    print("\n--- TOP 10 PHYSICAL FEATURE IMPORTANCES ---")
    print(top_physics)


def unsupervised_plot(embedding,labels,df):

    fig,axs = plt.subplots(ncols = 1,nrows = 2)
    axs = axs.flatten()

    noise_df = embedding[labels==-1]
    cluster_df = embedding[labels != -1]
    cluster_labels = labels[labels != -1]

    axs[0].scatter(noise_df[:,0],noise_df[:,1], c='lightgray', s=30, alpha=0.5, label='noise / unclustered')
    axs[0].scatter(cluster_df[:,0], cluster_df[:,1], c=cluster_labels, cmap='tab10', s=50, alpha=0.85)

    axs[0].set_title("StabilityAtlas: Unsupervised Phase-Space Topology Map", fontsize=15)
    axs[0].set_xlabel("UMAP Dimension 1")
    axs[0].set_ylabel("UMAP Dimension 2")
    axs[0].grid(True, linestyle='--', alpha=0.5)


    scatter = axs[1].scatter(
        embedding[:,0],
        embedding[:,1],
        c = df["worst_nadir_hz"],
        cmap = "coolwarm_r",
        s = 45,
        alpha = 0.85
    )

    cbar = plt.colorbar(scatter,ax = axs[1])
    cbar.set_label("Frequency Nadir (Hz)")
    axs[1].set_title("StabilityAtlas: Frequency Nadir Topology Map",fontsize = 15)
    axs[1].set_xlabel("UMAP Dimension 1")
    axs[1].set_ylabel("UMAP Dimension 2")
    axs[1].grid(True, linestyle='--', alpha=0.4)

    plt.tight_layout()
    plt.show()





