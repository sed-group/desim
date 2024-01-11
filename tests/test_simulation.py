from desim.data import TimeFormat, NonTechCost
from typing import List

import desim.simulation as sim


def create_simple_dsm(processes: List[sim.Process]) -> dict:
    n = len(processes) + 2  # +2 for start and end
    dsm = dict()
    for i in range(n):
        if i == 0:
            name = "Start"
        elif i == n - 1:
            name = "End"
        else:
            name = processes[i - 1].name

        dsm.update({name: [1 if i + 1 == j else "X" if i == j else 0 for j in range(n)]})
    return dsm


def get_processes():
    processes = [
        sim.Process(1, 5, 100000, 0, 'Architectural design', NonTechCost.CONTINOUSLY, TimeFormat.MONTH),
        sim.Process(2, 0, 0, 0, 'Verification', NonTechCost.CONTINOUSLY),
        sim.Process(3, 0.8, 30000, 0, 'Testing', NonTechCost.CONTINOUSLY, TimeFormat.YEAR),
        sim.Process(4, 3, 200, 1000, 'Manufacturing', NonTechCost.CONTINOUSLY, TimeFormat.HOUR),
        sim.Process(5, 1, 100, 10000, 'Integration', NonTechCost.CONTINOUSLY, TimeFormat.DAY),
    ]
    non_tech_processes = [
        sim.NonTechnicalProcess("Quality Management Process", 10000, 0)
    ]
    return processes, non_tech_processes


def test_simulation_sequential():
    processes, non_tech_processes = get_processes()

    flow_time = 3
    flow_rate = 260
    flow_start_process = "Testing"
    until = 30
    discount_rate = 0.08
    dsm = create_simple_dsm(processes)

    simulation = sim.Simulation(flow_time, flow_rate, flow_start_process, until,
                                discount_rate, processes, non_tech_processes, NonTechCost.CONTINOUSLY, dsm,
                                TimeFormat.YEAR)

    simulation.run_simulation()

    assert len(simulation.time_steps) > 10
    assert len(simulation.cum_NPV) > 10
    assert len(simulation.total_costs) > 10
    assert len(simulation.total_revenue) > 10


def test_simulation_alt_order():
    processes, non_tech_processes = get_processes()

    flow_time = 3
    flow_rate = 260
    flow_start_process = "Testing"
    until = 30
    discount_rate = 0.08

    dsm = {
        "Start":                ["X", 0, 0, 1, 0, 0, 0],
        "Architectural design": [0, "X", 1, 0, 0, 0, 0],
        "Verification":         [0, 0, "X", 0, 1, 0, 0],
        "Testing":              [0, 1, 0, "X", 0, 0, 0],
        "Manufacturing":        [0, 0, 0, 0, "X", 1, 0],
        "Integration":          [0, 0, 0, 0, 0, "X", 1],
        "End":                  [0, 0, 0, 0, 0, 0, "X"]
    }

    simulation = sim.Simulation(flow_time, flow_rate, flow_start_process, until,
                                discount_rate, processes, non_tech_processes, NonTechCost.CONTINOUSLY, dsm,
                                TimeFormat.YEAR)

    simulation.run_simulation()

    assert len(simulation.time_steps) > 10
    assert len(simulation.cum_NPV) > 10
    assert len(simulation.total_costs) > 10
    assert len(simulation.total_revenue) > 10


def test_simulation_alt_order2():
    processes, non_tech_processes = get_processes()

    flow_time = 3
    flow_rate = 260
    flow_start_process = "Testing"
    until = 30
    discount_rate = 0.08

    dsm = {
        "Start":                ["X", 1, 0, 0, 0, 0, 0],
        "Architectural design": [0, "X", 1, 0, 0, 0, 0],
        "Verification":         [0, 0, "X", 1, 0, 0, 0],
        "Testing":              [0, 0, 0, "X", 0, 1, 0],
        "Manufacturing":        [0, 0, 0, 0, "X", 0, 1],
        "Integration":          [0, 0, 0, 0, 1, "X", 0],
        "End":                  [0, 0, 0, 0, 0, 0, "X"]
    }

    simulation = sim.Simulation(flow_time, flow_rate, flow_start_process, until,
                                discount_rate, processes, non_tech_processes, NonTechCost.CONTINOUSLY, dsm,
                                TimeFormat.YEAR)

    simulation.run_simulation()

    assert len(simulation.time_steps) > 10
    assert len(simulation.cum_NPV) > 10
    assert len(simulation.total_costs) > 10
    assert len(simulation.total_revenue) > 10


def test_simulation_end_early():
    processes, non_tech_processes = get_processes()

    flow_time = 3
    flow_rate = 260
    flow_start_process = "Testing"
    until = 30
    discount_rate = 0.08
    dsm1 = create_simple_dsm(processes)
    dsm2 = {
        "Start":                ["X", 1, 0, 0, 0, 0, 0],
        "Architectural design": [0, "X", 1, 0, 0, 0, 0],
        "Verification":         [0, 0, "X", 1, 0, 0, 0],
        "Testing":              [0, 0, 0, "X", 0, 0, 1],
        "Manufacturing":        [0, 0, 0, 0, "X", 0, 0],
        "Integration":          [0, 0, 0, 0, 0, "X", 0],
        "End":                  [0, 0, 0, 0, 0, 0, "X"]
    }

    simulation1 = sim.Simulation(flow_time, flow_rate, flow_start_process, until,
                                discount_rate, processes, non_tech_processes, NonTechCost.CONTINOUSLY, dsm1,
                                TimeFormat.YEAR)

    simulation1.run_simulation()

    simulation2 = sim.Simulation(flow_time, flow_rate, flow_start_process, until,
                                 discount_rate, processes, non_tech_processes, NonTechCost.CONTINOUSLY, dsm2,
                                 TimeFormat.YEAR)

    simulation2.run_simulation()

    assert simulation1.total_costs[-1] > simulation2.total_costs[-1]
    assert simulation1.total_revenue[-1] > simulation2.total_revenue[-1]


def test_simulation_with_probability():
    processes, non_tech_processes = get_processes()

    flow_time = 3
    flow_rate = 260
    flow_start_process = "Testing"
    until = 30
    discount_rate = 0.08

    dsm = {
        "Start":                ["X", 1, 0, 0, 0, 0, 0],
        "Architectural design": [0, "X", 0.3, 0.2, 0.5, 0, 0],
        "Verification":         [0, 0, "X", 1, 0, 0, 0],
        "Testing":              [0, 0, 0, "X", 0.5, 0.5, 0],
        "Manufacturing":        [0, 0, 0, 0, "X", 1, 0],
        "Integration":          [0, 0, 0, 0, 0, "X", 1],
        "End":                  [0, 0, 0, 0, 0, 0, "X"]
    }

    simulation = sim.Simulation(flow_time, flow_rate, flow_start_process, until,
                                discount_rate, processes, non_tech_processes, NonTechCost.CONTINOUSLY, dsm,
                                TimeFormat.YEAR)

    simulation.run_simulation()

    assert len(simulation.time_steps) > 10
    assert len(simulation.cum_NPV) > 10
    assert len(simulation.total_costs) > 10
    assert len(simulation.total_revenue) > 10


def test_simulation_with_probability_rework():
    processes, non_tech_processes = get_processes()

    flow_time = 3
    flow_rate = 260
    flow_start_process = "Testing"
    until = 30
    discount_rate = 0.08

    dsm = {
        "Start":                ["X", 1, 0, 0, 0, 0, 0],
        "Architectural design": [0, "X", 1, 0, 0, 0, 0],
        "Verification":         [0, 0.9, "X", 0.1, 0, 0, 0],
        "Testing":              [0, 0, 0, "X", 0.5, 0.5, 0],
        "Manufacturing":        [0, 0, 0, 0, "X", 1, 0],
        "Integration":          [0, 0, 0, 0, 0, "X", 1],
        "End":                  [0, 0, 0, 0, 0, 0, "X"]
    }

    simulation = sim.Simulation(flow_time, flow_rate, flow_start_process, until,
                                discount_rate, processes, non_tech_processes, NonTechCost.CONTINOUSLY, dsm,
                                TimeFormat.YEAR)

    simulation.run_simulation()

    assert len(simulation.time_steps) > 10
    assert len(simulation.cum_NPV) > 10
    assert len(simulation.total_costs) > 10
    assert len(simulation.total_revenue) > 10


def test_sim_time_units():
    processes = [
        sim.Process(1, 20, 20000, 0, '20 months', NonTechCost.CONTINOUSLY, TimeFormat.MONTH),
        sim.Process(1, 0.5, 1000, 2000, "half year", NonTechCost.CONTINOUSLY, TimeFormat.YEAR)
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

    assert sim1.time_steps[-1] == 2.5
    assert sim1.total_costs[-1] == 21000
    assert sim1.total_revenue[-1] == 2000

    assert sim2.time_steps[-1] == 2.25
    assert sim2.total_costs[-1] == 21000
    assert sim2.total_revenue[-1] == 2000
