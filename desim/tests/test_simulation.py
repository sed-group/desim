import pytest
import importlib.util

#from simulation import Process, NonTechnicalProcess, Simulation
from desim.data import TimeFormat, NonTechCost

from typing import List

spec = importlib.util.spec_from_file_location("Simulation", "desim/simulation.py")

sim = importlib.util.module_from_spec(spec)

spec.loader.exec_module(sim)

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

