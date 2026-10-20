import numpy as np
from scipy.integrate import solve_ivp

def governed_system_ode(t, y, H, D, disturbance_func, T_g, R, P_ref, K_i, omega_0=2 * np.pi * 50):
    """
    Defines the coupled ODEs for both the Swing Equation and the Governor.
    Here, Electrical Load (Pe) is given by disturbance_func.
    
    State Vector:
    -------------
    y[0] : delta_omega (rad/s) -> Frequency deviation
    y[1] : P_m (p.u.)          -> Dynamic mechanical power
    y[2] : P_agc (p.u.)        -> Integral AGC supplementary power

    """
    delta_omega = y[0]
    P_m = y[1]
    P_agc = y[2]

    P_e = disturbance_func(t)
        
    # Governor Equation: d(P_m)/dt and Swing Equation: d(delta_omega)/dt
    # Note: R is often given in per-unit of frequency. We divide delta_omega by omega_0 
    # To convert the deviation into per-unit before applying the droop R.
    # d P_agc/dt is the automatic generation controller for removing offset error


    delta_omega_pu = delta_omega / omega_0

    d_delta_omega_dt = (omega_0 / (2 * H)) * (P_m - P_e - (D * delta_omega_pu)) # Swing Equation

    d_Pm_dt = (1.0 / T_g) * ((P_ref + P_agc) - (delta_omega_pu / R) - P_m) # Governor Equation

    d_Pagc_dt = - K_i * delta_omega_pu # Automatic Generation Controller Equation
    
    return [d_delta_omega_dt, d_Pm_dt, d_Pagc_dt]

def simulate_governed_response(t_span, y0, H, D, disturbance_func, T_g, R, P_ref, K_i = 0.0, omega_0=2 * np.pi * 50, t_eval=None):
    """
    Solves the coupled governor-swing equations over a specified time span.
    """
    sol = solve_ivp(
        fun=governed_system_ode,
        t_span=t_span,
        y0=y0, # Expecting [delta_omega_init, P_m_init]
        args=(H, D, disturbance_func, T_g, R, P_ref,K_i, omega_0),
        method='RK45',
        t_eval=t_eval,
        max_step = 0.05
    )
    return sol


def multimachine_system_ode(t, y, H1, H2, D1, D2, T_g1, T_g2, R1, R2, P_ref1, P_ref2, gamma1, gamma2, K_i, disturbance_func, omega_0=2 * np.pi * 50):
    """
    4-State Coupled ODE system tracking a Multi-Machine Power Grid.
    
    State Vector:
    -------------
    y[0] : delta_omega (rad/s) -> Common grid frequency deviation
    y[1] : P_m1 (p.u.)         -> Mechanical power from Generator 1
    y[2] : P_m2 (p.u.)         -> Mechanical power from Generator 2
    y[3] : P_agc (p.u.)        -> Centralized AGC integral reference adjustment

    """

    delta_omega = y[0]

    P_m1 = y[1]
    P_m2 = y[2]
    P_agc = y[3]

    P_e = disturbance_func(t)

    delta_w_pu = delta_omega / omega_0

    H_total = H1 + H2
    D_total = D1 + D2
    P_m_total = P_m1 + P_m2

    # Combined Swing Equation :
    d_delta_omega_dt = (omega_0 / (2*H_total)) * (P_m_total - P_e - (D_total * delta_w_pu)) 

    # Governor Equation for Generator 1
    # Gamma 1 Determines how much amoung of P_agc goes to Generator 1
    d_Pm1_dt = (1.0 / T_g1) * ((P_ref1 + gamma1*P_agc) - (delta_w_pu / R1) - P_m1)

    # Governor Equation for Generator 2
    # Gamma 2 Determines how much amoung of P_agc goes to Generator 2
    d_Pm2_dt = (1.0 / T_g2) * ((P_ref2 + gamma2*P_agc) - (delta_w_pu / R2) - P_m2)

    d_Pagc_dt = - K_i * delta_w_pu

    return [d_delta_omega_dt, d_Pm1_dt, d_Pm2_dt, d_Pagc_dt]

def simulate_multimachine_response(t_span, y0, params, disturbance_func, t_eval=None):

    sol = solve_ivp(
        fun = multimachine_system_ode,
        t_span= t_span,
        y0 = y0, # [ delta_omega, P_m1, P_m2, P_agc]
        args=(
            params['H1'], params['H2'], params['D1'], params['D2'],
            params['T_g1'], params['T_g2'], params['R1'], params['R2'],
            params['P_ref1'], params['P_ref2'], params['gamma1'], params['gamma2'],
            params['K_i'], disturbance_func, params.get('omega_0', 2 * np.pi * 50)
        ),
        method = "RK45",
        t_eval=t_eval,
        max_step = 0.05

    )

    return sol


def low_inertia_ffr_system_ode(t, y, H1, H2, D1, D2, T_g1, T_g2, R1, R2, P_ref1, P_ref2, gamma1, gamma2, K_i, K_virtual, T_battery, disturbance_func, omega_0=2 * np.pi * 50):
    """
    5-State Coupled ODE system tracking a Low-Inertia Grid with Virtual Inertia Battery Support.
    
    State Vector:
    -------------
    y[0] : delta_omega (rad/s) -> Common grid frequency deviation
    y[1] : P_m1 (p.u.)         -> Mechanical power from Generator 1
    y[2] : P_m2 (p.u.)         -> Mechanical power from Generator 2
    y[3] : P_agc (p.u.)        -> Centralized AGC secondary reference adjustment
    y[4] : P_ffr (p.u.)        -> Active power injection from Virtual Inertia Battery Inverter
    
    """

    delta_omega = y[0]
    P_m1 = y[1]
    P_m2 = y[2]
    P_agc = y[3]
    P_ffr = y[4]

    P_e = disturbance_func(t)
    delta_w_pu = delta_omega / omega_0

    H_total = H1 + H2
    D_total = D1 + D2

    P_generation_total = P_m1 + P_m2 + P_ffr

    d_delta_omega_dt = (omega_0/(2*H_total)) * (P_generation_total - P_e - (D_total * delta_w_pu))
    d_Pm1_dt = (1.0/T_g1) * ((P_ref1 + (gamma1*P_agc)) - (delta_w_pu/R1) - P_m1)
    d_Pm2_dt = (1.0/T_g2) * ((P_ref2 + (gamma2*P_agc)) - (delta_w_pu/R2) - P_m2)
    d_Pagc_dt = - K_i * delta_w_pu

    rocof_pu = d_delta_omega_dt / omega_0
    P_ffr_target = - K_virtual * rocof_pu
    d_Pffr_dt = (1.0 / T_battery) * (P_ffr_target - P_ffr)

    return [d_delta_omega_dt, d_Pm1_dt, d_Pm2_dt, d_Pagc_dt, d_Pffr_dt]

def simulate_low_inertia_ffr_response(t_span, y0, params, disturbance_func, t_eval=None):
    """
    Solves the 5-state low-inertia FFR system using explicit keyword passing.
    
    """

    sol = solve_ivp(
        fun = low_inertia_ffr_system_ode,
        t_span=t_span,
        y0=y0,
        args=(
            params['H1'], params['H2'], params['D1'], params['D2'],
            params['T_g1'], params['T_g2'], params['R1'], params['R2'],
            params['P_ref1'], params['P_ref2'], params['gamma1'], params['gamma2'],
            params['K_i'], params['K_virtual'], params['T_battery'],
            disturbance_func, params.get('omega_0', 2 * np.pi * 50)
        ),
        method = "RK45",
        t_eval = t_eval,
        max_step = 0.01
    )

    return sol


def low_inertia_soc_system_ode(t, y, H1, H2, D1, D2, T_g1, T_g2, R1, R2, P_ref1, P_ref2, gamma1, gamma2, K_i, K_virtual, T_battery, E_cap, disturbance_func, omega_0=2 * np.pi * 50):
    """
    6-State Coupled ODE system tracking a Low-Inertia Grid with a 
    State-of-Charge (SoC) constrained Virtual Inertia Battery.
    
    State Vector:
    -------------
    y[0] : delta_omega (rad/s) -> Common grid frequency deviation
    y[1] : P_m1 (p.u.)         -> Mechanical power from Generator 1
    y[2] : P_m2 (p.u.)         -> Mechanical power from Generator 2
    y[3] : P_agc (p.u.)        -> Centralized AGC secondary reference adjustment
    y[4] : P_ffr (p.u.)        -> Active power injection from Battery Inverter
    y[5] : SoC (dimensionless) -> Battery State of Charge [0.0 to 1.0]

    """

    delta_omega = y[0]
    P_m1 = y[1]
    P_m2 = y[2]
    P_agc = y[3]

    SoC = max(0.0,min(1.0,y[5]))
    raw_P_ffr = y[4]
    if SoC<=0.0:
        P_ffr = min(0.0,raw_P_ffr)
    elif SoC>=1.0:
        P_ffr  = max(0.0,y[4])
    else:
        P_ffr = raw_P_ffr

    P_e = disturbance_func(t)
    delta_w_pu = delta_omega / omega_0

    # 1. Physical Saturation Constraints:
    # If the battery is empty (SoC <= 0), it cannot discharge (P_ffr cannot be positive)
    # If the battery is completely full (SoC >= 1.0), it cannot charge (P_ffr cannot be negative)

    rocof_pu = (omega_0/(2*(H1+H2))) * ((P_m1 + P_m2 + P_ffr) - P_e - ((D1 + D2)* delta_w_pu)) / omega_0
    P_ffr_target = max(0.0, -K_virtual * rocof_pu)

    if SoC <= 0.001 and P_ffr_target > 0.0 :
        P_ffr_target= 0.0 # Force the Battery ejection power to be zero
    elif SoC >= 0.999 and P_ffr_target < 0.0 :
        P_ffr_target = 0.0

    H_total = H1 + H2
    D_total = D1 + D2
    P_generation_total = P_m1 + P_m2 + P_ffr

    d_delta_omega_dt = (omega_0/(2*H_total)) * (P_generation_total - P_e - (D_total * delta_w_pu))
    d_Pm1_dt = (1.0/T_g1) * ((P_ref1 + (gamma1*P_agc)) - (delta_w_pu/R1) - P_m1)
    d_Pm2_dt = (1.0/T_g2) * ((P_ref2 + (gamma2*P_agc)) - (delta_w_pu/R2) - P_m2)
    d_Pagc_dt = -K_i * delta_w_pu
    d_Pffr_dt = (1.0/T_battery) * (P_ffr_target - P_ffr)

    # State of Charge Integration
    # If the battery output is very close to zero and empty, stop draining
    if SoC <=0.0:
        if raw_P_ffr >= 0.0:
            d_Pffr_dt = min(0.0,d_Pffr_dt)
            y[4] = 0.0
            P_ffr = 0.0
    
    d_SoC_dt = -P_ffr / E_cap
    if SoC <= 0.0 and d_SoC_dt < 0.0:
        d_SoC_dt = 0.0
    elif SoC >= 1.0 and d_SoC_dt >0.0:
        d_SoC_dt = 0.0
        

    return [d_delta_omega_dt, d_Pm1_dt, d_Pm2_dt, d_Pagc_dt, d_Pffr_dt, d_SoC_dt]

 
def simulate_low_inertia_soc_response(t_span, y0, params, disturbance_func, t_eval=None):
    """
    Solves the 6-state low-inertia SoC system using explicit keyword passing.
    """
    sol = solve_ivp(
        fun=low_inertia_soc_system_ode,
        t_span=t_span,
        y0=y0, # [delta_omega, P_m1, P_m2, P_agc, P_ffr, SoC]
        args=(
            params['H1'], params['H2'], params['D1'], params['D2'],
            params['T_g1'], params['T_g2'], params['R1'], params['R2'],
            params['P_ref1'], params['P_ref2'], params['gamma1'], params['gamma2'],
            params['K_i'], params['K_virtual'], params['T_battery'], params['E_cap'],
            disturbance_func, params.get('omega_0', 2 * np.pi * 50)
        ),
        method='RK45',
        t_eval=t_eval,
        max_step=0.01
    )
    
    return sol








def multi_area_tie_system_ode(t, y, params, disturbance_func1, disturbance_func2):
    """
    8-State Interconnected Two-Area Power System Simulator.
    
    State Vector Mapping:
    ---------------------
    y[0] : delta_omega1 (rad/s) -> Area 1 frequency deviation
    y[1] : P_m1 (p.u.)          -> Area 1 governor mechanical output
    y[2] : P_agc1 (p.u.)         -> Area 1 secondary AGC integral state
    y[3] : delta_omega2 (rad/s) -> Area 2 frequency deviation
    y[4] : P_m2 (p.u.)          -> Area 2 governor mechanical output
    y[5] : P_agc2 (p.u.)         -> Area 2 secondary AGC integral state
    y[6] : delta_P_tie (p.u.)   -> Dynamic Tie-Line power flow from Area 1 to Area 2
    y[7] : SoC1 (dimensionless)  -> Area 1 Battery Storage State of Charge
    
    """

    omega_0 = params.get("omega_0",2*np.pi*50)
    
    dw1, P_m1, P_agc1 = y[0], y[1], y[2] # Area 1
    dw2, P_m2, P_agc2 = y[3], y[4], y[5] # Area 2

    dw1_pu = dw1 / omega_0
    dw2_pu = dw2 / omega_0

    P_e1 = disturbance_func1(t)
    P_e2 = disturbance_func2(t)
    dP_tie = y[6]
    SoC1 = max(0.0, min(1.0,y[7])) # Battery Capacity for Area 1

    # Net generation in Area 1 includes battery, but loses power exporting down tie-line
    swing_term_1 = (P_m1- dP_tie) - P_e1 - (params["D1"] * dw1_pu)
    P_ffr1 = 0.0
    
    # Virtual intertia triggers only if grid frequency is falling and battery has energy
    if SoC1 > 0.001 and swing_term_1 < 0.0:
        ddw1_dt = (omega_0 * swing_term_1) / (2*params["H1"] + params["K_virtual1"])
        rocof1_pu = ddw1_dt / omega_0
        P_ffr1 = -params["K_virtual1"] * rocof1_pu

        # We must update the acceleration to account for the battery's active support
        # ddw1_dt = (omega_0 / (2*params["H1"])) * (swing_term_1 + P_ffr1) BUT REDUNDANT

    else:
        P_ffr1 = 0.0
        ddw1_dt = (omega_0 / (2*params["H1"]))  * swing_term_1


    # Net generation in Area 2 receives power imported up from the tie-line (+dP_tie)
    swing_term_2 = P_m2  + dP_tie - P_e2 - (params["D2"]*dw2_pu)
    ddw2_dt = (omega_0 / (2*params["H2"])) * swing_term_2 # Area 2 swing equation

    # Governor Equations :
    dP_m1_dt = (1.0 / params['T_g1']) * ((params['P_ref1'] + (params['gamma1'] * P_agc1)) - (dw1_pu / params['R1']) - P_m1)
    dP_m2_dt = (1.0 / params['T_g2']) * ((params['P_ref2'] + (params['gamma2'] * P_agc2)) - (dw2_pu / params['R2']) - P_m2)

    # Interconnected Area Control Error (ACE) Equations
    ACE1 = (params["B1"] * dw1_pu) + dP_tie # Area 1 Exports 
    ACE2 = (params["B2"] * dw2_pu) - dP_tie # Area 2 Imports

    dP_agc1_dt = - params["K_i1"] * ACE1
    dP_agc2_dt = - params["K_i2"] * ACE2

    ddP_tie_dt = params["T_12"] * (dw1_pu - dw2_pu)

    d_SoC1_dt = - P_ffr1 / params["E_cap1"]
    if SoC1 <= 0.0 and d_SoC1_dt < 0.0:
        d_SoC1_dt = 0.0

    return [ddw1_dt, dP_m1_dt, dP_agc1_dt, ddw2_dt, dP_m2_dt, dP_agc2_dt, ddP_tie_dt, d_SoC1_dt]





def multi_area_multi_gen_dual_battery_ode(t, y, params, disturbance_func1, disturbance_func2):
    """
    11-State Interconnected Two-Area Multi-Generator Grid Engine.
    
    Features:
    - 2 Generators per Area (4 total generators)
    - Bidirectional Batteries in both Areas (Charge & Discharge)
    - Tie-Line Power Flow Interconnection
    - Un-looped explicit FFR math for both battery systems

    """

    omega_0 = params.get("omega_0",2*np.pi * 50)

    # Area 1 state variables :
    dw1, P_m1_A, P_m1_B, P_agc1, SoC1 = y[0], y[1], y[2], y[3], max(0.0, min(1.0, y[4]))

    # Area 2 state variables :
    dw2, P_m2_A, P_m2_B, P_agc2, SoC2 = y[5], y[6], y[7], y[8], max(0.0, min(1.0, y[9]))

    dP_tie = y[10]

    dw1_pu = dw1 / omega_0
    dw2_pu = dw2 / omega_0

    P_e1 = disturbance_func1(t)
    P_e2 = disturbance_func2(t)

    H1_total = params["H1_A"] + params["H1_B"]
    H2_total = params["H2_A"] + params["H2_B"]

    swing_term_1 = (P_m1_A + P_m1_B - dP_tie) - P_e1 - (params["D1"] * dw1_pu)
    P_ffr1 = 0.0

    # Bidirectional FFR Trigger logic:
    # If falling frequency (swing_term_1 < 0) & SoC1 > 0 -> Discharge (P_ffr1 > 0)
    # If rising frequency  (swing_term_1 > 0) & SoC1 < 1 -> Charge    (P_ffr1 < 0)
    if (SoC1>0.001 and swing_term_1<0.00) or (SoC1<0.999 and swing_term_1 > 0.0):
        ddw1_dt = (omega_0 * swing_term_1) / (2*H1_total + params["K_virtual1"])
        rocof1_pu = ddw1_dt / omega_0
        P_ffr1 = -params["K_virtual1"] * rocof1_pu
        ddw1_dt = (omega_0 / (2*H1_total)) * (swing_term_1 + P_ffr1)

    else:
        P_ffr1 = 0.0
        ddw1_dt = (omega_0 / (2*H1_total)) * swing_term_1

    swing_term_2 = (P_m2_A + P_m2_B + dP_tie) - P_e2 - (params["D2"] * dw2_pu)
    P_ffr2 = 0.0

    if (SoC2>0.001 and swing_term_2<0.00) or (SoC2<0.999 and swing_term_2 > 0.0):
        ddw2_dt = (omega_0*swing_term_2) / (2*H2_total + params["K_virtual2"])
        rocof2_pu = ddw2_dt / omega_0
        P_ffr2 = -params["K_virtual2"] * rocof2_pu
        ddw2_dt = (omega_0 / (2*H2_total)) * (swing_term_2 + P_ffr2)
    else:
        P_ffr2 = 0.0
        ddw2_dt = (omega_0 / (2*H2_total)) * swing_term_2

    # Governor Equations :
    dP_m1_A_dt = (1.0 / params['T_g1_A']) * ((params['P_ref1_A'] + (params['gamma1_A'] * P_agc1)) - (dw1_pu / params['R1_A']) - P_m1_A)
    dP_m1_B_dt = (1.0 / params['T_g1_B']) * ((params['P_ref1_B'] + (params['gamma1_B'] * P_agc1)) - (dw1_pu / params['R1_B']) - P_m1_B)

    dP_m2_A_dt = (1.0 / params['T_g2_A']) * ((params['P_ref2_A'] + (params['gamma2_A'] * P_agc2)) - (dw2_pu / params['R2_A']) - P_m2_A)
    dP_m2_B_dt = (1.0 / params['T_g2_B']) * ((params['P_ref2_B'] + (params['gamma2_B'] * P_agc2)) - (dw2_pu / params['R2_B']) - P_m2_B)

    ACE1 = (params["B1"]*dw1_pu) + dP_tie
    ACE2 = (params["B2"]*dw2_pu) - dP_tie

    dP_agc1_dt = -params["K_i1"] * ACE1
    dP_agc2_dt = -params["K_i2"] * ACE2
    ddP_tie_dt = params["T_12"] * (dw1_pu - dw2_pu)

    # Charge Discharge Tracking
    d_SoC1_dt = -P_ffr1 / params["E_cap1"]
    if (SoC1<=0.0 and d_SoC1_dt < 0.0) or (SoC1 >= 1.0 and d_SoC1_dt > 0.0):
        d_SoC1_dt = 0.0

    d_SoC2_dt = -P_ffr2 / params["E_cap2"]
    if (SoC2 <= 0.0 and d_SoC2_dt < 0.0) or (SoC2 >= 1.0 and d_SoC2_dt > 0.0):
        d_SoC2_dt = 0.0

    return [
        ddw1_dt, dP_m1_A_dt, dP_m1_B_dt, dP_agc1_dt, d_SoC1_dt,
        ddw2_dt, dP_m2_A_dt, dP_m2_B_dt, dP_agc2_dt, d_SoC2_dt,
        ddP_tie_dt
    ]

def Model_1(t, y, params, disturbance_func1, disturbance_func2):
    """
    11-State Interconnected Two-Area Multi-Generator Grid Engine.
    
    Features:
    - 2 Generators per Area (4 total generators)
    - Bidirectional Batteries in both Areas (Charge & Discharge)
    - Tie-Line Power Flow Interconnection

    """

    omega_0 = params.get("omega_0",2*np.pi * 50)
    
    # Area 1 state variables :
    dw1, P_m1_A, P_m1_B, P_agc1, SoC1 = y[0], y[1], y[2], y[3], max(0.0, min(1.0, y[4]))

    # Area 2 state variables :
    dw2, P_m2_A, P_m2_B, P_agc2, SoC2 = y[5], y[6], y[7], y[8], max(0.0, min(1.0, y[9]))

    dP_tie = y[10]

    dw1_pu = dw1 / omega_0
    dw2_pu = dw2 / omega_0

    P_e1 = disturbance_func1(t)
    P_e2 = disturbance_func2(t)

    H1_total = params["H1_A"] + params["H1_B"]
    H2_total = params["H2_A"] + params["H2_B"]

    swing_term_1 = (P_m1_A + P_m1_B - dP_tie) - P_e1 - (params["D1"] * dw1_pu)
    P_ffr1 = 0.0

    # Bidirectional FFR Trigger logic:
    # If falling frequency (swing_term_1 < 0) & SoC1 > 0 -> Discharge (P_ffr1 > 0)
    # If rising frequency  (swing_term_1 > 0) & SoC1 < 1 -> Charge    (P_ffr1 < 0)
    if (SoC1>0.001 and swing_term_1<0.00) or (SoC1<0.999 and swing_term_1 > 0.0):
        ddw1_dt = (omega_0 * swing_term_1) / (2*H1_total + params["K_virtual1"])
        rocof1_pu = ddw1_dt / omega_0
        P_ffr1 = -params["K_virtual1"] * rocof1_pu
        ddw1_dt = (omega_0 / (2*H1_total)) * (swing_term_1 + P_ffr1)

    else:
        P_ffr1 = 0.0
        ddw1_dt = (omega_0 / (2*H1_total)) * swing_term_1

    swing_term_2 = (P_m2_A + P_m2_B + dP_tie) - P_e2 - (params["D2"] * dw2_pu)
    P_ffr2 = 0.0

    if (SoC2>0.001 and swing_term_2<0.00) or (SoC2<0.999 and swing_term_2 > 0.0):
        ddw2_dt = (omega_0*swing_term_2) / (2*H2_total + params["K_virtual2"])
        rocof2_pu = ddw2_dt / omega_0
        P_ffr2 = -params["K_virtual2"] * rocof2_pu
        ddw2_dt = (omega_0 / (2*H2_total)) * (swing_term_2 + P_ffr2)
    else:
        P_ffr2 = 0.0
        ddw2_dt = (omega_0 / (2*H2_total)) * swing_term_2

    # Governor Equations :
    '''
    Feautures :
    - Generators Max and Min capacity to deliver power
    - Generation Rate Constraint 

    '''
    raw_dP_m1_A_dt = (1.0 / params['T_g1_A']) * ((params['P_ref1_A'] + (params['gamma1_A'] * P_agc1)) - (dw1_pu / params['R1_A']) - P_m1_A)
    dP_m1_A_dt = max(-params["ramp_down1_A"],min(params["ramp_up1_A"],raw_dP_m1_A_dt))
    if P_m1_A >= params["P_max1_A"] and dP_m1_A_dt > 0:
        dP_m1_A_dt = 0
    if P_m1_A <= params["P_min1_A"] and dP_m1_A_dt < 0:
        dP_m1_A_dt = 0


    raw_dP_m1_B_dt = (1.0 / params['T_g1_B']) * ((params['P_ref1_B'] + (params['gamma1_B'] * P_agc1)) - (dw1_pu / params['R1_B']) - P_m1_B)
    dP_m1_B_dt = max(-params["ramp_down1_B"],min(params["ramp_up1_B"],raw_dP_m1_B_dt))
    if P_m1_B >= params["P_max1_B"] and dP_m1_B_dt > 0:
        dP_m1_B_dt = 0
    if P_m1_B<= params["P_min1_B"] and dP_m1_B_dt < 0:
        dP_m1_B_dt = 0


    raw_dP_m2_A_dt = (1.0 / params['T_g2_A']) * ((params['P_ref2_A'] + (params['gamma2_A'] * P_agc2)) - (dw2_pu / params['R2_A']) - P_m2_A)
    dP_m2_A_dt = max(-params["ramp_down2_A"],min(params["ramp_up2_A"],raw_dP_m2_A_dt))
    if P_m2_A >= params["P_max2_A"] and dP_m2_A_dt > 0:
        dP_m2_A_dt = 0
    if P_m2_A <= params["P_min2_A"] and dP_m2_A_dt < 0:
            dP_m2_A_dt = 0

    raw_dP_m2_B_dt = (1.0 / params['T_g2_B']) * ((params['P_ref2_B'] + (params['gamma2_B'] * P_agc2)) - (dw2_pu / params['R2_B']) - P_m2_B)
    dP_m2_B_dt = max(-params["ramp_down2_B"],min(params["ramp_up2_B"],raw_dP_m2_B_dt))
    if P_m2_B >= params["P_max2_B"] and dP_m2_B_dt > 0:
            dP_m2_B_dt = 0
    if P_m2_B <= params["P_min2_B"] and dP_m2_B_dt < 0:
            dP_m2_B_dt = 0

    # In case of emergency, FORCING power transfer in tie lines

    emergency_in_2 = 0.0
    if dw2_pu <-0.006:
        emergency_in_2 = params["K_emergency"] * (dw2_pu)
    ACE1 = (params["B1"]*dw1_pu) + dP_tie + emergency_in_2

    emergency_in_1 = 0.0
    if dw1_pu < -0.006:
        emergency_in_1 = params["K_emergency"] * (dw1_pu)
    ACE2 = (params["B2"]*dw2_pu) - dP_tie + emergency_in_1

    dP_agc1_dt = -params["K_i1"] * ACE1
    dP_agc2_dt = -params["K_i2"] * ACE2

    ddP_tie_dt = params["T_12"] * (dw1_pu - dw2_pu)
    if dP_tie >= params["P_tie_max"] and ddP_tie_dt > 0:
        ddP_tie_dt = 0
    if dP_tie <= -params["P_tie_max"] and ddP_tie_dt < 0:
        ddP_tie_dt = 0


    # Charge Discharge Tracking
    d_SoC1_dt = -P_ffr1 / params["E_cap1"]
    if (SoC1<=0.0 and d_SoC1_dt < 0.0) or (SoC1 >= 1.0 and d_SoC1_dt > 0.0):
        d_SoC1_dt = 0.0

    d_SoC2_dt = -P_ffr2 / params["E_cap2"]
    if (SoC2 <= 0.0 and d_SoC2_dt < 0.0) or (SoC2 >= 1.0 and d_SoC2_dt > 0.0):
        d_SoC2_dt = 0.0

    return [
        ddw1_dt, dP_m1_A_dt, dP_m1_B_dt, dP_agc1_dt, d_SoC1_dt,
        ddw2_dt, dP_m2_A_dt, dP_m2_B_dt, dP_agc2_dt, d_SoC2_dt,
        ddP_tie_dt
    ]












