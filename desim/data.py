from dataclasses import dataclass
from typing import List
from enum import Enum
import numpy as np

class NonTechCost(Enum):
    """
    The ways of choosing how to apply the non-technical process costs
    """
    TO_TECHNICAL_PROCESS = 'to_process'
    LUMP_SUM = 'lump_sum'
    CONTINOUSLY = 'continously'
    NO_ADDED_COST = 'no_cost'


class TimeFormat(Enum):
    """
    The timeformats that can be chosen for a process. The values are the defaults for the
    simulation (years)
    """
    MINUTES = 365*24*60
    HOUR = 365*24
    DAY = 365
    WEEK = 52
    MONTH = 12
    YEAR = 1

@dataclass(unsafe_hash=True)
class SimResults:
    """
    Class for saving the results from a simulation and doing simple
    calculations on the results
    """
    design: str
    processes: List
    timesteps: List[List[float]]
    npvs: List[List[float]]
    costs: List[List[float]]
    revenues: List[List[float]]

    def normalize_npv(self):
        normalized_npv = []

        mean_npv = self.mean_npv()
        max_npv = max(mean_npv)
        min_npv = min(mean_npv)

        delta_npv = max_npv - min_npv
        for npv in mean_npv:
            n_npv = (npv - min_npv) / delta_npv
            normalized_npv.append(n_npv)

        return normalized_npv 


    def mean_npv_payback_time(self):
        """
        Calculates the time it takes before the mean npv 
        starts to generate value. If the mean NPV doesn't
        go above 0 then -1 is returned. 
        """
        
        for t, n in zip(self.timesteps[-1], self.mean_npv()):
            if n > 0:
                return t
        
        return -1

    def mean_npv(self):
        mean_npvs = []
        for _cumulative_npv in np.array(self.npvs).transpose():
            mean_npvs.append(np.mean(_cumulative_npv))
        
        return mean_npvs
    
    def mean_costs(self):
        mean_costs = []
        for costs in np.array(self.costs).transpose():
            mean_costs.append(np.mean(costs))
        
        return mean_costs
    
    def mean_revenues(self):
        mean_revenues = []
        for revenues in np.array(self.revenues).transpose():
            mean_revenues.append(np.mean(revenues))

        return mean_revenues
    
    def all_max_npv(self):
        max_npv = []
        for npv in self.npvs:
            max_npv.append(npv[-1])
        return max_npv