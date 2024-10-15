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