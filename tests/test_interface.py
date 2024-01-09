from desim.data import TimeFormat, NonTechCost
from typing import List
import desim.interface as des
import desim.simulation as sim

def create_simple_dsm(processes: List[sim.Process]) -> dict:
  l = len(processes)

  index_list = list(range(0, l))
  dsm = dict()
  for i, p in enumerate(processes):
      dsm.update({p.name: [1 if i + 1 == j else 0 for j in index_list]})
  return dsm


def test_monte_carlo_simulation():
  simulation = des.Des()

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
  flow_rate = 0.004 
  flow_start_process = "Testing"
  until = 30
  discount_rate = 0.08
  dsm = create_simple_dsm(processes)

  results = simulation.run_monte_carlo_simulation(flow_time, flow_rate, flow_start_process, processes, 
      non_tech_processes, NonTechCost.CONTINOUSLY, dsm, TimeFormat.YEAR, discount_rate, until, 10)
  
  assert len(results.mean_npv()) > 0
  assert results.mean_npv()[-1] < 0


def test_multiprocessing():
  simulation = des.Des()

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
  flow_rate = 0.004 
  flow_start_process = "Testing"
  until = 30
  discount_rate = 0.08
  dsm = create_simple_dsm(processes)

  results = simulation.run_parallell_simulations(flow_time, flow_rate, flow_start_process, 
    processes, non_tech_processes, NonTechCost.CONTINOUSLY, dsm, TimeFormat.YEAR, discount_rate,
    until, runs=10)
  
  assert len(results.mean_npv()) > 0
