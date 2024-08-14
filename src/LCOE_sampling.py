import random
import numpy as np
from parameters import repeat_elements
from schedule_mixed_reactor_optimizer import capacity_factor_weeks_approach_mix_reactors
from economic_FOMs import level_cost_of_energy_reactor_mix_starting_from_BOAK


def find_possible_combinations(power_list, demand, number_needed_solutions):
# Define the bounds for the coefficients
    lower_bound = demand
    upper_bound = 2*lower_bound

    # List to store solutions
    solutions_store = set()

    # list of coeffients
    a_list =  [0] * len(power_list)
  
    # Find 100 possible solutions
    while len( solutions_store) < number_needed_solutions:
        for i in range(len(a_list)):
            # Randomly choose values for a1, a2, and a3,...
            a_list[i] = random.randint(0, 1+ np.ceil(upper_bound/power_list[i]))
        # print(a_list)
        # # Calculate the value of the equation
        value = sum((np.array(a_list)) * (np.array(power_list)))
   
        # # Check if it falls within the desired range
        if lower_bound <= value <= upper_bound:
            solutions_store.add(tuple(a_list))

    return  list(solutions_store) 

power_list = [300, 20]
demand = 320
num_sol = 10
results = find_possible_combinations(power_list ,demand , num_sol ) 
# first_sol = list(results[0])
first_sol = [2, 0]
power_list_modified = [power_list [i] for i in range(len(first_sol)) if first_sol[i] != 0]
print(power_list_modified)
Num_of_each_reactor_type_modified = [x for x in first_sol if x != 0]

# print(first_sol)
long_list_power = repeat_elements(power_list_modified, Num_of_each_reactor_type_modified)
levelization_period_weeks = int(40*365/7)
interest_rate = 0.06
# print(long_list_power )
capacity_factor_results =   capacity_factor_weeks_approach_mix_reactors(long_list_power  ,levelization_period_weeks, demand)
MWh_generated_per_year_per_demand_list = capacity_factor_results[4]
MWh_excess_per_year_list =     capacity_factor_results[5]
Tot_OM__cost_per_year_list =  capacity_factor_results[6]

# capacity_factor_t_min = min(capacity_factor_results[1])
# output_lcoe = level_cost_of_energy_reactor_mix_starting_from_BOAK( interest_rate, power_list_modified, Num_of_each_reactor_type_modified,\
            # MWh_generated_per_year_per_demand_list, MWh_excess_per_year_list, 0,\
            #     Tot_OM__cost_per_year_list)
# print(output_lcoe, capacity_factor_t_min)