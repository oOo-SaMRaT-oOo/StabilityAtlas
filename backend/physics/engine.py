import numpy as np

def Stability_Atlas_Engine(t, y, params, disturbance_func1, disturbance_func2):

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













