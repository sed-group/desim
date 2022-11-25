import pytest
import importlib.util

#from simulation import Process, NonTechnicalProcess, Simulation
from desim.data import TimeFormat, NonTechCost

from typing import List

import desim.simulation as sim

def create_simple_dsm(processes: List[sim.Process]) -> dict:
  l = len(processes)

  index_list = list(range(0, l))
  dsm = dict()
  for i, p in enumerate(processes):
      dsm.update({p.name: [1 if i + 1 == j else 0 for j in index_list]})
  return dsm

def test_simulation():
  processes = [
    sim.Process(1, 5, 100000, 0, 'Architectural design', NonTechCost.CONTINOUSLY, TimeFormat.MONTH),
    sim.Process(2, 0, 0, 0, 'Verification', NonTechCost.CONTINOUSLY),
    sim.Process(3, 1, 30000, 0, 'Testing', NonTechCost.CONTINOUSLY, TimeFormat.YEAR),
    sim.Process(4, 3, 200, 0, 'Manufacturing', NonTechCost.CONTINOUSLY, TimeFormat.HOUR),
    sim.Process(5, 1, 100, 0, 'Integration', NonTechCost.CONTINOUSLY, TimeFormat.DAY),
  ]

  non_tech_processes = [
    sim.NonTechnicalProcess("Quality Mangement Process", 10000, 0)
  ]

  flow_time = 3 
  flow_rate = 260 
  flow_start_process = "Testing"
  until = 30
  discount_rate = 0.08
  dsm = create_simple_dsm(processes)

  simulation = sim.Simulation(flow_time, flow_rate, flow_start_process, until, 
    discount_rate, processes, non_tech_processes, NonTechCost.CONTINOUSLY, dsm, TimeFormat.YEAR)
  
  simulation.run_simulation()

  assert len(simulation.time_steps) > 10
  assert len(simulation.cum_NPV) > 10
  assert len(simulation.total_costs) > 10
  assert len(simulation.total_revenue) > 10

def test_sim_time_units():
  processes = [
    sim.Process(1, 20, 20000, 0, '20 months', NonTechCost.CONTINOUSLY, TimeFormat.MONTH),
    sim.Process(1, 0.5, 1000, 2000, "half year", NonTechCost.CONTINOUSLY,  TimeFormat.YEAR)
  ]

  flow_time = 0
  flow_rate = 0
  flow_start_process = ""
  until = 2.5
  discount_rate = 0.08
  dsm = create_simple_dsm(processes)

  sim1 = sim.Simulation(flow_time, flow_rate, flow_start_process, 
    until, discount_rate, processes, [], NonTechCost.CONTINOUSLY, dsm, TimeFormat.YEAR)
  
 
  sim1.run_simulation()
  
  until2 = 26  
  sim2 = sim.Simulation(flow_time, flow_rate, flow_start_process, 
    until2, discount_rate, processes, [], NonTechCost.CONTINOUSLY, dsm, TimeFormat.MONTH)
  
  sim2.run_simulation()
  
  
  assert sim1.time_steps[-1] == 2.25
  assert sim1.total_costs[-1] == 21000
  assert sim1.total_revenue[-1] == 2000

  assert sim2.time_steps[-1] == 2.25 or 2
  assert sim2.total_costs[-1] == 21000
  assert sim2.total_revenue[-1] == 2000

