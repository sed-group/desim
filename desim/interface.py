from typing import List
import multiprocessing as mp
from desim.data import SimResults, TimeFormat
from desim.simulation import Process, Simulation, NonTechCost


class Des(object):
    """
    This is a class for running a discrete event simulation.

    It is an interface of the different types of simulations that can be run.
    Possible simulation types:
      Normal simulation.
      Monte Carlo simulation.
      Parallellized simulation.
    """

    def __init__(self) -> None:
        pass

    def run_simulation(self, flow_time: float, flow_rate: float,
                       flow_start_process: str, processes: List[Process],
                       non_tech_processes, non_tech_costs: NonTechCost, dsm: dict, time_format: TimeFormat,
                       discount_rate=0.08, until=100):
        """
        Function for running a standard discrete event simulation. Will run the simulation once.

        Parameters:
          flow_time (float): The time that entities will flow in the simulation.
          flow_rate (float): The rate that entities will flow in the simulation. Calculated as Product/time_unit
          flow_start_process (str): The process that will start the flow of entites. Takes the name of the process
          processes (List[Process]): The list of processes of the simulation.
          non_tech_processes (List[NonTechProcess]): The list of non technical processes in the simulation.
          non_tech_costs (NonTechCost): How the non technical processes will be distributed.
          dsm (dict): A design structure matrix showing how the processes interact with eachother.
          time_format (TimeFormat): The unit of time of the simulation.
          discount_rate (float): The discount rate.
          until (float): For how long the simulation will run.

        """

        sim = Simulation(flow_time, flow_rate, flow_start_process, until, discount_rate,
                         processes, non_tech_processes, non_tech_costs, dsm, time_format)
        sim.run_simulation()

        return SimResults('No Design', processes, [sim.time_steps], [sim.cum_NPV], [sim.total_costs],
                          [sim.total_revenue])

    def run_monte_carlo_simulation(self, flow_time: float, flow_rate: float,
                                   flow_start_process: str, processes: List[Process],
                                   non_tech_processes, non_tech_costs: NonTechCost, dsm: dict, time_format: TimeFormat,
                                   discount_rate=0.08, until=100, runs=300):
        """
        Function for running a monte carlo version of the simulation. Will run the simulation @runs amount of times.

        Parameters:
          flow_time (float): The time that entities will flow in the simulation.
          flow_rate (float): The rate that entities will flow in the simulation. Calculated as Product/time_unit
          flow_start_process (str): The process that will start the flow of entites. Takes the name of the process
          processes (List[Process]): The list of processes of the simulation.
          non_tech_processes (List[NonTechProcess]): The list of non technical processes in the simulation.
          non_tech_costs (NonTechCost): How the non technical processes will be distributed.
          dsm (dict): A design structure matrix showing how the processes interact with eachother.
          time_format (TimeFormat): The unit of time of the simulation.
          discount_rate (float): The discount rate.
          until (float): For how long the simulation will run.
          runs (int): The amount of times the simulation will be run.

        """

        time_steps = []
        cumulative_NPV = []
        total_costs = []
        total_revenue = []

        for _ in range(runs):
            sim = Simulation(flow_time, flow_rate, flow_start_process, until, discount_rate,
                             processes, non_tech_processes, non_tech_costs, dsm, time_format)
            sim.run_simulation()

            time_steps.append(sim.time_steps)
            cumulative_NPV.append(sim.cum_NPV)
            total_costs.append(sim.total_costs)
            total_revenue.append(sim.total_revenue)

        return SimResults('No Design', processes, time_steps, cumulative_NPV, total_costs, total_revenue)

    def run_parallell_simulations(self, flow_time: float, flow_rate: float,
                                  flow_start_process: str, processes: List[Process],
                                  non_tech_processes, non_tech_costs: NonTechCost, dsm: dict, time_format: TimeFormat,
                                  discount_rate=0.08, until=100, runs=300):
        """
        Function for running a parallelized monte carlo version of the simulation.
        Will run the simulation @runs amount of times.

        Parameters:
          flow_time (float): The time that entities will flow in the simulation.
          flow_rate (float): The rate that entities will flow in the simulation. Calculated as Product/time_unit
          flow_start_process (str): The process that will start the flow of entites. Takes the name of the process.
          processes (List[Process]): The list of processes of the simulation.
          non_tech_processes (List[NonTechProcess]): The list of non technical processes in the simulation.
          non_tech_costs (NonTechCost): How the non technical processes will be distributed.
          dsm (dict): A design structure matrix showing how the processes interact with eachother.
          time_format (TimeFormat): The unit of time of the simulation.
          discount_rate (float): The discount rate.
          until (float): For how long the simulation will run.
          runs (int): The amount of times the simulation will be run.

        """

        time_steps = []
        cumulative_NPV = []
        total_costs = []
        total_revenue = []

        # Try/Catch because it can only be set once.
        try:
            # Important! If not set, the server will be terminated after simulation is complete.
            mp.set_start_method('spawn')
        except RuntimeError:
            pass
        pool = mp.Pool(mp.cpu_count())

        mp_processes = [
            pool.apply_async(func=self.help_run_simulation, args=(flow_time, flow_rate, flow_start_process, processes,
                                                                  non_tech_processes, non_tech_costs, dsm, time_format,
                                                                  discount_rate, until)) for _ in range(runs)]

        res = [f.get() for f in mp_processes]

        for time, npv, cost, revenue in res:
            time_steps.append(time)
            cumulative_NPV.append(npv)
            total_costs.append(cost)
            total_revenue.append(revenue)

        return SimResults('No Design', processes, time_steps, cumulative_NPV, total_costs, total_revenue)

    def help_run_simulation(self, flow_time: float, flow_rate: float,
                            flow_start_process: str, processes: List[Process],
                            non_tech_processes, non_tech_costs: NonTechCost, dsm: dict, time_format: TimeFormat,
                            discount_rate=0.08, until=100):
        """
        Helper function for the parallelization module in this class.

        """

        sim = Simulation(flow_time, flow_rate, flow_start_process, until, discount_rate,
                         processes, non_tech_processes, non_tech_costs, dsm, time_format)
        sim.run_simulation()

        return sim.time_steps, sim.cum_NPV, sim.total_costs, sim.total_revenue
