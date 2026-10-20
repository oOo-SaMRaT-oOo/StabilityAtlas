from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass
class SimulationResult:
    sim_id : int
    time : np.ndarray
    states : np.ndarray
    parameters : dict
    metrics : dict

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame({
            "time" : self.time,
            "dw1" : self.states[:,0],
            "P_m1_A": self.states[:, 1],
            "P_m1_B": self.states[:, 2],
            "P_agc1": self.states[:, 3],
            "SoC1": self.states[:, 4],
            "dw2": self.states[:, 5],
            "P_m2_A": self.states[:, 6],
            "P_m2_B": self.states[:, 7],
            "P_agc2": self.states[:, 8],
            "SoC2": self.states[:, 9],
            "dP_tie": self.states[:, 10],
            "freq1_hz": 50.0 + (self.states[:, 0] / (2 * np.pi)),
            "freq2_hz": 50.0 + (self.states[:, 5] / (2 * np.pi)),
        })