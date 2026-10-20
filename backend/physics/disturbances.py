import numpy as np

def step_disturbance(t, t_start, P_base, P_delta):
    """
    Simulates a sudden, permanent change
    (E.g., generator trip or large load connection).

    """
    if t >= t_start:
        return P_base + P_delta
    
    return P_base

def pulse_disturbance(t, t_start, t_clear, P_base, P_fault):
    """
    Simulates a temporary fault 
    (E.g., short circuit cleared by a breaker).

    """
    if t_start <= t < t_clear:
        return P_base + P_fault
    
    return P_base

def ramp_disturbance(t, t_start, t_end, P_base, P_delta):
    """
    Simulates a gradual change 
    (E.g., wind farm ramping down or industrial load ramping up).
    
    """
    if t < t_start:
        return P_base
    
    elif t_start <= t <= t_end:
        # Linear interpolation between start and end times
        fraction = (t - t_start) / (t_end - t_start)
        return P_base + fraction * P_delta
    
    else:
        return P_base + P_delta