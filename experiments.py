def exp_swing_equation():

    # Understanding Swing Equation :

    import numpy as np
    import matplotlib.pyplot as plt
    from backend.physics.swing_equation import simulate_frequency_response

    # 1. Define Grid Parameters
    H = 5.0        # Robust inertia
    D = 1.0        # System damping
    P_m = 1.0      # Mechanical power at 1.0 p.u.
    P_e = 1.15     # Sudden step increase in load to 1.15 p.u. (15% overload)

    NOMINAL_FREQ_HZ = 50.0
    omega_0 = 2 * np.pi * NOMINAL_FREQ_HZ

    # 2. Simulation Time setup
    t_span = (0.0, 10.0)  # Simulate 10 seconds
    t_eval = np.linspace(0, 10, 500) # 500 time points
    y0 = [0.0]            # Start at nominal frequency (deviation = 0)

    # 3. Run solver
    solution = simulate_frequency_response(t_span, y0, H, D, P_m, P_e, omega_0, t_eval)

    # 4. Convert deviation from rad/s back to Hz for plotting
    freq_deviation_hz = solution.y[0] / (2 * np.pi)
    actual_frequency_hz = NOMINAL_FREQ_HZ + freq_deviation_hz

    # 5. Plot the result
    plt.figure(figsize=(10, 5))
    plt.plot(solution.t, actual_frequency_hz, label="Grid Frequency (Hz)", color='crimson', lw=2)
    plt.axhline(NOMINAL_FREQ_HZ, color='black', linestyle='--', alpha=0.5, label="Nominal (50Hz)")
    plt.title("Transient Frequency Response After 15% Load Step")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Frequency (Hz)")
    plt.grid(True)
    plt.legend()
    plt.show()

def governor_equation():

    # Understanding Governor Action :

    import numpy as np
    import matplotlib.pyplot as plt
    from backend.physics.governors import simulate_governed_response

    # Grid & Governor Parameters
    H = 5.0        # Inertia
    D = 1.0        # Damping
    P_ref = 1.0    # Baseline mechanical setpoint
    P_e = 1.15     # Sudden load increase to 1.15 p.u.

    T_g = 0.5      # Governor time constant (0.5 seconds delay)
    R = 0.05       # 5% Droop characteristic (standard industry value)

    NOMINAL_FREQ_HZ = 50.0
    omega_0 = 2 * np.pi * NOMINAL_FREQ_HZ

    # Simulation Setup
    t_span = (0.0, 20.0) # Let's look at 20 seconds to see the recovery
    t_eval = np.linspace(0, 20, 1000)

    # CRITICAL: Our initial state vector now has TWO elements!
    # y0 = [initial_delta_omega, initial_P_m]
    y0 = [0.0, 1.0] 

    # Run solver
    sol = simulate_governed_response(t_span, y0, H, D, P_e, T_g, R, P_ref, omega_0, t_eval)

    # Extract and convert results
    freq_hz = NOMINAL_FREQ_HZ + (sol.y[0] / (2 * np.pi))
    dynamic_Pm = sol.y[1]

    # Plotting the dual reality: Frequency and Mechanical Power
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Top Plot: Frequency
    ax1.plot(sol.t, freq_hz, color='crimson', lw=2, label="Governed Frequency")
    ax1.axhline(50.0, color='black', linestyle='--', alpha=0.5)
    ax1.set_ylabel("Frequency (Hz)")
    ax1.set_title("Grid Dynamics with Active Governor Control")
    ax1.grid(True)
    ax1.legend()

    # Bottom Plot: Mechanical Power vs Electrical Load
    ax2.plot(sol.t, dynamic_Pm, color='blue', lw=2, label="Mechanical Power ($P_m$)")
    ax2.axhline(P_e, color='orange', linestyle=':', lw=2, label="Electrical Load ($P_e$)")
    ax2.set_xlabel("Time (seconds)")
    ax2.set_ylabel("Power (p.u.)")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()

def exp_pulse_disturbance():

    import numpy as np
    import matplotlib.pyplot as plt
    from backend.physics.governors import simulate_governed_response
    from backend.physics.disturbances import pulse_disturbance

    # Grid/Governor Setup
    H, D, P_ref, T_g, R = 5.0, 1.0, 1.0, 0.5, 0.05
    omega_0 = 2 * np.pi * 50.0

    # Define the dynamic disturbance profile using a lambda function wrapper
    # Pulse from t=1.0s to t=1.2s, adding +0.4 p.u. load during the fault

    dist_profile = lambda t: pulse_disturbance(t, t_start=1.0, t_clear=1.2, P_base=1.0, P_fault=0.4)

    # Simulation configuration
    t_span = (0.0, 15.0)
    t_eval = np.linspace(0, 15, 1000)
    y0 = [0.0, 1.0] # Initial frequency deviation=0, initial Pm=1.0

    # Solve
    sol = simulate_governed_response(t_span, y0, H, D, dist_profile, T_g, R, P_ref, omega_0, t_eval)

    # Plotting
    freq_hz = 50.0 + (sol.y[0] / (2 * np.pi))
    dynamic_Pe = [dist_profile(t) for t in sol.t] # Reconstruct Pe for plotting

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    ax1.plot(sol.t, freq_hz, color='purple', lw=2)
    ax1.axhline(50.0, color='black', linestyle='--', alpha=0.5)
    ax1.set_ylabel("Frequency (Hz)")
    ax1.set_title("Grid Response to a 200ms Temporary Pulse Fault")
    ax1.grid(True)

    ax2.plot(sol.t, sol.y[1], color='blue', lw=2, label="Mechanical Power ($P_m$)")
    ax2.plot(sol.t, dynamic_Pe, color='orange', linestyle='--', label="Electrical Load ($P_e$)")
    ax2.set_ylabel("Power (p.u.)")
    ax2.set_xlabel("Time (seconds)")
    ax2.grid(True)
    ax2.legend()
    plt.tight_layout()
    plt.show()

def exp_agc_restoration():
    import numpy as np
    import matplotlib.pyplot as plt
    from backend.physics.governors import simulate_governed_response
    from backend.physics.disturbances import step_disturbance

    # Grid, Governor, and Secondary Control Setup
    H, D, P_ref, T_g, R = 5.0, 1.0, 1.0, 0.5, 0.05
    K_i = 5.0  # Integral Gain for AGC Secondary restoration
    omega_0 = 2 * np.pi * 50.0

    # Define a permanent step increase of +0.15 p.u. load at t=1.0s
    dist_profile = lambda t: step_disturbance(t, t_start=1.0, P_base=1.0, P_delta=0.15)

    # Simulation Setup
    t_span = (0.0, 30.0) # 30 seconds to witness complete integral restoration
    t_eval = np.linspace(0, 30, 1500)

    # Initial states: [delta_omega=0, P_m=1.0, P_agc=0.0]
    y0 = [0.0, 1.0, 0.0]

    # Solve the system
    sol = simulate_governed_response(t_span, y0, H, D, dist_profile, T_g, R, P_ref, K_i, omega_0, t_eval)

    # Convert results
    freq_hz = 50.0 + (sol.y[0] / (2 * np.pi))
    dynamic_Pe = [dist_profile(t) for t in sol.t]

    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    ax1.plot(sol.t, freq_hz, color='darkgreen', lw=2, label="AGC Restored Frequency")
    ax1.axhline(50.0, color='black', linestyle='--', alpha=0.5)
    ax1.set_ylabel("Frequency (Hz)")
    ax1.set_title("Grid Frequency Restoration via Automatic Generation Control (AGC)")
    ax1.grid(True)
    ax1.legend()

    ax2.plot(sol.t, sol.y[1], color='blue', lw=2, label="Mechanical Power ($P_m$)")
    ax2.plot(sol.t, dynamic_Pe, color='orange', linestyle='--', label="Electrical Load ($P_e$)")
    ax2.set_ylabel("Power (p.u.)")
    ax2.set_xlabel("Time (seconds)")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()

def exp_multimachine_load_sharing():
    import numpy as np
    import matplotlib.pyplot as plt
    from backend.physics.governors import simulate_multimachine_response
    from backend.physics.disturbances import step_disturbance

    # Define system configurations inside a parameter dictionary
    params = {
        'H1': 3.0, 'H2': 7.0,       # Total Grid Inertia = 10.0
        'D1': 0.5, 'D2': 0.5,       # Damping contributions
        'T_g1': 0.2, 'T_g2': 0.8,   # Gen 1 is fast, Gen 2 is slow
        'R1': 0.04, 'R2': 0.08,     # Gen 1 has tighter droop (takes more load)
        'P_ref1': 0.6, 'P_ref2': 0.4, # Baseload: Gen 1 supplies 0.6, Gen 2 supplies 0.4 (Total=1.0)
        'gamma1': 0.7, 'gamma2': 0.3, # AGC sharing factor
        'K_i': 3.0,                 # Central AGC Gain
        'omega_0': 2 * np.pi * 50.0
    }

    # Creation of disturbance function for each time stamp
    dist_profile = lambda t: step_disturbance(t, t_start=1.0, P_base=1.0, P_delta=0.20)

    # Setting time for simulation
    t_span = (0.0, 25.0)
    t_eval = np.linspace(0, 25, 1200)

    # Providing initial conditions
    y0 = [0.0, params['P_ref1'], params['P_ref2'], 0.0]

    # Performing simulation
    sol = simulate_multimachine_response(t_span, y0, params, dist_profile, t_eval)

    freq_hz = 50.0 + (sol.y[0] / (2 * np.pi))
    P_m1_sol = sol.y[1]
    P_m2_sol = sol.y[2]
    dynamic_Pe = [dist_profile(t) for t in sol.t]

    # Plot results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    
    # Frequency Subplot
    ax1.plot(sol.t, freq_hz, color='crimson', lw=2.5, label="Interconnected Grid Frequency")
    ax1.axhline(50.0, color='black', linestyle='--', alpha=0.5)
    ax1.set_ylabel("Frequency (Hz)")
    ax1.set_title("Multi-Generator Transient Response & Load Sharing Profile")
    ax1.grid(True)
    ax1.legend()

    # Power Sharing Subplot
    ax2.plot(sol.t, dynamic_Pe, color='orange', linestyle=':', lw=2, label="Total Electrical Load ($P_e$)")
    ax2.plot(sol.t, P_m1_sol, color='blue', lw=2, label="Gen 1 Power ($P_{m1}$ - Fast, Droop=4%)")
    ax2.plot(sol.t, P_m2_sol, color='purple', lw=2, label="Gen 2 Power ($P_{m2}$ - Slow, Droop=8%)")
    ax2.plot(sol.t, P_m1_sol + P_m2_sol, color='black', linestyle='--', alpha=0.7, label="Total Gen ($P_{m1} + P_{m2}$)")
    ax2.set_ylabel("Power (p.u.)")
    ax2.set_xlabel("Time (seconds)")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()


def exp_virtual_inertia_rescue():
    import numpy as np
    import matplotlib.pyplot as plt
    from backend.physics.governors import simulate_low_inertia_ffr_response
    from backend.physics.disturbances import step_disturbance

    # Parameters modeling a highly fragile, low-inertia grid (70% reduction in H)
    base_params = {
        'H1': 0.8, 'H2': 1.2,       # Massive drop! Total Grid Inertia is now only 2.0!
        'D1': 0.5, 'D2': 0.5,
        'T_g1': 0.2, 'T_g2': 0.8,
        'R1': 0.04, 'R2': 0.08,
        'P_ref1': 0.6, 'P_ref2': 0.4,
        'gamma1': 0.7, 'gamma2': 0.3,
        'K_i': 3.0,
        'T_battery': 0.05,          # Battery inverter reacts in a blistering 50 milliseconds!
        'omega_0': 2 * np.pi * 50.0
    }

    dist_profile = lambda t : step_disturbance(t,t_start = 1.0, P_base = 1.0,P_delta = 0.20)
    t_span = (0.0,15.0)
    t_eval = np.linspace(0,15,1500)

    # RUN CASE A : K_VIRTUAL = 0.0
    params_no_battery = base_params.copy() 
    params_no_battery["K_virtual"] = 0.0
    y0_a = [0.0,base_params["P_ref1"],base_params["P_ref2"],0.0,0.0]
    sol_a = simulate_low_inertia_ffr_response(t_span,y0_a,params_no_battery,dist_profile,t_eval)

    # RUN CASE B : K_VIRTUAL = 15.0
    params_no_battery = base_params.copy() 
    params_no_battery["K_virtual"] = 15.0
    y0_b = [0.0,base_params["P_ref1"],base_params["P_ref2"],0.0,0.0]
    sol_b = simulate_low_inertia_ffr_response(t_span,y0_a,params_no_battery,dist_profile,t_eval)

    freq_hz_unprotected = 50.0 + (sol_a.y[0] / (2*np.pi))
    freq_hz_protected = 50.0 + (sol_b.y[0] / (2*np.pi))
    
    P_battery_sol = sol_b.y[4]

    # Plot the comparative analysis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    ax1.plot(sol_a.t, freq_hz_unprotected, color='black', linestyle='--', lw=2, label="Unprotected Low-Inertia Grid (No Battery)")
    ax1.plot(sol_b.t, freq_hz_protected, color='dodgerblue', lw=2.5, label="Protected Grid (Virtual Inertia Active)")
    ax1.axhline(50.0, color='grey', linestyle=':', alpha=0.7)
    ax1.set_ylabel("Grid Frequency (Hz)")
    ax1.set_title("Modern Grid Crisis: Physical Low-Inertia vs. Digital Virtual Inertia Stabilization")
    ax1.grid(True)
    ax1.legend()

    ax2.plot(sol_b.t, P_battery_sol, color='lime', lw=2.5, label="Battery Power Injection ($P_{ffr}$)")
    ax2.plot(sol_b.t, sol_b.y[1], color='blue', alpha=0.6, label="Gen 1 Mechanical ($P_{m1}$)")
    ax2.plot(sol_b.t, sol_b.y[2], color='purple', alpha=0.6, label="Gen 2 Mechanical ($P_{m2}$)")
    ax2.axhline(0.0, color='grey', linestyle='-', alpha=0.3)
    ax2.set_ylabel("Power Outjections (p.u.)")
    ax2.set_xlabel("Time (seconds)")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()

def exp_battery_depletion():
    import numpy as np
    import matplotlib.pyplot as plt
    from backend.physics.governors import simulate_low_inertia_soc_response
    from backend.physics.disturbances import step_disturbance

    params = {
        'H1': 0.8, 'H2': 1.2,        # Low physical inertia (Total H = 2.0)
        'D1': 0.5, 'D2': 0.5,
        'T_g1': 0.3, 'T_g2': 0.9,    # Sluggish mechanical governors
        'R1': 0.04, 'R2': 0.08,
        'P_ref1': 0.6, 'P_ref2': 0.4,
        'gamma1': 0.7, 'gamma2': 0.3,
        'K_i': 3.0,
        'K_virtual': 20.0,           # Highly aggressive virtual inertia
        'T_battery': 0.05,           # Fast response time
        'E_cap': 0.08,               # Tiny energy reservoir to force depletion!
        'omega_0': 2 * np.pi * 50.0
    }

    dist_profile = lambda t: step_disturbance(t, t_start=1.0, P_base=1.0, P_delta=0.25)
    
    t_span = (0.0, 10.0)
    t_eval = np.linspace(0, 10, 1000)

    y0 = [0.0, params['P_ref1'], params['P_ref2'], 0.0, 0.0, 0.04]

    sol = simulate_low_inertia_soc_response(t_span, y0, params, dist_profile, t_eval)
    freq_hz = 50.0 + (sol.y[0] / (2 * np.pi))
    P_m1 = sol.y[1]
    P_m2 = sol.y[2]
    P_ffr = sol.y[4]
    SoC = sol.y[5]

    # Plot
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 10), sharex=True)

    # Frequency Subplot
    ax1.plot(sol.t, freq_hz, color='crimson', lw=2.5, label="Grid Frequency (SoC Constrained)")
    ax1.axhline(50.0, color='grey', linestyle=':', alpha=0.7)
    ax1.set_ylabel("Frequency (Hz)")
    ax1.set_title("Grid Collapse: Battery Depletes Mid-Rescue")
    ax1.grid(True)
    ax1.legend()

    # Power Outputs Subplot
    ax2.plot(sol.t, P_ffr, color='lime', lw=2.5, label="Battery FFR Power ($P_{ffr}$)")
    ax2.plot(sol.t, P_m1, color='blue', alpha=0.7, label="Gen 1 Power ($P_{m1}$)")
    ax2.plot(sol.t, P_m2, color='purple', alpha=0.7, label="Gen 2 Power ($P_{m2}$)")
    ax2.set_ylabel("Power (p.u.)")
    ax2.grid(True)
    ax2.legend()

    # State of Charge Subplot
    ax3.plot(sol.t, SoC * 100.0, color='gold', lw=2.5, label="Battery State of Charge (%)")
    ax3.axhline(0.0, color='red', linestyle='--', alpha=0.5, label="Empty Limit")
    ax3.set_ylabel("Battery SoC (%)")
    ax3.set_xlabel("Time (seconds)")
    ax3.grid(True)
    ax3.legend()

    plt.tight_layout()
    plt.show()

def exp_multi_area_tieline():
    import numpy as np
    import matplotlib.pyplot as plt
    from backend.physics.governors import multi_area_tie_system_ode
    from backend.physics.disturbances import step_disturbance
    from scipy.integrate import solve_ivp

    params = {
        # Area 1: Low Inertia Green Grid
        'H1': 1.5, 'D1': 0.4, 'T_g1': 0.2, 'R1': 0.04,
        'P_ref1': 0.5, 'gamma1': 1.0, 'K_i1': 1.5, 'B1': 20.0,
        'K_virtual1': 10.0, 'E_cap1': 0.5,
        
        # Area 2: High Inertia Heavy Conventional Grid
        'H2': 6.0, 'D2': 0.6, 'T_g2': 0.6, 'R2': 0.05,
        'P_ref2': 0.5, 'gamma2': 1.0, 'K_i2': 0.3, 'B2': 40.0,
        
        # Transmission Link Synchronizing Coefficient
        'T_12': 2.5,
        'omega_0': 2 * np.pi * 50.0
    }

    dist_profile1 = lambda t : step_disturbance(t,t_start=1.0,P_base = 0.5,P_delta = 0.30)
    dist_profile2 = lambda t : 0.5

    t_span = (0.0,25.0)
    t_eval = np.linspace(0,25,2500)

    # Initial Vector: 
    # [dw1, Pm1, Pagc1, dw2, Pm2, Pagc2, dP_tie, SoC1]
    y0 = [0.0, 0.5, 0.0, 0.0, 0.5, 0.0, 0.0, 0.80]

    sol = solve_ivp(
        fun=multi_area_tie_system_ode,
        t_span=t_span,
        y0=y0,
        args=(params, dist_profile1, dist_profile2),
        method='RK45',
        t_eval=t_eval,
        max_step=0.01
    )

    f1 = 50.0 + (sol.y[0] / (2*np.pi))
    f2 = 50.0 + (sol.y[3] / (2*np.pi))
    P_m1, P_m2, dP_tie = sol.y[1], sol.y[4], sol.y[6]

    # Plotting out the Interconnected Power Flow Grid Dynamics
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), sharex=True)

    # Subplot 1: Frequency Deviations
    ax1.plot(sol.t, f1, color='dodgerblue', lw=2.5, label="Area 1 (Low Inertia)")
    ax1.plot(sol.t, f2, color='crimson', lw=2, linestyle='--', label="Area 2 (High Inertia)")
    ax1.axhline(50.0, color='grey', linestyle=':', alpha=0.5)
    ax1.set_ylabel("Frequency (Hz)")
    ax1.set_title("Multi-Area Interconnected Grid: Localized Area 1 Disturbance Dynamics")
    ax1.grid(True)
    ax1.legend()

    # Subplot 2: Dynamic Tie Line Transfers and Governor Action
    ax2.plot(sol.t, dP_tie, color='gold', lw=2.5, label="Tie-Line Power Flow ($\Delta P_{tie}$ Export 1->2)")
    ax2.plot(sol.t, P_m1 - 0.5, color='blue', alpha=0.6, label="Area 1 Delta Mech ($\Delta P_{m1}$)")
    ax2.plot(sol.t, P_m2 - 0.5, color='purple', alpha=0.6, label="Area 2 Delta Mech ($\Delta P_{m2}$)")
    ax2.axhline(0.0, color='black', alpha=0.3)
    ax2.set_ylabel("Power Flows & Variances (p.u.)")
    ax2.set_xlabel("Time (seconds)")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()

def Multiple_Area_Simulation():
    # Area 1: Step disturbance at t=1s PLUS short-circuit fault between t=10s and t=10.5s
    def dist_profile1(t):
        base_load = 0.5
        step_load = 0.25 if t>=1.0 else 0.0
        fault_spike = 0.6 if (10.0<=t<=10.5) else 0.0
        return base_load + step_load + fault_spike

    # Area 2: Peak-hour load step at t=3s
    def dist_profile2(t):
        base_load = 0.5
        peak_step = 0.20 if t>=3.0 else 0.0
        return base_load + peak_step


    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.integrate import solve_ivp
    from backend.physics.governors import multi_area_multi_gen_dual_battery_ode

    params = {
        # --- Area 1: Low-Inertia Renewable Heavy Grid ---
        'H1_A': 1.0, 'T_g1_A': 0.15, 'R1_A': 0.04, 'P_ref1_A': 0.25, 'gamma1_A': 0.5,
        'H1_B': 0.8, 'T_g1_B': 0.20, 'R1_B': 0.05, 'P_ref1_B': 0.25, 'gamma1_B': 0.5,
        'D1': 0.4, 'B1': 20.0, 'K_i1': 1.2,
        'K_virtual1': 12.0, 'E_cap1': 0.5,

        # --- Area 2: High-Inertia Conventional Grid ---
        'H2_A': 3.5, 'T_g2_A': 0.50, 'R2_A': 0.05, 'P_ref2_A': 0.25, 'gamma2_A': 0.5,
        'H2_B': 2.5, 'T_g2_B': 0.60, 'R2_B': 0.06, 'P_ref2_B': 0.25, 'gamma2_B': 0.5,
        'D2': 0.6, 'B2': 35.0, 'K_i2': 0.3,
        'K_virtual2': 8.0, 'E_cap2': 0.5,

        # Transmission Tie-Line & Grid Freq
        'T_12': 2.5,
        'omega_0': 2 * np.pi * 50.0
    }

    # Initial state vector y0:
    # [dw1, Pm1_A, Pm1_B, Pagc1, SoC1, dw2, Pm2_A, Pm2_B, Pagc2, SoC2, dP_tie]
    y0 = [
        0.0, 0.25, 0.25, 0.0, 0.80,  # Area 1 initial states (80% SoC)
        0.0, 0.25, 0.25, 0.0, 0.80,  # Area 2 initial states (80% SoC)
        0.0                          # Initial tie-line power flow deviation
    ]

    t_span = (0.0,30.0)
    t_eval = np.linspace(0,30,3000)

    sol = solve_ivp(
        fun = multi_area_multi_gen_dual_battery_ode,
        t_span = t_span,
        y0 = y0,
        args = (params,dist_profile1,dist_profile2),
        method = "RK45",
        t_eval = t_eval,
        max_step = 0.01
    )

    f1 = 50.0 + (sol.y[0] / (2*np.pi))
    f2 = 50.0 + (sol.y[5] / (2*np.pi))

    P_m1_total = sol.y[1] + sol.y[2]
    P_m2_total = sol.y[6] + sol.y[7]

    SoC1 = sol.y[4]
    SoC2 = sol.y[9]
    dP_tie = sol.y[10]

    # Plotting :
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # Frequencies Plotting :
    ax1.plot(sol.t, f1, color='dodgerblue', lw=2, label="Area 1 Freq (Hz)")
    ax1.plot(sol.t, f2, color='crimson', lw=2, linestyle='--', label="Area 2 Freq (Hz)")
    ax1.axhline(50.0, color='black', linestyle=':', alpha=0.5)
    ax1.set_ylabel("Frequency (Hz)")
    ax1.set_title("Multi-Area Cascade Stress Test: Step Load Shocks + Short-Circuit Fault")
    ax1.grid(True)
    ax1.legend()

    # Power Generation and Tie Line transfer :
    ax2.plot(sol.t, dP_tie, color='gold', lw=2.5, label=r"Tie-Line Flow ($\Delta P_{tie}$ 1$\rightarrow$2)")
    ax2.plot(sol.t, P_m1_total - 0.50, color='blue', alpha=0.7, label=r"Area 1 Mech ($\Delta P_{m1}$)")
    ax2.plot(sol.t, P_m2_total - 0.50, color='purple', alpha=0.7, label=r"Area 2 Mech ($\Delta P_{m2}$)")
    ax2.axhline(0.0, color='black', alpha=0.3)
    ax2.set_ylabel("Power Variances (p.u.)")
    ax2.grid(True)
    ax2.legend()

    # Battery States of Charge 
    ax3.plot(sol.t, SoC1, color='teal', lw=2, label="Area 1 Battery SoC")
    ax3.plot(sol.t, SoC2, color='darkorange', lw=2, linestyle='--', label="Area 2 Battery SoC")
    ax3.set_ylabel("Battery SoC")
    ax3.set_xlabel("Time (seconds)")
    ax3.grid(True)
    ax3.legend()

    plt.tight_layout()
    plt.show()


def exp_mitigation_comparison():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.integrate import solve_ivp
    from backend.physics.governors import multi_area_multi_gen_dual_battery_ode
    
    # 3-Second Sustained Fault Profile
    def dist_profile1(t):
        base_load = 0.5
        step_load = 0.25 if t >= 1.0 else 0.0
        fault_spike = 0.60 if (10.0 <= t <= 13.0) else 0.0  # 3-second fault!
        return base_load + step_load + fault_spike

    def dist_profile2(t):
        base_load = 0.5
        peak_step = 0.20 if t >= 3.0 else 0.0
        return base_load + peak_step

    base_params = {
        'H1_A': 1.0, 'T_g1_A': 0.15, 'R1_A': 0.04, 'P_ref1_A': 0.25, 'gamma1_A': 0.5,
        'H1_B': 0.8, 'T_g1_B': 0.20, 'R1_B': 0.05, 'P_ref1_B': 0.25, 'gamma1_B': 0.5,
        'D1': 0.4, 'B1': 20.0, 'K_i1': 1.2, 'K_virtual1': 12.0, 'E_cap1': 0.5,

        'H2_A': 3.5, 'T_g2_A': 0.50, 'R2_A': 0.05, 'P_ref2_A': 0.25, 'gamma2_A': 0.5,
        'H2_B': 2.5, 'T_g2_B': 0.60, 'R2_B': 0.06, 'P_ref2_B': 0.25, 'gamma2_B': 0.5,
        'D2': 0.6, 'B2': 35.0, 'K_i2': 0.3, 'K_virtual2': 8.0, 'E_cap2': 0.5,

        'T_12': 2.5, 'omega_0': 2 * np.pi * 50.0
    }

    t_span = (0.0, 30.0)
    t_eval = np.linspace(0, 30, 3000)

    # --- CASE 1: Unmitigated Baseline ---
    p1 = base_params.copy()
    y0_1 = [0.0, 0.25, 0.25, 0.0, 0.80, 0.0, 0.25, 0.25, 0.0, 0.80, 0.0]
    sol1 = solve_ivp(multi_area_multi_gen_dual_battery_ode, t_span, y0_1, args=(p1, dist_profile1, dist_profile2), t_eval=t_eval, max_step=0.01)

    # --- CASE 2: Option A (Battery Headroom, SoC = 0.50) ---
    p2 = base_params.copy()
    y0_2 = [0.0, 0.25, 0.25, 0.0, 0.50, 0.0, 0.25, 0.25, 0.0, 0.80, 0.0]
    sol2 = solve_ivp(multi_area_multi_gen_dual_battery_ode, t_span, y0_2, args=(p2, dist_profile1, dist_profile2), t_eval=t_eval, max_step=0.01)

    # --- CASE 3: Option B (Slower AGC, Ki1 = 0.3) ---
    p3 = base_params.copy()
    p3['K_i1'] = 0.3
    y0_3 = [0.0, 0.25, 0.25, 0.0, 0.80, 0.0, 0.25, 0.25, 0.0, 0.80, 0.0]
    sol3 = solve_ivp(multi_area_multi_gen_dual_battery_ode, t_span, y0_3, args=(p3, dist_profile1, dist_profile2), t_eval=t_eval, max_step=0.01)

    # Extract Frequencies & SoCs
    f1_c1 = 50.0 + (sol1.y[0] / (2 * np.pi))
    f1_c2 = 50.0 + (sol2.y[0] / (2 * np.pi))
    f1_c3 = 50.0 + (sol3.y[0] / (2 * np.pi))

    soc1_c1 = sol1.y[4]
    soc1_c2 = sol2.y[4]
    soc1_c3 = sol3.y[4]

    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Subplot 1: Frequency Comparison
    ax1.plot(sol1.t, f1_c1, color='crimson', lw=2, label="Baseline (SoC=0.8, Ki1=1.2)")
    ax1.plot(sol2.t, f1_c2, color='forestgreen', lw=2, label="Option A: Headroom (SoC=0.5, Ki1=1.2)")
    ax1.plot(sol3.t, f1_c3, color='dodgerblue', lw=2, linestyle='--', label="Option B: AGC Damping (SoC=0.8, Ki1=0.3)")
    ax1.axhline(50.0, color='black', linestyle=':', alpha=0.5)
    ax1.axhline(50.5, color='red', linestyle='--', alpha=0.7, label="Trip Limit (50.5 Hz)")
    ax1.set_ylabel("Area 1 Frequency (Hz)")
    ax1.set_title("Mitigation Strategy Comparison: 3-Second Sustained Fault Response")
    ax1.grid(True)
    ax1.legend()

    # Subplot 2: SoC Comparison
    ax2.plot(sol1.t, soc1_c1, color='crimson', lw=2, label="Baseline SoC")
    ax2.plot(sol2.t, soc1_c2, color='forestgreen', lw=2, label="Option A SoC")
    ax2.plot(sol3.t, soc1_c3, color='dodgerblue', lw=2, linestyle='--', label="Option B SoC")
    ax2.set_ylabel("Area 1 Battery SoC")
    ax2.set_xlabel("Time (seconds)")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()

def model_1_exp_1():
    import numpy as np
    from scipy.integrate import solve_ivp
    from backend.physics.governors import Model_1
    import matplotlib.pyplot as plt

    # 1. Define Disturbances
    def disturbance_func1(t):
        base_load = 0.8
        fault_spike = 0.60 if (10.0 <= t <= 10.5) else 0.0  
        return base_load +  fault_spike

    def disturbance_func2(t):
        base_load = 0.8
        peak_step = 0.20 if t >= 3.0 else 0.0
        return base_load + peak_step
        

    # 2. System Parameters (with deliberate tight physical bounds)
    params = {
        "omega_0": 2 * np.pi * 50,
        
        # Area 1 Generators (Inertia, Governor Time, Droop, AGC participation)
        "H1_A": 4.0, "T_g1_A": 0.2, "R1_A": 0.05, "gamma1_A": 0.5, "P_ref1_A": 0.5,
        "H1_B": 3.0, "T_g1_B": 0.3, "R1_B": 0.04, "gamma1_B": 0.5, "P_ref1_B": 0.3,
        
        # Generator 1 Limits (Tight P_max to force saturation!)
        "ramp_up1_A": 0.05, "ramp_down1_A": 0.05, "P_max1_A": 0.65, "P_min1_A": 0.0,
        "ramp_up1_B": 0.05, "ramp_down1_B": 0.05, "P_max1_B": 0.40, "P_min1_B": 0.0,
        
        # Area 2 Generators
        "H2_A": 4.0, "T_g2_A": 0.2, "R2_A": 0.05, "gamma2_A": 0.5, "P_ref2_A": 0.5,
        "H2_B": 3.0, "T_g2_B": 0.3, "R2_B": 0.04, "gamma2_B": 0.5, "P_ref2_B": 0.3,
        
        # Generator 2 Limits
        "ramp_up2_A": 0.05, "ramp_down2_A": 0.05, "P_max2_A": 0.80, "P_min2_A": 0.0,
        "ramp_up2_B": 0.05, "ramp_down2_B": 0.05, "P_max2_B": 0.60, "P_min2_B": 0.0,
        
        # Damping & AGC Gains
        "D1": 1.0, "D2": 1.0,
        "B1": 20.0, "B2": 20.0,
        "K_i1": 0.15, "K_i2": 0.15,
        
        # Batteries (FFR Gain & Capacity)
        "K_virtual1": 12.0, "E_cap1": 2.0,
        "K_virtual2": 12.0, "E_cap2": 2.0,
        
        # Tie-Line Parameter & Capacity Cap (Tight limit at 0.10 p.u.)
        "T_12": 0.25,
        "P_tie_max": 0.10,
        "K_emergency":15
    }   

    # 3. Initial State Vector [dw1, P_m1_A, P_m1_B, P_agc1, SoC1, dw2, P_m2_A, P_m2_B, P_agc2, SoC2, dP_tie]
    y0 = [
        0.0,                    # dw1 (rad/s deviation)
        params["P_ref1_A"],     # P_m1_A
        params["P_ref1_B"],     # P_m1_B
        0.0,                    # P_agc1
        0.5,                    # SoC1 (50% charge)
        0.0,                    # dw2
        params["P_ref2_A"],     # P_m2_A
        params["P_ref2_B"],     # P_m2_B
        0.0,                    # P_agc2
        0.5,                    # SoC2 (50% charge)
        0.0                     # dP_tie
    ]

    # 4. Run Simulation
    t_span = (0.0, 40.0)
    t_eval = np.linspace(t_span[0], t_span[1], 1000)

    sol = solve_ivp(
        fun=lambda t, y: Model_1(t, y, params, disturbance_func1, disturbance_func2),
        t_span=t_span,
        y0=y0,
        t_eval=t_eval,
        method='RK45'
    )

    # Re-calculate Battery FFR Power for plotting
    P_ffr1_hist = []
    for i in range(len(sol.t)):
        dw1 = sol.y[0][i]
        dw1_pu = dw1 / params["omega_0"]
        P_m1_A = sol.y[1][i]
        P_m1_B = sol.y[2][i]
        dP_tie = sol.y[10][i]
        P_e1 = disturbance_func1(sol.t[i])
        
        H1_total = params["H1_A"] + params["H1_B"]
        swing_term_1 = (P_m1_A + P_m1_B - dP_tie) - P_e1 - (params["D1"] * dw1_pu)
        
        ddw1_dt = (params["omega_0"] * swing_term_1) / (2 * H1_total + params["K_virtual1"])
        rocof1_pu = ddw1_dt / params["omega_0"]
        p_ffr = -params["K_virtual1"] * rocof1_pu
        P_ffr1_hist.append(p_ffr)

    # 5. Plot the Results 
    fig, axs = plt.subplots(4, 1, figsize=(11, 12), sharex=True)

    # Plot 1: Frequencies (Hz) & Limits
    f1 = 50.0 + (sol.y[0] / (2 * np.pi))
    f2 = 50.0 + (sol.y[5] / (2 * np.pi))
    axs[0].plot(sol.t, f1, label="Area 1 Frequency (Hz)", color="crimson", linewidth=2)
    axs[0].plot(sol.t, f2, label="Area 2 Frequency (Hz)", color="navy", linewidth=2, linestyle="--")
    axs[0].axhline(50.0, color="black", linestyle="-", alpha=0.6, label="Nominal (50.0 Hz)")
    axs[0].axhline(49.00, color="red", linestyle="-.", linewidth=1.5, label="Lower Nadir Limit (49.0 Hz)")
    axs[0].axhline(51.00, color="red", linestyle="-.", linewidth=1.5, label="Upper Limit (51.0 Hz)")
    axs[0].set_ylabel("Frequency [Hz]")
    axs[0].set_title("Grid Frequency Response & Emergency Boundaries")
    axs[0].legend(loc="upper right")
    axs[0].grid(True)

    # Plot 2: Generator Mechanical Power Output & Limits
    axs[1].plot(sol.t, sol.y[1], label="P_m1_A (Area 1)", color="darkred")
    axs[1].plot(sol.t, sol.y[2], label="P_m1_B (Area 1)", color="red")
    axs[1].axhline(params["P_max1_A"], color="darkred", linestyle=":", label="P_max1_A Limit")
    axs[1].axhline(params["P_max1_B"], color="red", linestyle=":", label="P_max1_B Limit")
    axs[1].plot(sol.t, sol.y[6], label="P_m2_A (Area 2)", color="darkblue", linestyle="--")
    axs[1].plot(sol.t, sol.y[7], label="P_m2_B (Area 2)", color="blue", linestyle="--")
    axs[1].set_ylabel("Power [p.u.]")
    axs[1].set_title("Generator Output & Capacity Limits")
    axs[1].legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    axs[1].grid(True)

    # Plot 3: Tie-Line Interconnection Flow
    axs[2].plot(sol.t, sol.y[10], label="Tie-Line Flow (dP_tie)", color="purple", linewidth=2)
    axs[2].axhline(params["P_tie_max"], color="purple", linestyle=":", label="+P_tie_max Limit")
    axs[2].axhline(-params["P_tie_max"], color="purple", linestyle=":", label="-P_tie_max Limit")
    axs[2].set_ylabel("Power [p.u.]")
    axs[2].set_title("Inter-Area Tie-Line Power Flow & Thermal Limits")
    axs[2].legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    axs[2].grid(True)

    # Plot 4: Battery FFR Power & State of Charge (SoC)
    ax4_soc = axs[3].twinx()  # Twin axis so SoC (0-1) and FFR Power share the plot smoothly!
    
    line1 = axs[3].plot(sol.t, P_ffr1_hist, label="P_ffr1 (Area 1 Power)", color="darkgreen", linewidth=2)
    line2 = ax4_soc.plot(sol.t, sol.y[4], label="SoC Area 1", color="limegreen", linestyle="--")
    
    # Combine legend from twin axes
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    axs[3].legend(lines, labels, loc="upper left", bbox_to_anchor=(1.08, 1))

    axs[3].set_ylabel("FFR Power [p.u.]", color="darkgreen")
    ax4_soc.set_ylabel("SoC [0.0 - 1.0]", color="limegreen")
    axs[3].set_xlabel("Time [seconds]")
    axs[3].set_title("Fast Frequency Response (FFR) & Battery State of Charge")
    axs[3].grid(True)

    plt.tight_layout()
    plt.show()


def engine_experiment():
    import numpy as np
    from scipy.integrate import solve_ivp
    from backend.physics.engine import Stability_Atlas_Engine
    import matplotlib.pyplot as plt

    # 1. Define Disturbances
    def disturbance_func1(t):
        base_load = 0.8
        fault_spike = 0.60 if (10.0 <= t <= 10.5) else 0.0  
        return base_load + fault_spike

    def disturbance_func2(t):
        base_load = 0.8
        peak_step = 0.20 if t >= 3.0 else 0.0
        return base_load + peak_step

    # 2. System Parameters (with deliberate tight physical bounds)
    params = {
        "omega_0": 2 * np.pi * 50,
        
        # Area 1 Generators (Inertia, Governor Time, Droop, AGC participation)
        "H1_A": 4.0, "T_g1_A": 0.2, "R1_A": 0.05, "gamma1_A": 0.5, "P_ref1_A": 0.5,
        "H1_B": 3.0, "T_g1_B": 0.3, "R1_B": 0.04, "gamma1_B": 0.5, "P_ref1_B": 0.3,
        
        # Generator 1 Limits (Tight P_max to force saturation!)
        "ramp_up1_A": 0.05, "ramp_down1_A": 0.05, "P_max1_A": 0.65, "P_min1_A": 0.0,
        "ramp_up1_B": 0.05, "ramp_down1_B": 0.05, "P_max1_B": 0.40, "P_min1_B": 0.0,
        
        # Area 2 Generators
        "H2_A": 4.0, "T_g2_A": 0.2, "R2_A": 0.05, "gamma2_A": 0.5, "P_ref2_A": 0.5,
        "H2_B": 3.0, "T_g2_B": 0.3, "R2_B": 0.04, "gamma2_B": 0.5, "P_ref2_B": 0.3,
        
        # Generator 2 Limits
        "ramp_up2_A": 0.05, "ramp_down2_A": 0.05, "P_max2_A": 0.80, "P_min2_A": 0.0,
        "ramp_up2_B": 0.05, "ramp_down2_B": 0.05, "P_max2_B": 0.60, "P_min2_B": 0.0,
        
        # Damping & AGC Gains
        "D1": 1.0, "D2": 1.0,
        "B1": 20.0, "B2": 20.0,
        "K_i1": 0.15, "K_i2": 0.15,
        
        # Batteries (FFR Gain & Capacity)
        "K_virtual1": 12.0, "E_cap1": 2.0,
        "K_virtual2": 12.0, "E_cap2": 2.0,
        
        # Tie-Line Parameter & Capacity Cap (Tight limit at 0.10 p.u.)
        "T_12": 0.25,
        "P_tie_max": 0.10,
        "K_emergency": 15
    }   

    # 3. Initial State Vector [dw1, P_m1_A, P_m1_B, P_agc1, SoC1, dw2, P_m2_A, P_m2_B, P_agc2, SoC2, dP_tie]
    y0 = [
        0.0,                    # dw1 (rad/s deviation)
        params["P_ref1_A"],     # P_m1_A
        params["P_ref1_B"],     # P_m1_B
        0.0,                    # P_agc1
        0.5,                    # SoC1 (50% charge)
        0.0,                    # dw2
        params["P_ref2_A"],     # P_m2_A
        params["P_ref2_B"],     # P_m2_B
        0.0,                    # P_agc2
        0.5,                    # SoC2 (50% charge)
        0.0                     # dP_tie
    ]

    # 4. Run Simulation
    t_span = (0.0, 40.0)
    t_eval = np.linspace(t_span[0], t_span[1], 1000)

    sol = solve_ivp(
        fun=lambda t, y: Stability_Atlas_Engine(t, y, params, disturbance_func1, disturbance_func2),
        t_span=t_span,
        y0=y0,
        t_eval=t_eval,
        method='RK45'
    )

    # Re-calculate Battery FFR Power for both Area 1 and Area 2
    P_ffr1_hist = []
    P_ffr2_hist = []

    for i in range(len(sol.t)):
        # --- Area 1 FFR ---
        dw1 = sol.y[0][i]
        dw1_pu = dw1 / params["omega_0"]
        P_m1_A = sol.y[1][i]
        P_m1_B = sol.y[2][i]
        SoC1 = sol.y[4][i]
        dP_tie = sol.y[10][i]
        P_e1 = disturbance_func1(sol.t[i])
        
        H1_total = params["H1_A"] + params["H1_B"]
        swing_term_1 = (P_m1_A + P_m1_B - dP_tie) - P_e1 - (params["D1"] * dw1_pu)
        
        if (SoC1 > 0.001 and swing_term_1 < 0.0) or (SoC1 < 0.999 and swing_term_1 > 0.0):
            ddw1_dt = (params["omega_0"] * swing_term_1) / (2 * H1_total + params["K_virtual1"])
            rocof1_pu = ddw1_dt / params["omega_0"]
            p_ffr1 = -params["K_virtual1"] * rocof1_pu
        else:
            p_ffr1 = 0.0
        P_ffr1_hist.append(p_ffr1)

        # --- Area 2 FFR ---
        dw2 = sol.y[5][i]
        dw2_pu = dw2 / params["omega_0"]
        P_m2_A = sol.y[6][i]
        P_m2_B = sol.y[7][i]
        SoC2 = sol.y[9][i]
        P_e2 = disturbance_func2(sol.t[i])

        H2_total = params["H2_A"] + params["H2_B"]
        swing_term_2 = (P_m2_A + P_m2_B + dP_tie) - P_e2 - (params["D2"] * dw2_pu)

        if (SoC2 > 0.001 and swing_term_2 < 0.0) or (SoC2 < 0.999 and swing_term_2 > 0.0):
            ddw2_dt = (params["omega_0"] * swing_term_2) / (2 * H2_total + params["K_virtual2"])
            rocof2_pu = ddw2_dt / params["omega_0"]
            p_ffr2 = -params["K_virtual2"] * rocof2_pu
        else:
            p_ffr2 = 0.0
        P_ffr2_hist.append(p_ffr2)

    # 5. Plot the Results 
    fig, axs = plt.subplots(4, 1, figsize=(11, 12), sharex=True)

    # Plot 1: Frequencies (Hz) & Limits
    f1 = 50.0 + (sol.y[0] / (2 * np.pi))
    f2 = 50.0 + (sol.y[5] / (2 * np.pi))
    axs[0].plot(sol.t, f1, label="Area 1 Frequency (Hz)", color="crimson", linewidth=2)
    axs[0].plot(sol.t, f2, label="Area 2 Frequency (Hz)", color="navy", linewidth=2, linestyle="--")
    axs[0].axhline(50.0, color="black", linestyle="-", alpha=0.6, label="Nominal (50.0 Hz)")
    axs[0].axhline(49.00, color="red", linestyle="-.", linewidth=1.5, label="Lower Nadir Limit (49.0 Hz)")
    axs[0].axhline(51.00, color="red", linestyle="-.", linewidth=1.5, label="Upper Limit (51.0 Hz)")
    axs[0].set_ylabel("Frequency [Hz]")
    axs[0].set_title("Grid Frequency Response & Emergency Boundaries")
    axs[0].legend(loc="upper right")
    axs[0].grid(True)

    # Plot 2: Generator Mechanical Power Output & Limits
    axs[1].plot(sol.t, sol.y[1], label="P_m1_A (Area 1)", color="darkred")
    axs[1].plot(sol.t, sol.y[2], label="P_m1_B (Area 1)", color="red")
    axs[1].axhline(params["P_max1_A"], color="darkred", linestyle=":", label="P_max1_A Limit")
    axs[1].axhline(params["P_max1_B"], color="red", linestyle=":", label="P_max1_B Limit")
    axs[1].plot(sol.t, sol.y[6], label="P_m2_A (Area 2)", color="darkblue", linestyle="--")
    axs[1].plot(sol.t, sol.y[7], label="P_m2_B (Area 2)", color="blue", linestyle="--")
    axs[1].set_ylabel("Power [p.u.]")
    axs[1].set_title("Generator Output & Capacity Limits")
    axs[1].legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    axs[1].grid(True)

    # Plot 3: Tie-Line Interconnection Flow
    axs[2].plot(sol.t, sol.y[10], label="Tie-Line Flow (dP_tie)", color="purple", linewidth=2)
    axs[2].axhline(params["P_tie_max"], color="purple", linestyle=":", label="+P_tie_max Limit")
    axs[2].axhline(-params["P_tie_max"], color="purple", linestyle=":", label="-P_tie_max Limit")
    axs[2].set_ylabel("Power [p.u.]")
    axs[2].set_title("Inter-Area Tie-Line Power Flow & Thermal Limits")
    axs[2].legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    axs[2].grid(True)

    # Plot 4: Battery FFR Power & State of Charge (SoC) for BOTH Areas
    ax4_soc = axs[3].twinx()  # Twin axis so SoC (0-1) and FFR Power share the plot smoothly!
    
    # FFR Active Power Outputs
    line1 = axs[3].plot(sol.t, P_ffr1_hist, label="P_ffr1 (Area 1 Power)", color="forestgreen", linewidth=2)
    line2 = axs[3].plot(sol.t, P_ffr2_hist, label="P_ffr2 (Area 2 Power)", color="teal", linewidth=2, linestyle="--")
    
    # State-of-Charge Curves (Darker, thicker lines for high visibility)
    line3 = ax4_soc.plot(sol.t, sol.y[4], label="SoC Area 1", color="darkgreen", linestyle=":", linewidth=2.2)
    line4 = ax4_soc.plot(sol.t, sol.y[9], label="SoC Area 2", color="darkcyan", linestyle=":", linewidth=2.2)
    
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


engine_experiment()