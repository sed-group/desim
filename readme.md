# Discrete Event Simulation
Library to run a simple discrete event simulation. Runs on simpy.

## Installation
1. Clone the repository
2. Run the following commands:

  `pip install wheel`

  `pip install .`

3. Now the package `desim` is installed. 


## Running a simulation

To run a simulation the suggestion is to use the interface provided in `desim/interface.py`

There the different types of simulations are provided. 

Example code of running a monte carlo simulation:

```python
from desim.interface import Des
from desim.data import NonTechCost, TimeFormat
from desim.simulation import Process


dsm = dict({
    'Design Process': [0, 1, 0],
    'Testing Process': [0, 0, 1],
    'Manufacturing Process': [0, 0, 0.2]
})


processes = [
  Process(1, 10000, 100000, 0, 'Desing Process', NonTechCost.CONTINOUSLY, TimeFormat.MONTH),
  Process(3, 5000, 30000, 0, 'Testing Process', NonTechCost.CONTINOUSLY, TimeFormat.YEAR),
  Process(4, 300, 200, 100, 'Manufacturing Process', NonTechCost.CONTINOUSLY, TimeFormat.HOUR),
]

non_tech_processes = [
  NonTechnicalProcess("Quality Mangement Process", 10000, 0)
]

flow_time = 3 
flow_rate = 260
flow_start_process = "Testing Process"
non_tech_cost = NonTechCost.CONTINOUSLY
time_unit = TimeFormat.YEAR
until = 30
discount_rate = 0.08
runs = 100


sim = Des()

results = sim.run_monte_carlo_simulation(flow_time, flow_rate, flow_start_process, processes, 
          non_tech_processes, non_tech_cost, dsm, time_unit, discount_rate, until, runs)

```