#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import sys
import pandas as pd
import pygad
import matplotlib.pyplot as plt
import warnings
from pathlib import Path

import time
warnings.filterwarnings('ignore')
sys.path.insert(1, str( (Path().absolute())  ) + "/src")


from parameters import  repeat_elements
from schedule_mixed_reactor_optimizer_Abdo import capacity_factor_weeks_approach_mix_reactors
from economic_FOMs import level_cost_of_energy_reactor_mix


# # Gene Space

# # LCOE Optimization

# In[2]:


# def initial_population_reactors(power_list, sol_per_pop):
#     # initialization : the number of each reactor type is zero
#     # Store the lists in a container (e.g., a list of lists)
#     lists_of_lists = []
#     # Create lists
#     for _ in range(sol_per_pop):
#         # list1 = generate_random_list(min(initial_list_of_multipliers ), max(initial_list_of_multipliers ), list_length)
#         list1= [0]* len(power_list)
#         lists_of_lists.append(list1)
#     return lists_of_lists

def initial_pop_reactors(power_list, sol_per_pop, possible_solutions):
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


def gene_upper_limit(power_list, demand): # limiting the maximum number of each type of reactors

    upper_limit_list = []
    for i in range(len(power_list )):
        # I use the multiplier 1.05 because of the ratio between refueling duration and operational lifetime is will nnot be higher than 1.05
        upper_limit =range(int(np.ceil(1.05*demand/power_list[i]))+2) ## TODO check the +1
        upper_limit_list.append(upper_limit )

    return  upper_limit_list



def on_gen(ga_instance):
    # pass
    print("Generation : ", ga_instance.generations_completed,  ga_instance.best_solution()[0], ga_instance.best_solution()[1])

def optimize_lcoe(power_list,  levelization_period_weeks, demand , interest_rate, capacity_factor_t_min_criteria):

    start_time = time.time()
    print('************************************ Starting Outer **********************************')

    # GA params
    sol_per_pop =  50 # 2*int(np.ceil((len(power_list))) )

    num_generations = 100 # 6000
    num_parents_mating =  20 #4 # consider increasing this
    num_genes = len(power_list)

    parent_selection_type = "rank"
    keep_parents =  10
    # crossover_type = "single_point"
    mutation_type = "adaptive"
    mutation_percent_genes  = (20, 1) #10
    # crossover_probability = mutation_probability = 0.9

    possible_solutions = gene_upper_limit(power_list, demand) # gene space
    # initial_pop  = initial_population_reactors(power_list ,sol_per_pop)
    initial_pop  = initial_pop_reactors(power_list ,sol_per_pop,possible_solutions)



    allow_dup  = True

    def fitness_eq(output_discrepancy):
        return -100 / (output_discrepancy) # Since I expect the minimum LCOE to approach 100, I so the discprepancy would be -100, I wanted the fintess to equal 1 if the LCOE = 100 is reached


    def fitness_func(ga_instance, solution, solution_idx):

        power_list_modified = [power_list [i] for i in range(len(solution)) if solution[i] != 0]

        Num_of_each_reactor_type_modified = [x for x in solution if x != 0]

        long_list_power = repeat_elements(power_list_modified, Num_of_each_reactor_type_modified)


        if sum(long_list_power) >= demand * capacity_factor_t_min_criteria  and sum(long_list_power) <=2*demand: #  ((sum(long_list_power)) - min(long_list_power) ) <= demand:



                capacity_factor_results =   capacity_factor_weeks_approach_mix_reactors(long_list_power  ,levelization_period_weeks, demand)
                MWh_generated_per_year_per_demand_list = capacity_factor_results[4]
                MWh_excess_per_year_list =     capacity_factor_results[5]
                Tot_OM__cost_per_year_list =  capacity_factor_results[6]

                capacity_factor_t_min = min(capacity_factor_results[1])

                output_lcoe = level_cost_of_energy_reactor_mix( interest_rate, power_list_modified, Num_of_each_reactor_type_modified,\
            MWh_generated_per_year_per_demand_list, MWh_excess_per_year_list, 0,\
                Tot_OM__cost_per_year_list)


                # if min_tot_P(power_list , solution, levelization_period_weeks) == expected_out :
                # fitness = 1 / ( np.abs(output - expected_out)  +1)

                fitness = fitness_eq(0 -  output_lcoe) # Here I assume the target is a very small number (zero$/MWh)

                if capacity_factor_t_min < capacity_factor_t_min_criteria: # Must satsify the criteria
                    fitness = -10000




                print("solution is : " , solution)
                print("Total Power is : " , sum(long_list_power))
                print("MW discrepancy : " , (demand - sum(long_list_power)))
                print("Capacity Factor (min): " , np.round(capacity_factor_t_min, 3))
                print("LCOE : " , np.round(output_lcoe, 3))



        else:
            fitness = -100000
        if fitness >=0:
            print("FITNESS NOW: ", fitness, "\n")
        return fitness

    ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating= num_parents_mating,
                       fitness_func= fitness_func,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,

                       parent_selection_type=parent_selection_type,
                       keep_parents=keep_parents, # crossover_type=crossover_type,

                       mutation_percent_genes= mutation_percent_genes,
                    #    crossover_probability=crossover_probability,
                    #    mutation_probability=mutation_probability,
                       gene_space= possible_solutions,
                       mutation_type=mutation_type, # stop_criteria= ["saturate_20"], #

                       on_generation= on_gen,
                       fitness_batch_size=1,
                       keep_elitism = int(sol_per_pop/5), # crossover_probability = 0.7,
                       gene_type = int,
                       initial_population = initial_pop,
                       save_solutions=True,
                       save_best_solutions=True,
                       parallel_processing = 1, # 8,



                       allow_duplicate_genes=allow_dup )



    ga_instance.run()

    end_time = time.time()
    fits = ga_instance.solutions_fitness
    # write fits to a csv file:
    np.savetxt('fitness_outer.csv', np.array(fits), delimiter=',')

    # plt.plot(fits)
    # plt.show()
    # ga_instance.plot_fitness()

    sol, sol_fitness, _ = ga_instance.best_solution()
    print("\n The optimization program runtime is " , np.round( (end_time -start_time), 0), " sec", " & The Number of Generations Passed is ",\
        ga_instance.generations_completed, "...... Fitness value of the best solution = {solution_fitness}".format(solution_fitness=sol_fitness))



    return sol







# In[ ]:


power_list = [1, 5, 10, 20, 50, 100, 200, 300, 400, 500, 1000] # we can decrease the number of solution if needed
capacity_factor_t_min_criteria_1 = 0.99 # we want to vary this to be 0.9, 0.95, 0.99, 0.999, 1

interest_rate = 0.06

Demand = 2000 # we want to change this to be 1000, 2000, 5000, 10000
# optimize_lcoe( [1000, 300,  50] ,  int(30*365/7), Demand, 0.06, capacity_factor_t_min_criteria_1)


# In[ ]:




