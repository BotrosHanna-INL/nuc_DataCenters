import sys
import os
import numpy as np
import pygad
import matplotlib.pyplot as plt
import warnings
import time
import csv
import itertools
import random

warnings.filterwarnings('ignore')
from pathlib import Path
sys.path.insert(1, str( (Path().absolute())  ) + "/src")

from parameters import  repeat_elements, refueling_duration_estimate, fuel_cycle_length 
from schedule_mixed_reactor_optimizer import capacity_factor_weeks_approach_mix_reactors
from economic_FOMs import level_cost_of_energy_reactor_mix_starting_from_BOAK
from schedule_similar_reactors import num_reactors_needed_for_capacity_factor_weeks_apprioach




# delete the output file is exists
filename = "GA_results.csv"
try:
    os.remove(filename)
except OSError:
    pass


# def initial_pop_reactors(power_list, sol_per_pop, possible_solutions): # I got this from M. Abdo
#     """
#     This function initializes a population of potential solutions for the reactor mix optimization problem.

#     Parameters:
#     - power_list (list): A list of possible reactor capacities.
#     - sol_per_pop (int): The number of potential solutions per population.
#     - possible_solutions (list): A list of upper limits for each reactor capacity.

#     Returns:
#     - pop (list): A list of potential solutions, where each sub-list represents a solution and contains integers representing the number of each reactor type.
#     """
#     pop = np.zeros((sol_per_pop, len(power_list)))
#     for i in range(len(power_list)):
#         temp = np.random.randint(0, max(possible_solutions[i]) + 1, size=sol_per_pop).tolist()
#         pop[:, i] = temp
#     return pop.tolist()


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
        
   
    return list_of_expected_sols + expanded_list_with_changes


def gene_upper_limit(power_list, demand): # limiting the maximum number of each type of reactors

    upper_limit_list = []
    for i in range(len(power_list )):
        # I use the multiplier 1.05 because of the ratio between refueling duration and operational lifetime is will nnot be higher than 1.05
        num_R =int( num_reactors_needed_for_capacity_factor_weeks_apprioach(0, 1,power_list[i], int(40*365/7), demand))
        
        upper_limit =range(int(1 + num_R)) 
        #### WARNING: The 1.05 factor above might need to change if the refueling duration or interval have changed 
        upper_limit_list.append(upper_limit )

    
    return  upper_limit_list



def on_gen(ga_instance):
    # pass
    print("Generation : ", ga_instance.generations_completed,  ga_instance.best_solution()[0], ga_instance.best_solution()[1])


def optimize_lcoe(power_list,  levelization_period_weeks, demand , interest_rate, capacity_factor_t_min_criteria):
   
    start_time = time.time()
    
    
    # GA params
    sol_per_pop =   int(2* (len(power_list)))
    
    num_generations = 100
    num_parents_mating =  int(sol_per_pop /2) # int(np.ceil(sol_per_pop/3))# consider increasing this
    num_genes = len(power_list)

    parent_selection_type = "rank"
    keep_parents = 0# int(np.ceil(sol_per_pop/5))
    
    mutation_type = "None"
    # mutation_percent_genes = 5
    
    crossover_type = "single_point"
    # mutation_type = "adaptive"
    # mutation_percent_genes =  mutation_percent_genes = (20, 1) #10
    
    possible_solutions = gene_upper_limit(power_list, demand) # gene space
    initial_pop  = initial_pop_reactors_2(power_list,  possible_solutions, sol_per_pop)
    
    allow_dup  = True
    
    

    def fitness_eq(output_discrepancy):
        return -100 / (output_discrepancy) # Since I expect the minimum LCOE to approach 100, I so the discprepancy would be -100, I wanted the fintess to equal 1 if the LCOE = 100 is reached
        
    
    def fitness_func(ga_instance, solution, solution_idx):
        print("\n\n proposed solution", solution)
       
        power_list_modified = [power_list [i] for i in range(len(solution)) if solution[i] != 0]
      
        Num_of_each_reactor_type_modified = [x for x in solution if x != 0]
      
        long_list_power = repeat_elements(power_list_modified, Num_of_each_reactor_type_modified)
       
        
        if sum(long_list_power) >= demand * capacity_factor_t_min_criteria and  sum(long_list_power) <= 2*demand : #  ((sum(long_list_power)) - min(long_list_power) ) <= demand:
            
            
        
                capacity_factor_results =   capacity_factor_weeks_approach_mix_reactors(long_list_power  ,levelization_period_weeks, demand)
                MWh_generated_per_year_per_demand_list = capacity_factor_results[4]
                MWh_excess_per_year_list =     capacity_factor_results[5]
                Tot_OM__cost_per_year_list =  capacity_factor_results[6]
                
                capacity_factor_t_min = min(capacity_factor_results[1])
               
                output_lcoe = level_cost_of_energy_reactor_mix_starting_from_BOAK( interest_rate, power_list_modified, Num_of_each_reactor_type_modified,\
            MWh_generated_per_year_per_demand_list, MWh_excess_per_year_list, 0,\
                Tot_OM__cost_per_year_list)

            
                fitness_1 = fitness_eq(0 -  output_lcoe) # Here I assume the target is a very small number (zero$/MWh)
                
                if capacity_factor_t_min >=capacity_factor_t_min_criteria: # Must satsify the criteria
                    fitness_2 = 0
                elif capacity_factor_t_min < capacity_factor_t_min_criteria: 
                    fitness_2 = - 2*(capacity_factor_t_min_criteria - capacity_factor_t_min)
                fitness = fitness_1 + fitness_2
                GA_results =  { 'sol_0' :solution[0] , 'sol_1' :solution[1], 'sol_2' :solution[2], 'fitness':fitness, 'CF': capacity_factor_t_min }
            
                with open("GA_results.csv", "a") as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in GA_results.items():
                        writer.writerow([key, value])
         
                
                # print("solution is : " , solution)
                # print("Total Power is : " , sum(long_list_power))
                # print("MW discrepancy : " , np.abs(demand - sum(long_list_power)))
                # print("Capacity Factor (min): " , np.round(capacity_factor_t_min, 3))
                # print("LCOE : " , np.round(output_lcoe, 3))
                
        else:
            fitness = -1
        # if fitness >=0:    
        # print( "FITNESS NOW: ", fitness, "\n")
        
        

        return fitness
            
    ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating= num_parents_mating,
                       fitness_func= fitness_func,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                     
                       parent_selection_type=parent_selection_type,
                       keep_parents=keep_parents, crossover_type=crossover_type,
                       
                    #    mutation_percent_genes= mutation_percent_genes,
                       
                       # pick 'possible_solutions' if you want to give more freedom,  or 'solutions_P_list' if you want to be faster.
                       gene_space=  possible_solutions ,
                       #mutation_type=mutation_type, 
                       stop_criteria= ["saturate_20"], 
                      
                       on_generation= on_gen,
                        fitness_batch_size=1,
                        keep_elitism = int(sol_per_pop/5),
                        gene_type = int, initial_population = initial_pop,
                    
                    
                    
                       allow_duplicate_genes=allow_dup )
      
    
 
    ga_instance.run()
  
    end_time = time.time() 
    
    
    sol, sol_fitness, _ = ga_instance.best_solution()
    print("\n The optimization program runtime is " , np.round( (end_time -start_time), 0), " sec", " & The Number of Generations Passed is ",\
        ga_instance.generations_completed, "...... Fitness value of the best solution = {solution_fitness}".format(solution_fitness=sol_fitness)) 



    
    return sol





power_list = [1000, 300 ,10] # we can decrease the number of solution if needed
capacity_factor_t_min_criteria_1 = 0.99 # we want to vary this to be 0.9, 0.95, 0.99, 0.999, 1 

interest_rate = 0.06

Demand = 1500 # we want to change this to be 1000, 2000, 5000, 10000 
optimize_lcoe( power_list ,  int(40*365/7), Demand, 0.06, capacity_factor_t_min_criteria_1)  