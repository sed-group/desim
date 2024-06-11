from dataclasses import dataclass
import random as r
import numpy as np
from typing import Optional

import simpy

from desim.data import NonTechCost, TimeFormat
from desim.helper import isfloat

TIMESTEP = 0.25

class Simulation(object):
    # @param:
    # flow_time = the time that entities will flow in the system
    # interarrival_time = the rate at which entities will flow in the system
    # interarrival_process = the process at which the entities will start flowing
    # until = the total simulation time
    def __init__(self, flow_time: float, flow_rate: float, flow_process: str, simulation_runtime: float,
                 discount_rate: float, processes, non_tech_processes, non_tech_addition, dsm,
                 time_format: TimeFormat) -> None:
        self.flow_time = flow_time
        self.flow_rate = flow_rate
        self.interarrival_time = 0 if flow_rate <= 0 else 1 / (
                    flow_rate * time_format.value)  # Causes the interarrival time to be in years.
        self.interarrival_process = flow_process
        self.until = simulation_runtime / time_format.value  # Causes the runtime to be in years.
        self.discount_rate = discount_rate
        self.cum_NPV = [0]
        self.total_costs = [0]
        self.total_revenue = [0]
        self.time_steps = [0]
        self.entities = []
        self.processes = processes
        self.non_tech_costs = sum([p.cost for p in non_tech_processes])
        self.non_tech_revenues = sum([p.revenue for p in non_tech_processes])
        self.add_non_tech = non_tech_addition
        self.dsm_before_flow, self.dsm_after_flow = self.get_dsm_separation(dsm)
        self.time_format = time_format

    # Sets up the simpy environment and runs the simulation
    def run_simulation(self):
        env = simpy.Environment()
        env.process(self.lifecycle(env))
        env.process(self.observe_costs(env))
        env.run(until=self.until + TIMESTEP)

    # Initializes the lifecycle in each of the entities. Runs everything before the interarrival
    # process as a single entity.
    def lifecycle(self, env):
        interarrival_process = list(filter(lambda p: p.name == self.interarrival_process, self.processes))
        total_ent_amount = 0 if self.interarrival_time <= 0 else (1 / self.interarrival_time) * self.flow_time

        if self.interarrival_process != self.processes[0].name:
            e = Entity(env, self.processes, self.non_tech_costs)
            self.entities.append(e)
            yield env.process(e.lifecycle(self.dsm_before_flow, [self.processes[0]], 1))

        end_flow = env.now + self.flow_time
        while env.now < end_flow:
            if self.flow_rate >= 1/TIMESTEP:
                n_entities = int(self.flow_rate * TIMESTEP)
                timeout = TIMESTEP
            else:
                n_entities = int(self.flow_rate)
                timeout = 1
            for _ in range(int(n_entities)):
                mod_entities = self.flow_rate % (1/timeout)
                if env.now % 1 == 0 and mod_entities != 0:
                    for _ in range(int(mod_entities)): # Run the entities that are left over from converting n_entities to an integer
                        e = Entity(env, self.processes, self.non_tech_costs)
                        self.entities.append(e)
                        env.process(e.lifecycle(self.dsm_after_flow, interarrival_process, total_ent_amount))
                e = Entity(env, self.processes, self.non_tech_costs)
                self.entities.append(e)
                env.process(e.lifecycle(self.dsm_after_flow, interarrival_process, total_ent_amount))
            yield env.timeout(timeout)


    # Observes the total time, cost, revenue, and NPV for each entity in each timestep.
    def observe_costs(self, env):

        if self.add_non_tech == NonTechCost.LUMP_SUM:
            self.total_costs[0] += self.non_tech_costs

        while True:
            yield env.timeout(TIMESTEP)
            if self.add_non_tech == NonTechCost.CONTINOUSLY:
                self.add_static_costs_to_entities()

            self.total_costs.append(sum([e.cost for e in self.entities]))
            self.total_revenue.append(sum([e.revenue for e in self.entities]))
            self.time_steps.append(env.now)

            self.calculate_NPV(self.total_costs, self.total_revenue, self.time_steps)
            
            

    # Generates the waiting time as interarrival rate on an exponential distribution
    def generate_interarrival(self):
        return np.random.exponential(self.interarrival_time)

    def add_static_costs_to_entities(self):  # Adds the costs of the non-technical processes to all active entities.
        for e in self.entities:
            e.cost += self.non_tech_costs * TIMESTEP / (
                        len(self.entities) * (self.until)) # This works in the margin of 0.00000002 euros

    def calculate_NPV(self, total_costs, total_revenue, time_steps):
        timestep_revenue = total_revenue[len(time_steps) - 1] - total_revenue[len(time_steps) - 2]
        timestep_cost = total_costs[len(time_steps) - 1] - total_costs[len(time_steps) - 2]

        net_revenue = timestep_revenue - timestep_cost  # Cashflow for the timestep
        npv = net_revenue / ((1 + self.discount_rate) ** time_steps[-1])
        self.cum_NPV.append(self.cum_NPV[-1] + npv)

    # Separates the given DSM into two dictionaries with the before flow and after flow parts of the dsm
    def get_dsm_separation(self, dsm):
        before_dsm = dict()
        dsm = dsm.copy()
        for key, row in dsm.items():
            dsm[key] = [float(x) if isfloat(x) else 0 for x in row]
        for i in range(len(self.processes)):
            if self.processes[i].name == self.interarrival_process:
                break
            before_dsm.update({self.processes[i-1].name: dsm.pop(self.processes[i-1].name)})
        return before_dsm, dsm


class Entity(object):
    # @param
    # env = the simpy environment
    # processes = the processes that the entity will go through
    def __init__(self, env, processes, total_non_tech_costs) -> None:
        self.env = env
        self.processes = processes
        self.total_time = []
        self.total_cost = []
        self.total_revenue = []
        self.cost = 0
        self.revenue = 0
        self.total_non_tech_costs = total_non_tech_costs

    # Runs the lifecycle for this entity.
    # Can choose between processes but cannot run multiple processes in parallell
    def lifecycle(self, dsm, current_processes, ent_amount):
        active_activities = current_processes
        while len(active_activities) > 0:
            for activity in active_activities:
                yield self.env.process(activity.run_process(self.env, self, ent_amount, self.total_non_tech_costs))
            active_activities = self.find_active_activities(dsm, active_activities)  # Find subsequent activities


    # Finds the active processes for the lifecycle based on the dsm and the current state
    # That the lifecycle is in.
    def find_active_activities(self, dsm: dict, current_processes):
        active_activities = []
        for process in current_processes:
            if (process.name not in dsm.keys()):
                break

            transitions = dsm.get(process.name)

            if (all([p == 0 for p in
                     transitions])):  # Checks if all rows are 0, if that is the case then there is nothing more to be done after this process
                continue

            next_processes = []
            self.choose_process_from_row(transitions, next_processes)  # Select the process index from its row
            #if process_index >= len(self.processes):  # Simulation has reached the end
            #    continue
            
            if any([p >= len(self.processes) for p in next_processes]):
                continue
            
            active_activities += [self.processes[p] for p in next_processes]

        return active_activities

    # Selects a process index from a row of transitional probabilities
    def choose_process_from_row(self, row, next_processes):
        if sum(row) > 1:
            process_index = r.choices([i for i, _ in enumerate(row)], row, k=1)[0] - 1
            next_processes.append(process_index)
            row[process_index + 1] = 0
            self.choose_process_from_row(row, next_processes)
        elif sum(row) > 0:
            next_processes.append(r.choices([i for i, _ in enumerate(row)], row, k=1)[0] - 1)  # -1 because the first column is the start


@dataclass
class Process(object):
    # @param
    # id = the id of a process
    # time = the time a process will take in years.
    # cost = the cost of a process
    # revenue = the revenue of a process
    # name = the name of a process
    # time_format = the unit in which the time is given.
    def __init__(self, id, time, cost, revenue, name, add_non_tech: NonTechCost,
                 time_format: Optional[TimeFormat] = None) -> None:
        self.time = self.convert_time_format_to_default(time, time_format)
        self.cost = cost
        self.revenue = revenue
        self.W = 1
        self.WN = False
        self.id = id
        self.name = name
        self.add_non_tech = add_non_tech

    # Converts all times to the correct (default: Years) time format
    def convert_time_format_to_default(self, time, time_format: Optional[TimeFormat] = None):
        return (time / time_format.value) if time_format is not None else 0

    # Runs a process and adds the cost and the revenue to the entity
    def run_process(self, env, entity, ent_amount, non_tech_costs):
        # Calculate the number of timesteps based on the total time and the timestep
        if self.time >= TIMESTEP:
            num_steps = int(self.time * self.W / TIMESTEP)

            # Calculate the cost and revenue to be added at each timestep
            cost_per_step = self.cost / num_steps
            revenue_per_step = self.revenue / num_steps
            
            for _ in range(num_steps):
                entity.cost += cost_per_step
                entity.revenue += revenue_per_step

                if self.add_non_tech == NonTechCost.TO_TECHNICAL_PROCESS:
                    added_cost = (non_tech_costs * self.time / (sum([p.time for p in entity.processes]) * ent_amount)) / num_steps
                    entity.cost += added_cost
                yield env.timeout(TIMESTEP)  # Wait for the timestep duration
        else: # Add full value if under TIMESTEP. If the time is 0, then the process is instantaneous
            entity.cost += self.cost
            entity.revenue += self.revenue

            if self.add_non_tech == NonTechCost.TO_TECHNICAL_PROCESS:
                added_cost = non_tech_costs * self.time / (sum([p.time for p in entity.processes]) * ent_amount)
                entity.cost += added_cost
            yield env.timeout(self.time)

@dataclass
class NonTechnicalProcess(object):
    def __init__(self, name: str, cost: float, revenue: float) -> None:
        self.name = name
        self.cost = cost
        self.revenue = revenue
