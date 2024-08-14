import sys
import numpy as np
from pathlib import Path
import itertools
import random

sys.path.insert(1, str( (Path().absolute())  ) + "/src")

from schedule_similar_reactors import num_reactors_needed_for_capacity_factor_weeks_apprioach

def gene_upper_limit(power_list, demand): # limiting the maximum number of each type of reactors

    upper_limit_list = []
    for i in range(len(power_list )):
        # I use the multiplier 1.05 because of the ratio between refueling duration and operational lifetime is will nnot be higher than 1.05
        num_R =int( num_reactors_needed_for_capacity_factor_weeks_apprioach(0, 1,power_list[i], int(40*365/7), demand))
        
        upper_limit =range(int(1 + num_R)) 
        #### WARNING: The 1.05 factor above might need to change if the refueling duration or interval have changed 
        upper_limit_list.append(upper_limit )

    
    return  upper_limit_list

def initial_pop_reactors(power_list, sol_per_pop, possible_solutions): # I got this from M. Abdo
    """
    This function initializes a population of potential solutions for the reactor mix optimization problem.

    Parameters:
    - power_list (list): A list of possible reactor capacities.
    - sol_per_pop (int): The number of potential solutions per population.
    - possible_solutions (list): A list of upper limits for each reactor capacity.

    Returns:
    - pop (list): A list of potential solutions, where each sub-list represents a solution and contains integers representing the number of each reactor type.
    """
    pop = np.zeros((sol_per_pop, len(power_list)))
    for i in range(len(power_list)):
        temp = np.random.randint(0, max(possible_solutions[i]) + 1, size=sol_per_pop).tolist()
        pop[:, i] = temp
    
    return pop.tolist()

# # print(gene_upper_limit([1000, 300, 10], 1500))
# power_list= [1000, 300, 10]
# sol_per_pop = 5
demand = 1500
# possible_solutions = gene_upper_limit(power_list, demand) # gene space
# initial_pop  = initial_pop_reactors(power_list ,sol_per_pop,possible_solutions)
# print(initial_pop )

def initial_pop_reactors_2(power_list,  possible_solutions,sol_per_pop ):
    
    list_of_max_num_of_reactors = []
    for i in range (len(possible_solutions)):
        list_of_max_num_of_reactors.append( max(possible_solutions[i]))
    
     
    list_of_expected_solutions = [[0] * len(power_list)] *len(power_list)
    list_of_expected_solutions_arr = np.array(list_of_expected_solutions)
    
    for i in range(len(power_list)):
        list_of_expected_solutions_arr[i][i] = list_of_max_num_of_reactors[i]
        
    list_of_expected_sols = list_of_expected_solutions_arr.tolist()
    try:
        expanded_list = list(itertools.islice(itertools.cycle(list_of_expected_sols),sol_per_pop - len(list_of_expected_sols)))
         # add numbers randomly to this list
        expanded_list_with_changes = [[item + random.choice([0, 1]) for item in sublist] for sublist in expanded_list]
    except:
        expanded_list_with_changes = []
        
   
    return expanded_list_with_changes + expanded_list
        
power_list= [1000, 300, 10]  
possible_solutions = gene_upper_limit(power_list, demand) # gene space
print(possible_solutions)
# print(max(possible_solutions[0]))
# The code `print(max(possible_solutions[0]))` is finding and printing the maximum value in the list
# `possible_solutions[0]`. This list contains the upper limits for the number of reactors of the first
# type (index 0) based on the given power list and demand. The `max()` function is used to find the
# maximum value in the list, and `print()` is used to display this value.
print( initial_pop_reactors_2(power_list,  possible_solutions, 6))

# lists = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

# # Update the elements
# for i in range(len(lists)):
#     lists[i][i] = 1

# print(lists)


# # Initialize the list of lists
# lists =  [[0] * len(power_list)] *len(power_list)
# lists1 = lists
# print(lists1)
# # Define the additional list
# additional_list = [10, 20, 30]

# # Update the elements
# for i in range(len(lists1)):
#     lists1[i][i] = additional_list[i]

# print(lists)
# a = [[1,2], [3,4]]
# c = (np.array(a))
# print(c[0][0])

