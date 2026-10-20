import numpy as np

def generate_grid_scenario(seed: int = None):

    if seed is not None:
        np.random.seed(seed)

    # TIER 1: ENVIRONMENT CONTEXT SELECTION

    SCENARIO_TYPES = [
        "SOLAR_PEAK_LOW_INERTIA",
        "NIGHT_LOW_DEMAND",
        "HEAVY_INDUSTRIAL_INERTIA",
        "RENEWABLE_DROUGHT",
        "EXTREME_STORM_CONTINGENCY" 
    ]

    selected_env = np.random.choice(SCENARIO_TYPES)

    # Disturbance Profile 
    
    DISTURBANCE_TYPES = ["STEP", "RAMP", "PULSE", "CASCADE", "NOISY_STEP"]
    dist_type_1 = np.random.choice(DISTURBANCE_TYPES, p=[0.35, 0.25, 0.15, 0.15, 0.10])
    dist_type_2 = np.random.choice(DISTURBANCE_TYPES, p=[0.35, 0.25, 0.15, 0.15, 0.10])

    params = {
        "scenario_type": selected_env,
        "dist_type_1": dist_type_1,
        "dist_type_2": dist_type_2,
        "omega_0": 2 * np.pi * 50,

        # Governor / Droop Defaults
        "T_g1_A": 0.2, "T_g1_B": 0.4, "T_g2_A": 0.2, "T_g2_B": 0.4,
        "R1_A": 0.05, "R1_B": 0.05, "R2_A": 0.05, "R2_B": 0.05,
        "gamma1_A": 0.5, "gamma1_B": 0.5, "gamma2_A": 0.5, "gamma2_B": 0.5,

        "ramp_up1_A": 0.1, "ramp_down1_A": 0.1,
        "ramp_up1_B": 0.08, "ramp_down1_B": 0.08,
        "ramp_up2_A": 0.1, "ramp_down2_A": 0.1,
        "ramp_up2_B": 0.08, "ramp_down2_B": 0.08,

        "K_i1": 0.15, "K_i2": 0.15,
        "B1": 20.0, "B2": 20.0,
        "K_emergency": 15.0,
        "T_12": 2.5, "P_tie_max": 0.10,
    }

    # STOCHASTIC PARAMETER ADJUSTMENTS BASED ON CONTEXT

    if selected_env == "SOLAR_PEAK_LOW_INERTIA":
        params["H1_A"] = np.random.uniform(1.5, 3.0); params["H1_B"] = np.random.uniform(1.0, 2.5)
        params["H2_A"] = np.random.uniform(1.5, 3.0); params["H2_B"] = np.random.uniform(1.0, 2.5)
        params["K_virtual1"] = np.random.uniform(12.0, 20.0); params["K_virtual2"] = np.random.uniform(12.0, 20.0)
        params["E_cap1"] = np.random.uniform(2.0, 4.0); params["E_cap2"] = np.random.uniform(2.0, 4.0)
        params["D1"] = np.random.uniform(0.5, 1.5); params["D2"] = np.random.uniform(0.5, 1.5)
        params["P_ref1_A"] = 0.3; params["P_ref1_B"] = 0.2
        params["P_ref2_A"] = 0.3; params["P_ref2_B"] = 0.2

    elif selected_env == "HEAVY_INDUSTRIAL_INERTIA":
        params["H1_A"] = np.random.uniform(5.0, 8.0); params["H1_B"] = np.random.uniform(4.0, 7.0)
        params["H2_A"] = np.random.uniform(5.0, 8.0); params["H2_B"] = np.random.uniform(4.0, 7.0)
        params["K_virtual1"] = np.random.uniform(2.0, 8.0); params["K_virtual2"] = np.random.uniform(2.0, 8.0)
        params["E_cap1"] = np.random.uniform(1.0, 2.0); params["E_cap2"] = np.random.uniform(1.0, 2.0)
        params["D1"] = np.random.uniform(2.0, 4.0); params["D2"] = np.random.uniform(2.0, 4.0)
        params["P_ref1_A"] = 0.6; params["P_ref1_B"] = 0.4
        params["P_ref2_A"] = 0.6; params["P_ref2_B"] = 0.4

    elif selected_env == "NIGHT_LOW_DEMAND":
        params["H1_A"] = np.random.uniform(3.0, 5.0); params["H1_B"] = np.random.uniform(2.5, 4.5)
        params["H2_A"] = np.random.uniform(3.0, 5.0); params["H2_B"] = np.random.uniform(2.5, 4.5)
        params["K_virtual1"] = np.random.uniform(5.0, 10.0); params["K_virtual2"] = np.random.uniform(5.0, 10.0)
        params["E_cap1"] = np.random.uniform(1.5, 3.0); params["E_cap2"] = np.random.uniform(1.5, 3.0)
        params["D1"] = np.random.uniform(1.0, 2.0); params["D2"] = np.random.uniform(1.0, 2.0)
        params["P_ref1_A"] = 0.25; params["P_ref1_B"] = 0.15
        params["P_ref2_A"] = 0.25; params["P_ref2_B"] = 0.15

    elif selected_env == "EXTREME_STORM_CONTINGENCY":
        params["H1_A"] = np.random.uniform(1.0, 3.5); params["H1_B"] = np.random.uniform(1.0, 3.0)
        params["H2_A"] = np.random.uniform(1.0, 3.5); params["H2_B"] = np.random.uniform(1.0, 3.0)
        params["K_virtual1"] = np.random.uniform(10.0, 18.0); params["K_virtual2"] = np.random.uniform(10.0, 18.0)
        params["E_cap1"] = np.random.uniform(1.0, 2.5); params["E_cap2"] = np.random.uniform(1.0, 2.5)
        params["D1"] = np.random.uniform(0.2, 1.0); params["D2"] = np.random.uniform(0.2, 1.0)
        params["P_ref1_A"] = 0.5; params["P_ref1_B"] = 0.3
        params["P_ref2_A"] = 0.5; params["P_ref2_B"] = 0.3

    else:  # RENEWABLE_DROUGHT
        params["H1_A"] = np.random.uniform(2.5, 4.5); params["H1_B"] = np.random.uniform(2.0, 4.0)
        params["H2_A"] = np.random.uniform(2.5, 4.5); params["H2_B"] = np.random.uniform(2.0, 4.0)
        params["K_virtual1"] = np.random.uniform(4.0, 10.0); params["K_virtual2"] = np.random.uniform(4.0, 10.0)
        params["E_cap1"] = np.random.uniform(0.5, 1.5); params["E_cap2"] = np.random.uniform(0.5, 1.5)
        params["D1"] = np.random.uniform(1.0, 2.5); params["D2"] = np.random.uniform(1.0, 2.5)
        params["P_ref1_A"] = 0.5; params["P_ref1_B"] = 0.35
        params["P_ref2_A"] = 0.5; params["P_ref2_B"] = 0.35

    # Power Limits
    params["P_max1_A"] = 0.65; params["P_min1_A"] = 0.2
    params["P_max1_B"] = 0.40; params["P_min1_B"] = 0.1
    params["P_max2_A"] = 0.65; params["P_min2_A"] = 0.2
    params["P_max2_B"] = 0.40; params["P_min2_B"] = 0.1

    # Initial State of Charge
    if selected_env == "RENEWABLE_DROUGHT":
        soc1_init, soc2_init = np.random.uniform(0.1, 0.3), np.random.uniform(0.1, 0.3)
    elif selected_env == "SOLAR_PEAK_LOW_INERTIA":
        soc1_init, soc2_init = np.random.uniform(0.7, 0.95), np.random.uniform(0.7, 0.95)
    else:
        soc1_init, soc2_init = np.random.uniform(0.3, 0.8), np.random.uniform(0.3, 0.8)

    y0 = [
        0.0,
        params["P_ref1_A"], params["P_ref1_B"], 0.0, soc1_init,
        0.0,
        params["P_ref2_A"], params["P_ref2_B"], 0.0, soc2_init,
        0.0
    ]

    # DYNAMIC DISTURBANCE BUILDER FUNCTION
    def build_disturbance_function(base_load, dist_type, max_severity):
        fault_time = np.random.uniform(2.0, 6.0)
        mag = np.random.uniform(0.1, max_severity) if dist_type != "NONE" else 0.0
        
        # Additional shape properties
        ramp_duration = np.random.uniform(1.5, 4.0)
        pulse_width = np.random.uniform(0.5, 2.0)
        cascade_delay = np.random.uniform(1.0, 3.0)
        noise_std = np.random.uniform(0.01, 0.03)

        def disturbance(t):
            if t < fault_time:
                return base_load
            
            if dist_type == "STEP":
                return base_load + mag

            elif dist_type == "RAMP":
                # Gradual power drop/increase (e.g., cloud covering solar panel)
                progress = min(1.0, (t - fault_time) / ramp_duration)
                return base_load + (mag * progress)

            elif dist_type == "PULSE":
                # Temporary load spike that recovers
                if fault_time <= t <= (fault_time + pulse_width):
                    return base_load + mag
                return base_load

            elif dist_type == "CASCADE":
                # First event at fault_time, second larger event shortly after
                if t >= (fault_time + cascade_delay):
                    return base_load + mag * 1.8
                return base_load + mag

            elif dist_type == "NOISY_STEP":
                # Step fault accompanied by continuous high-frequency load noise
                gaussian_noise = np.random.normal(0, noise_std)
                return base_load + mag + gaussian_noise

            return base_load

        return disturbance

    max_sev = np.random.uniform(0.5,0.7) if selected_env == "EXTREME_STORM_CONTINGENCY" else 0.50

    base_load_1 = params["P_ref1_A"] + params["P_ref1_B"]
    base_load_2 = params["P_ref2_A"] + params["P_ref2_B"]

    dist1 = build_disturbance_function(base_load_1, dist_type_1, max_sev)
    dist2 = build_disturbance_function(base_load_2, dist_type_2, max_sev)

    return params, y0, dist1, dist2