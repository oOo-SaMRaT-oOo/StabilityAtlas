import sys
import os
# Add root project folder (StabilityAtlas) to Python search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn

from backend.ai.ml_engine import StabilityAtlasEngine

engine = StabilityAtlasEngine(model_dir="ai/assets")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code here runs BEFORE the app starts up
    print(" Booting server: Loading model artifacts...")
    engine.load_artifacts()

    yield

    # Code here runs AFTER the app shuts down
    print(" Shutting down server...")
    

# Initialize Fast API
app = FastAPI(
    title = "StabilityAtlas API",
    description="Backend API for Grid Twin Stability Inference & Physics Engine",
    version="1.0.0",
    lifespan=lifespan
)

# Permits your future React frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic validates that the incoming request contains these exact data types
class ScenarioPayload(BaseModel):
    # --- Context & Scenario Identifier ---
    scenario_type: str = "SOLAR_PEAK_LOW_INERTIA"
    
    # --- Operating Points & Power References (in p.u.) ---
    P_ref1_A: float = 0.30
    P_ref1_B: float = 0.20
    P_ref2_A: float = 0.30
    P_ref2_B: float = 0.20

    # --- Power Limits (in p.u.) ---
    P_max1_A: float = 0.65
    P_min1_A: float = 0.20
    P_max1_B: float = 0.40
    P_min1_B: float = 0.10
    
    # --- Governor & Turbine Response Parameters ---
    T_g1_A: float = 0.2
    T_g1_B: float = 0.4
    T_g2_A: float = 0.2
    T_g2_B: float = 0.4

    R1_A: float = 0.05
    R1_B: float = 0.05
    R2_A: float = 0.05
    R2_B: float = 0.05
    
    # --- System Inertia & Virtual Inertia Controls ---
    H1_A: float = 2.25
    H1_B: float = 1.75
    H2_A: float = 2.25
    H2_B: float = 1.75

    K_virtual1: float = 8.0
    K_virtual2: float = 8.0
    
    # --- Battery Storage Capacities & Damping (in p.u.) ---
    E_cap1: float = 3.0
    E_cap2: float = 3.0

    D1: float = 1.0
    D2: float = 1.0
    
    # --- Tie-Line & Interconnector Limits ---
    T_12: float = 2.5
    P_tie_max: float = 0.10
    
    # --- Disturbance String Categorical ---
    dist_type_1: str = "STEP"

# When App is Visited
@app.get("/")
def health_check():
    return {"status":"online",
            "system":"StabilityAtlas Core Engine v1.0"} 

@app.post("/predict")
def predict_scenario(payload:ScenarioPayload):

    """
    Receives grid scenario inputs from the frontend, runs Random Forest + SHAP,
    and returns predicted cluster, risk metrics, and top physical drivers.

    """

    try:
        scenario_dict = payload.model_dump()
        result = engine.predict_grid_state(scenario_dict)
        return result

    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app",
                host = "127.0.0.1",
                port = 8000,
                reload = True)



