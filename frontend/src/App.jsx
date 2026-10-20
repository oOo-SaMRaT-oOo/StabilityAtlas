import React, { useState, useEffect } from 'react';
import { fetchGridPrediction } from './api';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  ShieldAlert, 
  Sliders, 
  Zap, 
  Gauge, 
  Percent, 
  Layers, 
  TrendingDown, 
  Radio, 
  Database
} from 'lucide-react';

import { GlowingLine,Header_text,GlowingLineSub,FooterSignature} from './styles';

import FrequencyChart from './FrequencyChart';


export default function App() {
  
  // 1. Store current values of the control sliders
  const [params, setParams] = useState({
    Scenario : "SOLAR_PEAK_LOW_INERTIA",
    Virtual_Inertia: 12.0,
    P_ref: 1.0,
    Damping_Factor: 1.0,
  });

  // 2. Store prediction data coming back from Python FastAPI
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 3. Effect hook: Automatically trigger API call when params change
  useEffect(() => {
    const getPrediction = async () => {
      setLoading(true);
      setError(null);

      const env = params.Scenario;

      // 1. Calculate Scenario Averages directly from scenario_factory.py ranges
      let baseH1_A, baseH1_B, baseH2_A, baseH2_B;
      let defaultPref1_A, defaultPref1_B, defaultPref2_A, defaultPref2_B;
      let baseD1, baseD2;

      let baseEcap;
      if (env === "SOLAR_PEAK_LOW_INERTIA") {
        baseEcap = 3.0; // Average of [2.0, 4.0]
      } else if (env === "HEAVY_INDUSTRIAL_INERTIA") {
        baseEcap = 1.5; // Average of [1.0, 2.0]
      } else if (env === "NIGHT_LOW_DEMAND") {
        baseEcap = 2.25; // Average of [1.5, 3.0]
      } else if (env === "EXTREME_STORM_CONTINGENCY") {
        baseEcap = 1.75; // Average of [1.0, 2.5]
      } else { // RENEWABLE_DROUGHT
        baseEcap = 1.0; // Average of [0.5, 1.5]
      }

      if (env === "SOLAR_PEAK_LOW_INERTIA") {
        baseH1_A = 2.25; baseH1_B = 1.75; baseH2_A = 2.25; baseH2_B = 1.75;
        defaultPref1_A = 0.30; defaultPref1_B = 0.20; defaultPref2_A = 0.30; defaultPref2_B = 0.20;
        baseD1 = 1.0; baseD2 = 1.0;

      } else if (env === "HEAVY_INDUSTRIAL_INERTIA") {
        baseH1_A = 6.5; baseH1_B = 5.5; baseH2_A = 6.5; baseH2_B = 5.5;
        defaultPref1_A = 0.60; defaultPref1_B = 0.40; defaultPref2_A = 0.60; defaultPref2_B = 0.40;
        baseD1 = 3.0; baseD2 = 3.0;

      } else if (env === "NIGHT_LOW_DEMAND") {
        baseH1_A = 4.0; baseH1_B = 3.5; baseH2_A = 4.0; baseH2_B = 3.5;
        defaultPref1_A = 0.25; defaultPref1_B = 0.15; defaultPref2_A = 0.25; defaultPref2_B = 0.15;
        baseD1 = 1.5; baseD2 = 1.5;

      } else if (env === "EXTREME_STORM_CONTINGENCY") {
        baseH1_A = 2.25; baseH1_B = 2.0; baseH2_A = 2.25; baseH2_B = 2.0;
        defaultPref1_A = 0.50; defaultPref1_B = 0.30; defaultPref2_A = 0.50; defaultPref2_B = 0.30;
        baseD1 = 0.6; baseD2 = 0.6;

      } else { // RENEWABLE_DROUGHT
        baseH1_A = 3.5; baseH1_B = 3.0; baseH2_A = 3.5; baseH2_B = 3.0;
        defaultPref1_A = 0.50; defaultPref1_B = 0.35; defaultPref2_A = 0.50; defaultPref2_B = 0.35;
        baseD1 = 1.75; baseD2 = 1.75;
      }

      // Translate Macro UI Params to Pydantic ScenarioPayload 
      const payload = {
        scenario_type: env,
        
        // --- Operating Points (scaled in p.u.) ---
        P_ref1_A: defaultPref1_A * params.P_ref,
        P_ref1_B: defaultPref1_B * params.P_ref,
        P_ref2_A: defaultPref2_A * params.P_ref,
        P_ref2_B: defaultPref2_B * params.P_ref,

        // --- Governors, Droop & Power Limits (Fixed Defaults from Factory) ---
        T_g1_A: 0.2, T_g1_B: 0.4, T_g2_A: 0.2, T_g2_B: 0.4,
        R1_A: 0.05, R1_B: 0.05, R2_A: 0.05, R2_B: 0.05,
        P_max1_A: 0.65, P_min1_A: 0.20,
        P_max1_B: 0.40, P_min1_B: 0.10,

        // --- Physical Inertia & Virtual Inertia Controls ---
        H1_A: baseH1_A, H1_B: baseH1_B,
        H2_A: baseH2_A, H2_B: baseH2_B,
        K_virtual1: params.Virtual_Inertia,
        K_virtual2: params.Virtual_Inertia,

        // --- Damping & Tie-Line Limits ---
        D1: baseD1 * params.Damping_Factor, 
        D2: baseD2 * params.Damping_Factor, 
        P_tie_max: 0.10, 

        // --- Battery Energy Storage Capacities (p.u.) ---
        E_cap1: baseEcap,
        E_cap2: baseEcap,

        // --- Disturbance Indicators ---
        dist_type_1: env === "EXTREME_STORM_CONTINGENCY" ? "CASCADE" : "STEP",
      };

      try {
        const data = await fetchGridPrediction(payload);
        setPrediction(data);
      } catch (err) {
        setError("Failed to connect to FastAPI server. Ensure backend is running at http://127.0.0.1:8000");
      } finally {
        setLoading(false);
      }
    
    };

    // Debounce 300ms : So that rapid slider moves don't overwhelm FastAPI
    const timeoutId = setTimeout(getPrediction, 300);
    return () => clearTimeout(timeoutId);
  }, [params]);

  // 4. Helper function to update slider state when user drags a slider
  const handleSliderChange = (name, value) => {
    setParams(prev => ({
      ...prev,
      [name]: isNaN(value)? value : parseFloat(value)
    }));
  };

  const renderSeverityBadge = (severity) => {
  switch (severity) {
    case "GREEN_SAFE":
      return (
        <div className="flex items-center gap-2 text-green-400">
          <CheckCircle size={18} />
          <span>GRID STATE: STABLE</span>
        </div>
      );

    case "YELLOW_WARNING":
      return (
        <div className="flex items-center gap-2 text-yellow-400">
          <AlertTriangle size={18} />
          <span>GRID STATE: ELEVATED RISK</span>
        </div>
      );

    case "RED_CRITICAL":
      
    default:
      return (
        <div className="flex items-center gap-2 text-red-400">
          <ShieldAlert size={18} />
          <span>GRID STATE: UNSTABLE</span>
        </div>
      );
  }
};  


/* HEADER and SLIDER */

return (
  <div className="min-h-screen bg-slate-950 text-slate-100 p-8">

    {/* 1. Dashboard Top Bar Header */}
    <div className="flex justify-between items-center mb-8">
      <div>
        <Header_text text = "StabilityAtlas"/>
        <GlowingLine/>
        <p className="text-slate-400">
          Real-Time Microgrid Stability Simulator</p>

          <GlowingLineSub/>
      </div>

      {/* Dynamic Severity Badge */}
      {prediction && renderSeverityBadge(prediction.severity)}
    </div>

    {/* 2. Main 2-Column Grid Layout */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

      {/* LEFT COLUMN: Control Sliders Panel */}
      <div className="bg-slate-900 rounded-xl p-6 shadow-lg">

        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
          <Sliders className="text-cyan-400" />
          Grid Control Sliders
        </h2>

        {/* Scenario Preset Selector */}
        <div className="mb-6">
          <label className="block mb-2 font-medium text-cyan-300">
            Select Microgrid Scenario Preset
          </label>
          <select
                value={params.Scenario}
                onChange={(e) => handleSliderChange("Scenario", e.target.value)}
                className="w-full bg-slate-800 text-slate-100 border border-slate-700 rounded-lg p-2.5 focus:ring-2 focus:ring-cyan-400 focus:outline-none cursor-pointer">
                <option value="SOLAR_PEAK_LOW_INERTIA">☀️ Solar Peak (Low Physical Inertia)</option>
                <option value="NIGHT_LOW_DEMAND">🌙 Night Low Demand (Low Power Base)</option>
                <option value="HEAVY_INDUSTRIAL_INERTIA">🏭 Heavy Industrial (High Inertia & Damping)</option>
                <option value="RENEWABLE_DROUGHT">🌵 Renewable Drought (Low Battery SOC)</option>
                <option value="EXTREME_STORM_CONTINGENCY">🌪️ Extreme Storm Contingency (High Severity)</option>
            </select>
        </div>



        {/* Slider 1 */}
        <div className="mb-6">
          <label className="block mb-2">
            Virtual Inertia (K_virtual): {params.Virtual_Inertia}
          </label>

          <input
            type="range"
            min="2.0"
            max="20.0"
            step="0.5"
            value={params.Virtual_Inertia}
            onChange={(e) =>
              handleSliderChange("Virtual_Inertia", e.target.value)
            }
            className="w-full accent-cyan-400 bg-slate-800 h-2 rounded-lg cursor-pointer"
          />
        </div>

        {/* Slider 2 */}
        <div className="mb-6">
          <label className="block mb-2">
            Active Power Ref (P_ref): {params.P_ref}
          </label>

          <input
            type="range"
            min="0.5"
            max="1.5"
            step="0.05"
            value={params.P_ref}
            onChange={(e) =>
              handleSliderChange("P_ref", e.target.value)
            }
            className="w-full accent-cyan-400 bg-slate-800 h-2 rounded-lg cursor-pointer"
          />
        </div>

        {/* Slider 3 */}
        <div className="mb-6">
          <label className="block mb-2">
            Damping Factor (D): {params.Damping_Factor}
          </label>

          <input
            type="range"
            min="0.20"
            max="2.00"
            step="0.05"
            value={params.Damping_Factor}
            onChange={(e) =>
              handleSliderChange("Damping_Factor", e.target.value)
            }
            className="w-full accent-cyan-400 bg-slate-800 h-2 rounded-lg cursor-pointer"
          />
        </div>


        {/* Quick-Trigger Stress Presets */}
        <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 mb-6">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2.5 font-mono">
            Quick Stress Test Presets
          </p>
          <div className="grid grid-cols-3 gap-2 text-xs font-mono">
            <button
              onClick={() => setParams(p => ({ ...p, Virtual_Inertia: 2.0, P_ref: 1.45, Damping_Factor: 0.2 }))}
              className="py-2 px-1 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-md transition duration-150 flex items-center justify-center gap-1 font-semibold"
            >
              ⚡ Max Stress
            </button>

            <button
              onClick={() => setParams(p => ({ ...p, Virtual_Inertia: 14.0, P_ref: 0.90, Damping_Factor: 1.2 }))}
              className="py-2 px-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-md transition duration-150 flex items-center justify-center gap-1 font-semibold"
            >
              🛡️ Safe Base
            </button>

            <button
              onClick={() => setParams(p => ({ ...p, Virtual_Inertia: 5.0, P_ref: 1.25, Damping_Factor: 0.5 }))}
              className="py-2 px-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-md transition duration-150 flex items-center justify-center gap-1 font-semibold"
            >
              🌵 Vulnerable
            </button>
          </div>
        </div>



          {/* 🌟 SYSTEM HEALTH & CONNECTION DECK */}
<div className="bg-slate-950 p-4 rounded-lg border border-slate-800 mt-3 font-mono">

  {/* Title */}
  <div className="flex items-center justify-between mb-4">
    <span className="text-xs uppercase tracking-widest text-cyan-400 font-semibold">
      System Health
    </span>

    <span className="text-[10px] text-slate-500">
      LIVE TELEMETRY
    </span>
  </div>

  {/* FastAPI Status */}
  <div className="flex justify-between items-center py-2 border-b border-slate-900">
    <span className="flex items-center gap-2 text-emerald-400">
      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
      FastAPI Backend
    </span>

    <span className="text-slate-400">
      ONLINE
    </span>
  </div>

  {/* API Address */}
  <div className="flex justify-between items-center py-2 border-b border-slate-900">
    <span className="text-slate-500">
      Endpoint
    </span>

    <span className="text-cyan-400">
      127.0.0.1:8000
    </span>
  </div>

  {/* Connection State */}
  <div className="flex justify-between items-center py-2 border-b border-slate-900">
    <span className="text-slate-500">
      Connection
    </span>

    <span
      className={`${
        loading
          ? "text-yellow-400"
          : "text-emerald-400"
      }`}
    >
      {loading ? "SYNCING..." : "CONNECTED"}
    </span>
  </div>

  {/* Debounce */}
  <div className="flex justify-between items-center py-2 border-b border-slate-900">
    <span className="text-slate-500">
      Debounce Window
    </span>

    <span className="text-slate-300">
      300 ms
    </span>
  </div>

  {/* Approximate Latency */}
  <div className="flex justify-between items-center py-2 border-b border-slate-900">
    <span className="text-slate-500">
      Estimated Latency
    </span>

    <span className="text-cyan-400">
      ~18 ms
    </span>
  </div>

  {/* ML Engine */}
  <div className="flex justify-between items-center py-2 border-b border-slate-900">
    <span className="text-slate-500">
      ML Engine
    </span>

    <span className="text-emerald-400">
      Random Forest ✓
    </span>
  </div>

  {/* Explainability */}
  <div className="flex justify-between items-center py-2 border-b border-slate-900">
    <span className="text-slate-500">
      Explainability
    </span>

    <span className="text-amber-400">
      SHAP ACTIVE
    </span>
  </div>

  {/* Last Prediction */}
  <div className="flex justify-between items-center pt-3">
    <span className="text-slate-500">
      Last Prediction
    </span>

    <span className="text-slate-300">
      {prediction ? "Completed" : "Waiting..."}
    </span>
  </div>

</div>


      </div>


      {/* RIGHT COLUMN */}

      {/* RIGHT COLUMN: Prediction Result & Telemetry Panel */}
      <div className="bg-slate-900 rounded-xl p-6 shadow-lg border border-slate-800 flex flex-col">

      {/* 1. Header Section */}
      <div className="border-b border-slate-800 pb-4 mb-6">
        <h2 className="text-2xl font-semibold text-slate-100 flex items-center gap-2">
          <Activity className="text-cyan-400" />
          Prediction Result
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Real-time ML Model Telemetry & Physics Metrics
        </p>
      </div>


      {/* State Handler: Loading Spinner */}
      {loading && (
        <div className="flex-1 flex flex-col items-center justify-center py-12 text-slate-400">
          <div className="w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mb-3"></div>
          <p className="text-sm font-medium">Running physics inference engine ...</p>
        </div>
      )}


      {/* State Handler: Error Display */}
      {error && !loading && (
        <div className="flex-1 flex items-center justify-center py-8 px-4 bg-red-950/30 rounded-lg border border-red-900/50 text-red-400 text-center">
          <div className="flex flex-col items-center gap-2">
            <AlertTriangle className="text-red-400" size={24} />
            <p className="text-sm font-semibold">Simulation Error ...</p>
            <p className="text-xs text-red-300/80">{error}</p>
          </div>
        </div>
      )}

      {/* Telemetry Content (When data is ready) */}
      {!loading && !error && (
        <div className="space-y-4">

      {/* 2. Severity Badge Section */}
      <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 flex justify-between items-center mb-4">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Severity Badge
        </span>
        <div>
          {prediction ? renderSeverityBadge(prediction.severity) : (
            <span className="text-slate-500 text-sm">Awaiting simulation ...</span>
                )}
              </div>
            </div>
            </div>
          )
          }


        {/* 3. Metrics Grid - Row 1: Confidence & Cluster ID */}
        <div className="grid grid-cols-2 gap-3 mb-3">

            {/* Confidence (%) */}
            <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 flex items-center gap-3">
              <div className="p-2 bg-cyan-500/10 rounded-md text-cyan-400">
                <Percent size={20} />
              </div>
              <div>
                <p className="text-xs text-slate-400">Confidence</p>
                <p className="text-lg font-bold text-slate-100">
                  {prediction?.confidence_percentage ? `${(prediction.confidence_percentage).toFixed(1)}%` : 'Waiting ...'}
                </p>
              </div>
            </div>

            {/* Cluster ID */}
            <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 flex items-center gap-3">
              <div className="p-2 bg-purple-500/10 rounded-md text-purple-400">
                <Layers size={20} />
              </div>
              <div>
                <p className="text-xs text-slate-400">Cluster ID</p>
                <p className="text-lg font-bold text-slate-100">
                  {prediction?.predicted_cluster !== undefined ? `Cluster #${prediction.predicted_cluster}` : 'Waiting ...'}
                </p>
              </div>
            </div>
      </div>

      {/* 4. Metrics Grid - Row 2: Avg Frequency Nadir & Max RoCoF */}

      <div className="grid grid-cols-2 gap-3 mb-3">

        {/* Avg Frequency Nadir */}
        <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 rounded-md text-blue-400">
            <TrendingDown size={20} />
          </div>
          <div>
            <p className="text-xs text-slate-400">Avg Frequency Nadir</p>
            <p className="text-lg font-bold text-slate-100">
              {prediction?.avg_nadir_hz !== undefined ? `${prediction.avg_nadir_hz.toFixed(2)} Hz` : 'Waiting ...'}
            </p>
          </div>
        </div>

        {/* Max RoCoF */}
        <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 flex items-center gap-3">
          <div className="p-2 bg-amber-500/10 rounded-md text-amber-400">
            <Radio size={20} />
          </div>
          <div>
            <p className="text-xs text-slate-400">Max RoCoF</p>
            <p className="text-lg font-bold text-slate-100">
              {prediction?.max_rocof_hz_s !== undefined ? `${prediction.max_rocof_hz_s.toFixed(2)} Hz/s` : 'Waiting ...'}
            </p>
          </div>
        </div>
    </div>

    {/* 5. Metrics Grid - Row 3: Instability Probability & Sample Count */}
  <div className="grid grid-cols-2 gap-3 mb-3">

    {/* Instability Probability */}
    <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 flex items-center gap-3">
      <div className="p-2 bg-rose-500/10 rounded-md text-rose-400 shrink-0">
        <Gauge size={20} />
      </div>
      <div>
        <p className="text-xs text-slate-400">Instability Probability</p>
        <p className="text-lg font-bold text-rose-400">
          {prediction?.instability_rate !== undefined 
            ? `${(prediction.instability_rate).toFixed(1)}%` 
            : 'Waiting ...'}
        </p>
      </div>
    </div>

    {/* Sample Count */}
    <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 flex items-center gap-3">
      <div className="p-2 bg-emerald-500/10 rounded-md text-emerald-400 shrink-0">
        <Database size={20} />
      </div>
      <div>
        <p className="text-xs text-slate-400">Sample Count</p>
        <p className="text-lg font-bold text-slate-100">
          {prediction?.sample_count !== undefined 
            ? prediction.sample_count.toLocaleString() 
            : 'Waiting ...'}
        </p>
      </div>
    </div>
  </div>

  {/* 6. SHAP Feature Impact Section */}
<div className="bg-slate-950 p-4 rounded-lg border border-slate-800 mt-3">
  <div className="flex items-center justify-between mb-3">
    <div className="flex items-center gap-2">
      <Zap size={16} className="text-amber-400" />
      <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
        Top SHAP Risk Drivers
      </span>
    </div>
    <span className="text-[10px] text-slate-500 font-mono">Impact Score</span>
  </div>

  <div className="space-y-2.5">
    {prediction?.top_risk_drivers && prediction.top_risk_drivers.length > 0 ? (
      prediction.top_risk_drivers.map((driver, idx) => {
        // Find max impact score for proportional bar width scaling
        const maxImpact = Math.max(
          ...prediction.top_risk_drivers.map((d) => Math.abs(d.impact_score)),
          0.0001
        );
        const barWidth = `${Math.min((Math.abs(driver.impact_score) / maxImpact) * 100, 100)}%`;
        const isPositive = driver.impact_score > 0;

        return (
          <div key={idx} className="space-y-1"> 
            <div className="flex justify-between items-center text-xs">
              <span className="font-mono text-slate-300 truncate max-w-[200px]" title={driver.feature}>
                {driver.feature}
              </span>
              <span className={`font-mono font-semibold ${isPositive ? 'text-rose-400' : 'text-emerald-400'}`}>
                {isPositive ? `+${driver.impact_score}` : driver.impact_score}
              </span>
            </div>

            {/* Visual SHAP Impact Bar */}
            <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  isPositive ? 'bg-rose-500' : 'bg-emerald-500'
                }`}
                style={{ width: barWidth }}
              />
            </div>
          </div>
        );
      })
    ) : (
      <p className="text-xs text-slate-500 italic">No SHAP attribution data available</p>
    )}
  </div>
</div>



<FrequencyChart
    nadirHz={prediction?.avg_nadir_hz ?? 50}
    rocof={prediction?.max_rocof_hz_s ?? 0}
/>
      </div>
    </div>
    <br></br><GlowingLine/>

    <FooterSignature />

        </div>


    );
        }
