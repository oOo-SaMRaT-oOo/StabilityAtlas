import numpy as np
from scipy.integrate import solve_ivp

def swing_equation_ode(t, y, H, D, P_m, P_e, omega_0=2 * np.pi * 50):
    """
    Defines the ordinary differential equation (ODE) for the swing equation.
    
    Parameters:
    -----------
    t : float
        Current time step (seconds).
    y : list or ndarray
        State variables: [delta_omega] (frequency deviation in rad/s).
    H : float
        Inertia constant (seconds).
    D : float
        Damping factor (p.u.).
    P_m : float
        Mechanical power input (p.u.).
    P_e : float
        Electrical power demand/load (p.u.).
    omega_0 : float, optional
        Nominal system frequency in rad/s. Defaults to 2*pi*50 (50 Hz grid).
        
    Returns:
    --------
    list
        Derivative of the state variables: [d_delta_omega_dt]
    """
    delta_omega = y[0]
    
    # Swing Equation re-arranged: d(delta_omega)/dt = (omega_0 / 2H) * (P_m - P_e - D * delta_omega)
    d_delta_omega_dt = (omega_0 / (2 * H)) * (P_m - P_e - (D * delta_omega))
    
    return [d_delta_omega_dt] # Returns the List of Functions for particular value of omega given


def simulate_frequency_response(t_span, y0, H, D, P_m, P_e, omega_0=2 * np.pi * 50, t_eval=None):
    """
    Solves the swing equation over a specified time span.
    """
    sol = solve_ivp(
        fun=swing_equation_ode,
        t_span=t_span,
        y0=y0,
        args=(H, D, P_m, P_e, omega_0),
        method='RK45',  # Runge-Kutta 45 explicit solver
        t_eval=t_eval
    )

    return sol