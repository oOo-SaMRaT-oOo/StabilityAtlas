import os
import joblib
import numpy as np
import pandas as pd
import shap

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score,train_test_split

class StabilityAtlasEngine:
    def __init__(self,model_dir = "model_artifacts"):
        self.model_dir = model_dir
        self.model = None
        self.feature_columns = None
        self.feature_defaults = None
        self.risk_profiles = None
        self.explainer = None
        self.ignore_cols = [
                            # identifiers / labels, not physical features
                            "sim_id","scenario_type","cluster",

                            # everything returned by extract_grid_metrices() — all outcomes
                            "nadir_a1_hz","nadir_a2_hz","worst_nadir_hz","max_rocof_a1",
                            "max_rocof_a2","delta_soc1","delta_soc2","max_tie_flow_pu",
                            "tie_utilization_pct","is_unstable",
                            ]
        
    def train_and_export(self, df : pd.DataFrame, labels:np.ndarray):
        df_clean = df.copy()
        df_clean["cluster"] = labels
        df_clean = df_clean[df_clean["cluster"]!=-1].copy()
        self.risk_profiles =  self.build_risk_profile(df_clean) # Risk Information
        raw_features = [c for c in df_clean.columns if c not in self.ignore_cols]

        x = pd.get_dummies(df_clean[raw_features])
        y = df_clean["cluster"]

        self.feature_columns = list(x.columns)
        self.feature_defaults = x.median().to_dict()


        x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,
                                                         random_state=42,
                                                         stratify=y
                                                         )

        self.model = RandomForestClassifier(
            n_estimators= 100,
            max_depth=6,
            random_state=42,
            n_jobs=-1
        )

        cv_scores = cross_val_score(
            self.model,x_train,y_train,scoring="accuracy",cv = 3
        )
        
        self.model.fit(x_train, y_train)

        self.explainer = shap.TreeExplainer(self.model)

        test_accuracy = self.model.score(x_test,y_test)

        print("\n--- STABILITY ATLAS ENGINE: TRAINING COMPLETE ---\n")
        print(f"CV SCORE : {np.mean(cv_scores) * 100:.2f}%")
        print(f"TEST ACCURACY : {test_accuracy * 100:.2f}%")

        self.save_artifacts()

    def build_risk_profile(self,df):
        df_used = df.copy()
        df_used["max_rocof"] = np.maximum(
            df["max_rocof_a1"].abs(),
            df["max_rocof_a2"].abs())
        
        summary = df_used.groupby("cluster").agg(
            avg_nadir = ("worst_nadir_hz","mean"),
            max_rocof = ("max_rocof","max"),
            instability_rate = ("is_unstable","mean"),
            sample_count = ("sim_id","count") 
        )

        # --- DEBUG PURPOSE --- #

        print(summary)

        # --- #

        profiles = {}
        for cluster_id in summary.index:
            row = summary.loc[cluster_id]

            nadir = float(row["avg_nadir"])
            rocof = float(row["max_rocof"])
            unstable_rate = float(row["instability_rate"])

            nadir_penalty = np.clip((49.5 - nadir) / (49.5 - 47.5), 0.0, 1.0)
            rocof_penalty = np.clip((rocof - 0.5) / (2.5 - 0.5), 0.0, 1.0)

            risk_score = (
                0.50 * nadir_penalty +
                0.35 * unstable_rate +
                0.15 * rocof_penalty
            ) * 100.0

            if nadir < 47.5 or unstable_rate >= 0.4 or risk_score >= 60.0:
                severity = "RED_CRITICAL"
            elif nadir < 48.8 or unstable_rate >= 0.05 or risk_score >= 25.0:
                severity = "YELLOW_WARNING"
            else:
                severity = "GREEN_SAFE"

            profiles[int(cluster_id)] = { # cluster_id is key - Nested dictionary
                "severity":severity,
                "avg_nadir_hz" : round(nadir,3),
                "max_rocof_hz_s":round(rocof,3),
                "instability_rate":round(unstable_rate*100,2),
                "sample_count":int(row["sample_count"])
            }


        return profiles



    def save_artifacts(self):
        os.makedirs(self.model_dir,exist_ok=True)
        joblib.dump(
            self.model,os.path.join(self.model_dir,"stability_rf_model.pkl")
        )
        joblib.dump(
            self.feature_columns,
            os.path.join(self.model_dir,"feature_columns.pkl")
        )
        joblib.dump(
                    self.risk_profiles,
                    os.path.join(self.model_dir,"risk_profiles.pkl")
                )
        joblib.dump(
                            self.feature_defaults,
                            os.path.join(self.model_dir,"feature_defaults.pkl")
                        )

    def load_artifacts(self):
        model_path = os.path.join(self.model_dir,"stability_rf_model.pkl")
        cols_path = os.path.join(self.model_dir,"feature_columns.pkl")
        risk_path = os.path.join(self.model_dir,"risk_profiles.pkl")
        feature_default_path = os.path.join(self.model_dir,"feature_defaults.pkl")


        if not os.path.exists(model_path) or not os.path.exists(cols_path):
            raise FileNotFoundError(
                f"Artifacts not found in directory : {self.model_dir}"
            )

        self.model = joblib.load(model_path)
        self.feature_columns = joblib.load(cols_path)
        self.risk_profiles = joblib.load(risk_path)
        self.explainer = shap.TreeExplainer(self.model)
        self.feature_defaults = joblib.load(feature_default_path)



        print(f"\n[+] Engine Loaded Successfully from '{self.model_dir}'")

    def predict_grid_state(self,raw_scenario_dict:dict) -> dict :
        if self.model is None or self.feature_columns is None:
            raise RuntimeError("ERROR : ENGINE NOT LOADED")

        input_df = pd.DataFrame([raw_scenario_dict])
        encoded_df = pd.get_dummies(input_df)

        aligned_df = encoded_df.reindex(columns=self.feature_columns)
        aligned_df = aligned_df.fillna(self.feature_defaults)

        shap_values = self.explainer.shap_values(aligned_df)

        predicted_cluster = int(self.model.predict(aligned_df)[0])
        probablities = self.model.predict_proba(aligned_df)[0]
        confidence = float(np.max(probablities))

        risk_info = self.risk_profiles.get(predicted_cluster,{
            "severity" : "UNKNOWN",
            "avg_nadir_hz" : None,
            "max_rocof_hz_s" : None,
            "instability_rate" : None,
            "sample_count" : 0,

        })

        class_idx = list(self.model.classes_).index(predicted_cluster)
        vals = shap_values[0,:,class_idx]
        feature_impacts = []
        for i in range(len(self.feature_columns)):
            col_name = self.feature_columns[i]
            shap_val = float(vals[i])
            item = {
                "feature":col_name,
                "impact_score":round(shap_val,4)
            }
            feature_impacts.append(item)

        get_magnitude = lambda item : abs(item["impact_score"])
        feature_impacts.sort(key=get_magnitude,reverse=True)
        top_drivers = [feature_impacts[x] for x in range(0,3)]


        return {
            "predicted_cluster":predicted_cluster,
            "confidence_percentage":round(confidence*100,2),
            "severity" : risk_info["severity"],
            "avg_nadir_hz" : risk_info["avg_nadir_hz"],
            "max_rocof_hz_s" : risk_info["max_rocof_hz_s"],
            "instability_rate" : risk_info["instability_rate"],
            "sample_count" : risk_info["sample_count"],
            "class_probablities":probablities.tolist(),
            "top_risk_drivers":top_drivers
        }

