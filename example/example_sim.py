import desim.interface as des
from desim.data import TimeFormat, NonTechCost
import desim.simulation as sim
import matplotlib.pyplot as plt


def simulation_sequential_example():
    simulation = des.Des()
    processes = [
        sim.Process(
            1, 5, 200, 0, "Architectural design", NonTechCost.TO_TECHNICAL_PROCESS, TimeFormat.YEAR
        ),
        sim.Process(
            2, 400, 3.0, 0, "Implementation", NonTechCost.TO_TECHNICAL_PROCESS, TimeFormat.HOUR
        ),
        sim.Process(
            3, 20.14, 0.34, 0, "Integration", NonTechCost.TO_TECHNICAL_PROCESS, TimeFormat.MINUTES
        ),
        sim.Process(
            4, 0, 1.9, 5.5, "Operation", NonTechCost.TO_TECHNICAL_PROCESS, TimeFormat.YEAR
        ),
    ]
    processes2 = [
        sim.Process(
            1, 5, 250, 0, "Architectural design", NonTechCost.TO_TECHNICAL_PROCESS, TimeFormat.YEAR
        ),
        sim.Process(
            2, 5, 0, 50, "Implementation", NonTechCost.TO_TECHNICAL_PROCESS, TimeFormat.YEAR
        ),
        sim.Process(
            3, 1, 0, 100, "Integration", NonTechCost.TO_TECHNICAL_PROCESS, TimeFormat.YEAR
        ),
        sim.Process(
            4, 10, 0, 100, "Operation", NonTechCost.TO_TECHNICAL_PROCESS, TimeFormat.YEAR
        ),
    ]
    non_tech_processes = [sim.NonTechnicalProcess("Project portfolio management", 0, 0)]

    dsm = {
        "Start":                ["X", 1, 0, 0, 0, 0],
        "Architectural design": [0, "X", 1, 0, 0, 0],
        "Implementation":       [0, 0, "X", 1, 0, 0],
        "Integration":          [0, 0, 0, "X", 1, 0],
        "Operation":            [0, 0, 0, 0, "X", 1],
        "End":                  [0, 0, 0, 0, 0, 0]
    }

    flow_time = 5
    flow_rate = 10
    flow_start_process = "Implementation"
    until = 30
    discount_rate = 0.08

    simulation = simulation.run_simulation(
        flow_time,
        flow_rate,
        flow_start_process,
        processes2,
        non_tech_processes,
        NonTechCost.TO_TECHNICAL_PROCESS,
        dsm,
        TimeFormat.YEAR,
        discount_rate,
        until
    )

    print("NPV:", simulation.npvs[0])
    print("Time:", simulation.timesteps[0])

    plt.plot(simulation.timesteps[0], simulation.npvs[0])
    plt.ylabel("NPV")
    plt.show()

simulation_sequential_example()
