from typing import List

import numpy as np
import multiprocessing as mp

from desim.simulation import Process, Simulation, Entity, NonTechCost

class Des(object):
    def __init__(self) -> None:
        pass

    def run_simulation(self, flow_time: float, flow_rate: float, 
        flow_start_process: Process, processes: List[Process], 
        non_tech_processes, non_tech_costs: NonTechCost, dsm: dict, 
        discount_rate=0.08, until = 100):
        
        
        sim = Simulation(flow_time, flow_rate, flow_start_process, until, discount_rate,
                     processes, non_tech_processes, non_tech_costs, dsm)
        sim.run_simulation()

        return sim.time_steps, sim.cum_NPV, sim.total_costs, sim.total_revenue

    def run_monte_carlo_simulation(self, flow_time: float, flow_rate: float, 
        flow_start_process: Process, processes: List[Process], 
        non_tech_processes, non_tech_costs: NonTechCost, dsm: dict, 
        discount_rate=0.08, until = 100, runs=300):

        time_steps = []
        cumulative_NPV = []
        total_costs = []
        total_revenue = []

        for _ in range(runs):
            time_s, cum_npv, total_c, total_r = self.run_simulation(flow_time, flow_rate, flow_start_process, processes, non_tech_processes, non_tech_costs, dsm, discount_rate, until)

            time_steps.append(time_s)
            cumulative_NPV.append(cum_npv)
            total_costs.append(total_c)
            total_revenue.append(total_r)
        
        mean_timesteps = []
        mean_npvs = []
        mean_costs = []
        mean_revenue = []

        for ts, npvs, costs, revenue in np.array(time_steps).transpose(), np.array(cumulative_NPV).transpose(), np.array(total_costs).transpose(), np.array(total_revenue).transpose():
            mean_timesteps.append(np.mean(ts))
            mean_npvs.append(np.mean(npvs))
            mean_costs.append(np.mean(costs))
            mean_revenue.append(np.mean(revenue))
        

        return mean_timesteps, mean_npvs, mean_costs, mean_revenue
    
    def run_parallell_simulations(self, flow_time: float, flow_rate: float, 
        flow_start_process: Process, processes: List[Process], 
        non_tech_processes, non_tech_costs: NonTechCost, dsm: dict, 
        discount_rate=0.08, until = 100, runs=300):

        time_steps = []
        cumulative_NPV = []
        total_costs = []
        total_revenue = []


        pool = mp.Pool(mp.cpu_count())

        mp_processes = [pool.apply_async(func=self.run_simulation, args=(flow_time, flow_rate, flow_start_process, processes, non_tech_processes, non_tech_costs, dsm, discount_rate, until)) for _ in range(runs)]

        res = [f.get() for f in mp_processes]

        for time, npv, cost, revenue in res:
            time_steps.append(time)
            cumulative_NPV.append(npv)
            total_costs.append(cost)
            total_revenue.append(revenue)

        mean_timesteps = []
        mean_npvs = []
        mean_costs = []
        mean_revenue = []


        for _time_steps in np.array(time_steps).transpose():
            mean_timesteps.append(np.mean(_time_steps))

        for _cumulative_npv in np.array(cumulative_NPV).transpose():
            mean_npvs.append(np.mean(_cumulative_npv))

        for _total_costs in np.array(total_costs).transpose():
            mean_costs.append(np.mean(_total_costs))
        
        for _total_revenue in np.array(total_revenue).transpose():
            mean_revenue.append(np.mean(_total_revenue))

        #transposed = (_time_steps, _cumulative_npv, _total_costs, _total_revenue)

        #for (ts, npvs, costs, revenue) in transposed:

        return mean_timesteps, mean_npvs, mean_costs, mean_revenue
