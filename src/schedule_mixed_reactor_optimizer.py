# from src import fuel_cycle_length, refueling_duration_estimate, calculate_duty_cycle_weeks_approach,\
#     levelization_period_weeks

import pygad
import numpy as np
import time
from parameters import fuel_cycle_length, refueling_duration_estimate, OM_cost_per_MWh
from schedule_similar_reactors import calculate_duty_cycle_weeks_approach




# When scheduling, we calculate the sum of the powers all reactors each timestep (week). The minimum of this sum is what we try to minimize

def min_tot_P(power_list , initial_delay_list, levelization_period_weeks): # operational_lifetime_delta_list, refueling_operation_delta_list
    """
    This function calculates the minimum total power output over a given time period,
    considering the initial delay, fuel cycle length, refueling duration, and power of each reactor.

    Parameters:
    power_list (list of float): A list of the power of each reactor.
    initial_delay_list (list of int): A list of the initial delay (in weeks) for each reactor.
    levelization_period_weeks (int): The total time period (in weeks) over which the calculation is performed.

    Returns:
    min_tot_P (float): The minimum total power output over the given time period.
    tt_list (list of int): A list of time (in weeks) after all the reactors are in service.
    P_t_list_of_lists (list of list of float): A list of lists, where each inner list represents the power output of each reactor at a specific time.
    max_initial_delay (int): The maximum initial delay (in weeks) among all the reactors.
    """
    
    P_t_list_tot  = []
    tt_list = []
    P_t_list_of_lists = []
    
    for tt in range( 1+int(max(initial_delay_list)), int(levelization_period_weeks) +1): # Going through the time (weeks) after all the reactors are in service
        tt_list.append(tt)
        P_t_list = []
       
        for i in range (len(power_list)):
            reactor_power = power_list[i]
            P_t = calculate_duty_cycle_weeks_approach(int(initial_delay_list[i]), int(levelization_period_weeks), reactor_power, int(tt))
            P_t_list.append(P_t)
            
        P_t_list_tot.append(sum(P_t_list))   
        P_t_list_of_lists.append(P_t_list) 
    min_tot_P = min(P_t_list_tot)
    return  min_tot_P, tt_list, P_t_list_of_lists, int((max(initial_delay_list)) )


def initial_population(power_list, sol_per_pop):
    """
    This function calculates an initial guess for the population of reactors.
    It assumes that all reactors have the same category (e.g. SMR) and that they have the same fuel cycle length.
    If this is not the case, the function will return an error.

    Parameters:
    - power_list (list): A list of the power levels for each reactor.
    - sol_per_pop (int): The number of solutions per population.

    Returns:
    - initial_population (list): A list of initial guesses for the population of reactors.
    - allow_duplicate (bool): A boolean indicating whether duplicate solutions are allowed.
    - expected_output (float): The expected output of the optimization process.

    The function first calculates the fuel lifetime-to-refueling ratio for the reactors with the highest and lowest power levels.
    If this ratio is greater than or equal to the number of reactors, the function assumes that all reactors have the same category and calculates an initial guess for the population based on this assumption.
    If the ratio is less than the number of reactors, the function assumes that the reactors have different categories and returns an error.

    The function then returns the initial guess for the population, along with a boolean indicating whether duplicate solutions are allowed and the expected output of the optimization process.
    """
    
    num_reactors = len(power_list)

    # calculating a good guess for the initial population
    # if all of them have the same category (e.g. smr):
    
    if fuel_cycle_length(max(power_list)) == fuel_cycle_length(min(power_list) ):
        refuel_period  = refueling_duration_estimate(max(power_list))
        fuel_lifetime_to_refueling_ratio = np.floor(fuel_cycle_length(max(power_list))/refuel_period )
        
        
        if int(fuel_lifetime_to_refueling_ratio)   >= num_reactors:
            the_max_delay = (num_reactors  - 1)* refuel_period
            num_intervals = int(np.ceil(the_max_delay/refuel_period)) +1
            initial_population_init = np.linspace(0, the_max_delay, num_intervals ).round().astype(int)
            initial_population_0 = initial_population_init
            allow_duplicate = False
            expected_output = sum(power_list) - max(power_list)
            
        elif int(fuel_lifetime_to_refueling_ratio)  <  num_reactors:   
            the_max_delay = fuel_cycle_length(max(power_list) ) 
            num_intervals = int(np.ceil(the_max_delay/refuel_period)) +1
            initial_population_init = np.linspace(0, the_max_delay, num_intervals ).round().astype(int)
            initial_population_0 = (np.hstack([initial_population_init]* int(np.ceil(num_reactors/len(initial_population_init))     )))[:num_reactors]
            allow_duplicate = True
            expected_output = sum(power_list) - (max(power_list)) * int(np.ceil(num_reactors/fuel_lifetime_to_refueling_ratio))

    # if they don't have the same category (mix of smr, micro, large reactors)
    elif fuel_cycle_length(max(power_list)) != fuel_cycle_length(min(power_list) ):
        the_max_delay = fuel_cycle_length(min(power_list) ) # minimum power means longer lifetime
        allow_duplicate = True # this is more complicated so I allow the duplication
        expected_output = sum(power_list) - max(power_list)
        initial_population_init = np.linspace(0, the_max_delay, num_reactors )


            
        initial_population_0 = (np.hstack([initial_population_init]* int(np.ceil(num_reactors/len(initial_population_init))     )))[:num_reactors]

            
            
             
    initial_population = [] 
    for i in range(sol_per_pop ) :
        initial_population.append(initial_population_0 )
    
    return initial_population, allow_duplicate, expected_output 


def on_gen(ga_instance):
    # pass
    print("Schedule Generation : ", ga_instance.generations_completed,  ga_instance.best_solution()[0], ga_instance.best_solution()[1])
    print(ga_instance.generations_completed, ga_instance.population)
    

def optimize_schedule(power_list,  levelization_period_weeks ): # Note that the power list here includes all the values of power (with repetition)
    
    start_time = time.time()
    
    # GA params
    sol_per_pop = int(2*len(power_list))   
    
    num_generations = 300
    num_parents_mating =  int(sol_per_pop/2)
    num_genes = len(power_list)
    # init_range_low = 0
    # init_range_high = 2

    parent_selection_type = "rank"
    keep_parents = int(sol_per_pop/2)
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

        fitness = fitness_eq(expected_out - output)
        
        if max(solution)>(365*5/7): # no delays after 4 years (I convert it to weeks because the timesteps are in weeks)
            fitness = -1 # reduced it from - 10000 to -1

        return fitness
    
    fitness_to_reach = "reach_" + str(fitness_eq(0)) # the target fitness
    
        
    ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_func= fitness_func,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       
                       parent_selection_type=parent_selection_type,
                       keep_parents=keep_parents,
                       crossover_type=crossover_type,
                       mutation_percent_genes= mutation_percent_genes,
                       
                       mutation_type=mutation_type,
                       stop_criteria= [fitness_to_reach , "saturate_5"], #  stopping criteria
                       on_generation= on_gen,
                        fitness_batch_size=1,
                        keep_elitism = int(sol_per_pop/5),
                        
                        gene_type = gene_type,
                       initial_population = initial_pop,
                       allow_duplicate_genes=allow_dup )
      
    
    
    ga_instance.run()
    end_time = time.time() 
    print(f"Nu of Gs passed is {ga_instance.generations_completed}")
    
    # ga_instance.plot_fitness()
    
    
    sol, sol_fitness, _ = ga_instance.best_solution()
    
    
    prediction = (min_tot_P(power_list , sol, levelization_period_weeks))[0]
    schedule_times = (min_tot_P(power_list , sol, levelization_period_weeks))[1]
    schedule_powers = (min_tot_P(power_list , sol, levelization_period_weeks))[2]
    schedule_rampup_duration = (min_tot_P(power_list , sol, levelization_period_weeks))[3]
    # discrepancy between the prediction and the output we were looking for
   
    prediction_discrepancy = np.abs(expected_out - prediction)      
    print(f"\n The difference between prediction and desired output is {prediction_discrepancy} : {expected_out} vs. {prediction} Total MW")
    print(f"\nIt takes {np.round(schedule_rampup_duration*7/365, 2)} years to startup up all the reactors")
    
    print("\n\n\n The schedule optimizatation ends")
    return schedule_times, schedule_powers, schedule_rampup_duration, sol


def capacity_factor_weeks_approach_mix_reactors(long_list_of_powers,levelization_period_weeks, demand):
    
    schedule = optimize_schedule(long_list_of_powers, levelization_period_weeks) 

    times =  schedule[0] # This is the time in weeks
    powers =  schedule[1]
    
    #OM Cost. Since it is per Mwh, I multiply it by the 168 hours per week (because the time is in weeks)
    # Cost ($/week)
    OM_costs = [[168*element* OM_cost_per_MWh(element, long_list_of_powers.count(element)) for element in row] for row in powers] # Multiply the cost ($/MWh) by the power (MW) by the number of hours in each timestep(week): 168 hours
    
    
    P_list_tot_array = (np.vstack(powers))
    OM_costs_array = (np.vstack(OM_costs))
   
    # sum powers of several reactors per day
    P_list_tot_array_sum = [0]* len(P_list_tot_array)
    for i in range(len(P_list_tot_array_sum )):
        P_list_tot_array_sum[i] = sum(P_list_tot_array[i])
        
    # sum costs of several reactors per week    
    OM_cost_list_tot_array_sum = [0]* len(OM_costs_array) 
    for i in range(len(OM_cost_list_tot_array_sum)):
        OM_cost_list_tot_array_sum[i] = sum(OM_costs_array[i] )
    
    
    #extract time and power after excluding the initial ramp up period
    times_array_excludingRampUp = times

    
    # nominal power and actual power
    tot_nom_output_t    =  demand # power per reactor * number of reactors (i.e. the total power)
    tot_actual_output_t =  P_list_tot_array_sum
    
    capacity_factor_t = np.array(tot_actual_output_t)/demand    

    tot_nom_output = tot_nom_output_t * (len(times_array_excludingRampUp)) # total power per day of all reactors multiplied by the number of days
    
    tot_actual_output_ttt = sum(tot_actual_output_t)
    
    overall_capacity_factor = tot_actual_output_ttt/tot_nom_output


    # time in years
    t_years = np.floor (np.array(times_array_excludingRampUp)/ 52.1785714286) + 1
    
    # make sure that you start at year (1) even when the reactors take more than a year to ramp up
    t_years_modified  = t_years - min(t_years) +1 # time in years
    
    # Use the output (tot_actual_output_t) to create a list of production and excess energy
    excess_energy =  [0] * (len(tot_actual_output_t))
    energy_produced_per_demand =  [0] * (len(tot_actual_output_t))
    tot_actual_output_t_mwh =  [0] * (len(tot_actual_output_t))
    
    for i in range(len(tot_actual_output_t)):
        if tot_actual_output_t[i] <= demand:
            excess_energy [i] = 0
            energy_produced_per_demand[i] = tot_actual_output_t[i] * 168 # hours per week
            tot_actual_output_t_mwh[i] = tot_actual_output_t[i] * 168 # hours per week
            
        elif tot_actual_output_t[i] > demand :
            excess_energy [i] =  (tot_actual_output_t[i] - demand) * 168
            energy_produced_per_demand[i] = demand * 168 # hours per week
            tot_actual_output_t_mwh[i] = tot_actual_output_t[i] * 168 # hours per week
    
    
    # tot yearly production 
    tot_yearly_production = {}
    
    # Iterate through the lists simultaneously
    for year, production_tot in zip(t_years_modified, tot_actual_output_t_mwh):
        if year in tot_yearly_production :
            # If the year is already in the dictionary, add the production value
            tot_yearly_production [year] += production_tot
        else:
            # If the year is not in the dictionary, initialize it with the production value
            tot_yearly_production [year] = production_tot

    #  yearly production per demand
    yearly_production_per_demand = {}
    
    # Iterate through the lists simultaneously
    for year, production in zip(t_years_modified, energy_produced_per_demand):
        if year in yearly_production_per_demand :
            # If the year is already in the dictionary, add the production value
            yearly_production_per_demand [year] += production
        else:
            # If the year is not in the dictionary, initialize it with the production value
            yearly_production_per_demand [year] = production

     
    # yearly excess energy
    yearly_excess_energy = {} 
    
    # Iterate through the lists simultaneously
    for year, excess in zip(t_years_modified, excess_energy):
        if year in yearly_excess_energy :
            # If the year is already in the dictionary, add the production value
            yearly_excess_energy [year] += excess
        else:
            # If the year is not in the dictionary, initialize it with the production value
            yearly_excess_energy [year] =excess   
    
    
    # yearly OM_cost (dollars)
    yearly_OM_cost = {} 
    
    # Iterate through the lists simultaneously
    for year, excess in zip(t_years_modified, OM_cost_list_tot_array_sum):
        if year in yearly_OM_cost  :
            # If the year is already in the dictionary, add the production value
            yearly_OM_cost  [year] += excess
        else:
            # If the year is not in the dictionary, initialize it with the production value
            yearly_OM_cost  [year] = excess
           
            
    MW_hours_generated_per_year_total = list(tot_yearly_production .values())
    MW_hours_generated_per_year_per_demand = list(yearly_production_per_demand.values())
    MW_hours_excess_per_year = list(yearly_excess_energy.values())
    yearly_OM_cost_list = list(yearly_OM_cost.values ())
    
    return times_array_excludingRampUp, capacity_factor_t, overall_capacity_factor, MW_hours_generated_per_year_total,\
        MW_hours_generated_per_year_per_demand , MW_hours_excess_per_year, yearly_OM_cost_list
                 
