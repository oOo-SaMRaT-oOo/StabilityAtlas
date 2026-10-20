import sys
import os

# Enable root directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.ai.build_atlas_manifold import generate_stability_atlas
from backend.ai.ml_engine import StabilityAtlasEngine
from essential_functions_used import clear_screen

# Remove UMAP warning for randomstate = 42
import warnings
warnings.filterwarnings("ignore", message=".*n_jobs value 1 overridden.*")

def main():
    clear_screen()

    print("-" * 60)
    print("      STABILITY ATLAS: END-TO-END TRAINING PIPELINE     ")
    print("-" * 60)

    # 1. UMAP Manifold & HDBSCAN Clustering
    print("\n[1/3] Running UMAP Manifold & HDBSCAN Clustering ...\n")
    df, labels, embedding = generate_stability_atlas()
    print(f"      ► Dataset shape loaded : {df.shape}")
    print(f"      ► Total samples        : {len(labels)}")

    # 2. Train Supervised Engine & Manupulate Artifacts
    print("\n\n[2/3] Training StabilityAtlasEngine Classifier ...")
    engine = StabilityAtlasEngine(model_dir="ai/assets")
    engine.train_and_export(df=df,labels = labels)

    # 3. Live Sanity Check / Mock Real-Time Inference
    print("\n\n[3/3] Running Production Inference Health Check ...")
    engine.load_artifacts()

    # Pull row 0 as a mock incoming SCADA telemetry packet
    sample_payload = df.iloc[0].to_dict()
    result = engine.predict_grid_state(sample_payload)

    print("\n\n\n" + "-" * 60)
    print("                HEALTH CHECK RESULTS                   ")
    print("-" * 60)
    print(f"\n  Predicted Cluster ID : {result['predicted_cluster']}")
    print(f"  Confidence Level     : {result['confidence_percentage']}%")
    print(f"  Severity Tier        : {result['severity']}")
    print(f"  Expected Nadir       : {result['avg_nadir_hz']} Hz")
    print(f"  Max Expected RoCoF   : {result['max_rocof_hz_s']} Hz/s")
    print(f"  Instability Risk     : {result['instability_rate']}%")
    print("\n  Top Physical Risk Drivers :")
    for driver in result["top_risk_drivers"]:
        print(f"    - {driver['feature']}: {driver['impact_score']}")
    print("\n\n[✔] PIPELINE EXECUTION SUCCESSFUL : ARTIFACTS READY FOR DEPLOYMENT.\n\n\n")


if __name__ == "__main__":
    main()

