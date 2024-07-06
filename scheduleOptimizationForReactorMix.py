from src import operational_lifetime_estimate, refueling_period_estimate, calculate_duty_cycle_weeks_approach,\
    levelization_period_weeks

import pygad
import numpy as np
import time

def min_tot_P(power_list , initial_delay_list, levelization_period_weeks): # operational_lifetime_delta_list, refueling_operation_delta_list
   
    # operational_lifetime_delta_list is the change of the operational lifetime to minimize the chance of refueling several reactors at the same time
    # This delta is less than or equal to 4 weeks
    # refueling_operation_delta_list is the delay of refueling to avoid 
    P_t_list_tot  = []
    tt_list = []
    P_t_list_of_lists = []
    
    for tt in range( 1+int(max(initial_delay_list)), int(levelization_period_weeks) +1): # Going through the time (weeks)
        tt_list.append(tt)
        P_t_list = []
        for i in range (len(power_list)):
            reactor_power = power_list[i]
            fuel_lifetime_weeks = operational_lifetime_estimate(reactor_power)  # - int(operational_lifetime_delta_list[i])
            refuel_period_weeks = refueling_period_estimate(reactor_power)  #+ int(refueling_operation_delta_list[i])
            P_t = calculate_duty_cycle_weeks_approach(int(initial_delay_list[i]), int(fuel_lifetime_weeks), int(refuel_period_weeks),\
                int(levelization_period_weeks), reactor_power, int(tt))
            P_t_list.append(P_t)
            
        P_t_list_tot.append(sum(P_t_list))   
        P_t_list_of_lists.append(P_t_list) 
    min_tot_P = min(P_t_list_tot)
    return  min_tot_P, tt_list, P_t_list_of_lists, int((max(initial_delay_list)) )






def initial_population(power_list, sol_per_pop):
    num_reactors = len(power_list)

    # calculating a good guess foe the initial population
    # if all of them have the same category (e.g. smr):
    if operational_lifetime_estimate(max(power_list)) == operational_lifetime_estimate(min(power_list) ):
        refuel_period  = refueling_period_estimate(max(power_list))
        fuel_lifetime_to_refueling_ratio = np.floor(operational_lifetime_estimate(max(power_list))/refuel_period )
        
        
        if int(fuel_lifetime_to_refueling_ratio)   >= num_reactors:
            the_max_delay = (num_reactors  - 1)* refuel_period
            num_intervals = int(np.ceil(the_max_delay/refuel_period)) +1
            initial_population_init = np.linspace(0, the_max_delay, num_intervals )
            initial_population_0 = initial_population_init
            allow_duplicate = False
            expected_output = sum(power_list) - max(power_list)
            
        elif int(fuel_lifetime_to_refueling_ratio)  <  num_reactors:   
            the_max_delay = operational_lifetime_estimate(max(power_list) ) 
            num_intervals = int(np.ceil(the_max_delay/refuel_period)) +1
            initial_population_init = np.linspace(0, the_max_delay, num_intervals )
            initial_population_0 = (np.hstack([initial_population_init]* int(np.ceil(num_reactors/len(initial_population_init))     )))[:num_reactors]
            allow_duplicate = True
            expected_output = sum(power_list) - (max(power_list)) * int(np.ceil(num_reactors/fuel_lifetime_to_refueling_ratio))

    # if they don't have the same category (mix of smr, micro, large reactors)
    elif operational_lifetime_estimate(max(power_list)) != operational_lifetime_estimate(min(power_list) ):
        the_max_delay = operational_lifetime_estimate(min(power_list) ) # minimum power means longer lifetime
        allow_duplicate = True # this is more complicated so I allow the duplication
        expected_output = sum(power_list) - max(power_list)
        initial_population_init = np.linspace(0, the_max_delay, num_reactors )
        # refuel_period  = refueling_period_estimate(np.mean(power_list)) # this is just a guess (initialization)
        # fuel_lifetime_to_refueling_ratio = np.floor(operational_lifetime_estimate(np.mean(power_list))/refuel_period ) # max power means low fuel lifetime
        
        # # This leads to low lifetime to refueling period ratio

        # if int(fuel_lifetime_to_refueling_ratio)   >= num_reactors:
        #     the_max_delay = (num_reactors  - 1)* refuel_period
        #     num_intervals = int(np.ceil(the_max_delay/refuel_period)) +1
        #     initial_population_init = np.linspace(0, the_max_delay, num_intervals )
        #     initial_population_0 = initial_population_init
        #     allow_duplicate = True # this is more complicated so I allow the duplication
        #     expected_output = sum(power_list) - max(power_list)
        
        # elif int(fuel_lifetime_to_refueling_ratio)  <  num_reactors:   
        #     the_max_delay = operational_lifetime_estimate(max(power_list) ) 
        #     num_intervals = int(np.ceil(the_max_delay/refuel_period)) +1
            
        initial_population_0 = (np.hstack([initial_population_init]* int(np.ceil(num_reactors/len(initial_population_init))     )))[:num_reactors]
        #     allow_duplicate = True
        #     power_list_sorted = sorted(power_list, reverse=True)
            
            
            
            
        # expected_output = sum(power_list) - sum(power_list_sorted[: int(np.ceil(num_reactors/fuel_lifetime_to_refueling_ratio))] )
 
    # initial_population_0 = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18] 
    initial_population = [] 
    for i in range(sol_per_pop ) :
        initial_population.append(initial_population_0 )

    return initial_population, allow_duplicate, expected_output 


def on_gen(ga_instance):
    pass
    # print("Generation : ", ga_instance.generations_completed,  ga_instance.best_solution()[0], ga_instance.best_solution()[1])
    # print(ga_instance.generations_completed, ga_instance.population)
    

def optimize_schedule(power_list,  levelization_period_weeks ):
    
    start_time = time.time()
    
    # GA params
    sol_per_pop = int(2*len(power_list))   
    
    

    num_generations = 300
    num_parents_mating =  max( 3, int(sol_per_pop/3))
    num_genes = len(power_list)
    init_range_low = 0
    init_range_high = 2

    parent_selection_type = "rank"
    keep_parents =  max(3, int(sol_per_pop/3))
    gene_type= int
    crossover_type = "single_point"

    mutation_type = "random"
    mutation_percent_genes = 10
    
    initial_pop  = (initial_population(power_list, sol_per_pop))[0]
    allow_dup  = (initial_population(power_list, sol_per_pop))[1]
    expected_out  = (initial_population(power_list, sol_per_pop))[2]
    
    def fitness_eq(output_discrepancy):
        return 1 / ( np.abs(output_discrepancy)  +1) 
        
    
    def fitness_func(ga_instance, solution, solution_idx):
        output = (min_tot_P(power_list , solution, levelization_period_weeks))[0]

        
        # if min_tot_P(power_list , solution, levelization_period_weeks) == expected_out :
        # fitness = 1 / ( np.abs(output - expected_out)  +1)
        fitness = fitness_eq(expected_out - output)
        if max(solution)>(365*4/7): # no delays after 4 years
            fitness = -10000
        # fitness = 100* ( 1  -  ( (expected_out - output)/expected_out))
        #     fitness = 1 / ( np.abs(output - sum(power_list)) +0.01) 
            
        
        return fitness
    
    fitness_to_reach = "reach_" + str(fitness_eq(0))
        
    ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_func= fitness_func,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       init_range_low=init_range_low,
                       init_range_high=init_range_high,
                       parent_selection_type=parent_selection_type,
                       keep_parents=keep_parents,
                       crossover_type=crossover_type,
                       mutation_percent_genes= mutation_percent_genes,
                       
                       mutation_type=mutation_type,
                       stop_criteria= [fitness_to_reach , "saturate_20"], # 
                       on_generation= on_gen,
                        fitness_batch_size=1,
                        keep_elitism = int(sol_per_pop/5),
                        crossover_probability = 0.7,
                        gene_type = gene_type,
                    
                       initial_population = initial_pop,
                       allow_duplicate_genes=allow_dup )
      
    
    
    ga_instance.run()
    end_time = time.time() 
    # print(f"Number of generations passed is {ga_instance.generations_completed}")
    
    ga_instance.plot_fitness()
    
    sol, sol_fitness, _ = ga_instance.best_solution()
    print("\n The program runtime is " , np.round( (end_time -start_time), 0), " sec", " & The Number of Generations Passed is ",\
        ga_instance.generations_completed, "...... Fitness value of the best solution = {solution_fitness}".format(solution_fitness=sol_fitness)) 

    # print("Parameters of the best solution : {solution}".format(solution=solution))
    # print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=sol_fitness))
    
    prediction = (min_tot_P(power_list , sol, levelization_period_weeks))[0]
    schedule_times = (min_tot_P(power_list , sol, levelization_period_weeks))[1]
    schedule_powers = (min_tot_P(power_list , sol, levelization_period_weeks))[2]
    schedule_rampup_duration = (min_tot_P(power_list , sol, levelization_period_weeks))[3]
    # discrepancy between the prediction and the output we were looking for
    prediction_discrepancy = np.round(100*(abs(expected_out - prediction))/expected_out ,2)
    print(f"\n The difference between prediction and desired output is {prediction_discrepancy} %: {expected_out} vs. {prediction} Total MW")
    print(f"\nIt takes {np.round(schedule_rampup_duration*7/365, 2)} years to startup up all the reactors \n")
    
    
    return schedule_times, schedule_powers, schedule_rampup_duration  




optimize_schedule([ 20, 1 , 1 , 1, 20, 500, 1, 1, 5, 5, 10, 30, 50],  520 )
# 
# optimize_schedule([ 20, 1 , 1 , 1, 20, 500, 1, 1, 5, 5, 10, 30, 50, 50],  2*520 )

# optimize_schedule([ 20, 1 , 1 , 1, 20, 500, 1, 1, 5, 5, 10, 30, 50, 50, 200],  2*520 )

# a =  [1] * 1000
# optimize_schedule(a,  2*520 )







 
   
 
                   



















   
   
   

    
          




    


  











    
    


