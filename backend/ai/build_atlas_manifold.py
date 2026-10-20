import sys
import os
import glob

# Add root project folder (StabilityAtlas) to Python search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

import umap
import hdbscan  

from essential_functions_used import cluster_profile
from essential_functions_used import light_weight_cluster
from essential_functions_used import unsupervised_plot,clear_screen

def generate_stability_atlas(file_path = None):

    # Automatically select the newest Parquet file in data/raw
    if file_path is None:
        
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "raw"))
        files = glob.glob(os.path.join(data_dir, "*.parquet"))
        if not files:
            raise FileNotFoundError(f"No parquet files found in {data_dir}")
        file_path = max(files, key=os.path.getctime)

    # 1. Load Raw Feature Matrix
    df = pd.read_parquet(file_path)

    # Clustering Based on Prefault Conditions
    ignore_cols = [              
                # identifiers / labels, not physical features
                "sim_id","scenario_type","cluster",

                # everything returned by extract_grid_metrices() — all outcomes
                "nadir_a1_hz","nadir_a2_hz","worst_nadir_hz","max_rocof_a1",
                "max_rocof_a2","delta_soc1","delta_soc2","max_tie_flow_pu",
                "tie_utilization_pct","is_unstable",
                ]
    
    features = df.drop(columns=ignore_cols, errors="ignore")

    # Encode string features
    features = pd.get_dummies(features)

    # 2. Standardize Features (Zero Mean, Unit Variance)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    # 3. UMAP Manifold Projection (Compress 64D -> 2D)  
    reducer = umap.UMAP(n_neighbors = 15, min_dist = 0.1, random_state = 42)
    embedding = reducer.fit_transform(X_scaled)

    # 4. Unsupervised HDBSCAN Clustering
    clusters = hdbscan.HDBSCAN(min_cluster_size = 5, gen_min_span_tree = True)
    labels = clusters.fit_predict(embedding)

    # unsupervised_plot(embedding,labels,df) 
    # cluster_profile(df,labels)

    return df,labels,embedding



if __name__ == "__main__":
    generate_stability_atlas()


