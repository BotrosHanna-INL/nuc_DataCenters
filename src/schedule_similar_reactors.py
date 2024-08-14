import numpy as np
from parameters import fuel_cycle_length, refueling_duration_estimate

# calculate the start and end of the fuel cycle of each reactor depening on the delay of the start of each reactor
def reactor_on_durations_weeks_approach(delay_in_weeks, fuel_lifetime_weeks, refuel_period_weeks, levelization_period_weeks ):
    # Calculate the begining and the end of each fuel cycle start (in weeks)
    fuel_cycle_start_weeks = delay_in_weeks+1  # initizalition (in weeks). We start at week #1 not week (#0)
    cycle_num = 0
    fuel_cycle_start_weeks_list = []
    fuel_cycle_end_weeks_list = []
    
    while (fuel_cycle_start_weeks ) <= levelization_period_weeks:

        fuel_cycle_start_weeks = delay_in_weeks + cycle_num*(fuel_lifetime_weeks+refuel_period_weeks) +1
        fuel_cycle_end_weeks = fuel_cycle_start_weeks+ fuel_lifetime_weeks -1
        cycle_num = cycle_num +1
        
        if fuel_cycle_start_weeks<= levelization_period_weeks:
            fuel_cycle_start_weeks_list.append(fuel_cycle_start_weeks)
            fuel_cycle_end_weeks_list.append(fuel_cycle_end_weeks )
    
    if fuel_cycle_end_weeks_list[-1 ] > levelization_period_weeks: 
        fuel_cycle_end_weeks_list[-1 ]= levelization_period_weeks
    
    return fuel_cycle_start_weeks_list, fuel_cycle_end_weeks_list



# calculate the power of the reactor at each timestep (depending on whether the reactor is running or down)

def calculate_duty_cycle_weeks_approach(inital_delay_in_weeks, levelization_period_weeks, power, t_weeks):
    fuel_lifetime_weeks = fuel_cycle_length(power)
    refuel_period_weeks = refueling_duration_estimate(power)
    
    fuel_cycle_durations_weeks = reactor_on_durations_weeks_approach(inital_delay_in_weeks, fuel_lifetime_weeks,  refuel_period_weeks, levelization_period_weeks)
    fuel_cycle_start_weeks = fuel_cycle_durations_weeks[0]
    fuel_cycle_end_weeks = fuel_cycle_durations_weeks[-1]
    
    # initialize
    power_dict  = {}
    if t_weeks in range(levelization_period_weeks+1):
        
        power_dict[t_weeks] = 0
        

    for n in range(len(fuel_cycle_start_weeks )):
        start_time_weeks = fuel_cycle_start_weeks[n]
        
        end_time_weeks = fuel_cycle_end_weeks [n]
        
        if t_weeks in range(start_time_weeks, end_time_weeks +1):
            power_dict[t_weeks] = power
    
    return power_dict[t_weeks]   



# calculate the power of muliple reactors at each timestep (depending on whether the reactor is running or down)

def calculate_schedule_multiple_reactors_weeks_approach(num_reactors, power, levelization_period_weeks):
    
    fuel_lifetime_weeks = fuel_cycle_length(power)
    refueling_period_weeks = refueling_duration_estimate(power)
    
    if num_reactors <= (fuel_lifetime_weeks/refueling_period_weeks):
        initial_delay_list =list(refueling_period_weeks*np.linspace(0,  num_reactors-1, num_reactors) )
        P_list_tot = []
        for i in range(len(initial_delay_list)):
            
            delay = initial_delay_list[i] 
            
            t_list = []
            P_list = []

            for time in range(1, levelization_period_weeks+1): # we start with week#1 not week #0
            
                P = calculate_duty_cycle_weeks_approach( int( delay), levelization_period_weeks, power, time)
                t_list.append(time)
                P_list.append(P)

            P_list_tot.append(P_list)
    elif num_reactors > (fuel_lifetime_weeks/refueling_period_weeks):
        
        num_reactors_down_max = int(np.ceil(num_reactors * refueling_period_weeks/fuel_lifetime_weeks))
        num_reactors_down_min = int(np.floor(num_reactors * refueling_period_weeks/fuel_lifetime_weeks))

        # how many times the celing value is used
        num_reactors_down_max_freq = int(np.ceil((num_reactors * refueling_period_weeks)% fuel_lifetime_weeks)/refueling_period_weeks) 
        num_reactors_down_min_freq = int(fuel_lifetime_weeks /refueling_period_weeks)- num_reactors_down_max_freq



        reactor_down_list1 = [num_reactors_down_max ]*num_reactors_down_max_freq
        reactor_down_list2 = [num_reactors_down_min ]*num_reactors_down_min_freq
        reactor_down_list = reactor_down_list1  + reactor_down_list2

        assert len(reactor_down_list  ) == int(fuel_lifetime_weeks/refueling_period_weeks) , "There is an assertion error. review!"

        initial_delay_list = []
        for n in np.linspace(0,  int(fuel_lifetime_weeks/refueling_period_weeks )-1, int(fuel_lifetime_weeks/refueling_period_weeks )):

            delay_list = [n*refueling_period_weeks] * reactor_down_list [int(n)]
            initial_delay_list.append(delay_list )
        initial_delay_list = list(np.hstack(initial_delay_list))


        P_list_tot = []
        for i in range(len(initial_delay_list)):
            
            delay = initial_delay_list[i] 
            
            t_list = []
            P_list = []

            for time in range(1, levelization_period_weeks+1):  #we start with week#1 not week #0
            
                P = calculate_duty_cycle_weeks_approach( int( delay), levelization_period_weeks, power, time)
            
                t_list.append(time)
                P_list.append(P)

            P_list_tot.append(P_list)
    
    fullPower_duration = initial_delay_list[-1]
    
    return  t_list,  P_list_tot, fullPower_duration 



# calculate the capacity factor of muliple reactors at each timestep (depending on whether the reactor is running or down)
def capacity_factor_weeks_approach(num_reactors, power1,levelization_period_weeks, demand):
        
    schedule = calculate_schedule_multiple_reactors_weeks_approach(num_reactors, power1, levelization_period_weeks) 

    times =  schedule[0] # This is the time in weeks
    powers =  schedule[1]
    
    P_list_tot_array = (np.vstack(powers))
    
    # # remove the data before getting to the full power
    times_array =np.reshape(np.array(times) , (1, len(times)))
    times_power_array = np.concatenate((times_array , P_list_tot_array)) # merging the time and power in one array
    times_power_array_excludingRampUp = times_power_array[:,int(schedule[2]):] # remove the initial rampup period

    #extract time and power after excluding the initial ramp up period
    times_array_excludingRampUp = times_power_array_excludingRampUp[0]
    power_array_excludingRampUp = np.delete(times_power_array_excludingRampUp, (0), axis=0)
    
    # nominal power and actual power
    tot_nom_output_t    = demand # power per reactor * number of reactors (i.e. the total power)
    tot_actual_output_t =  sum(power_array_excludingRampUp)
    capacity_factor_t = tot_actual_output_t/tot_nom_output_t 

    

    tot_nom_output = tot_nom_output_t * (len(times_array_excludingRampUp)) # total power per day of all reactors multiplied by the number of days
    
    tot_actual_output_ttt = sum(tot_actual_output_t)
    
    overall_capacity_factor = tot_actual_output_ttt/tot_nom_output


    # time in years
    t_years = np.floor (times_array_excludingRampUp/ 52.1785714286) + 1
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
    
    
           
            
    MW_hours_generated_per_year_total = list(tot_yearly_production .values())
    MW_hours_generated_per_year_per_demand = list(yearly_production_per_demand.values())
    MW_hours_excess_per_year = list(yearly_excess_energy.values())
    return times_array_excludingRampUp, capacity_factor_t, overall_capacity_factor,\
        MW_hours_generated_per_year_total, MW_hours_generated_per_year_per_demand, MW_hours_excess_per_year
  
  
# calculate the number of reactors needed to reach a specific capacity factor of muliple reactors at each timestep (depending on whether the reactor is running or down)
                 
def num_reactors_needed_for_capacity_factor_weeks_apprioach(overall_capacity_factor_criteria, min_capacity_factor_criteria,\
     power, levelization_period_weeks, demand_0):
    fuel_lifetime_weeks = fuel_cycle_length(power)
    refueling_period_weeks = refueling_duration_estimate(power)

    refueling_to_fuel_cycle_ratio =  refueling_period_weeks/fuel_lifetime_weeks
    maximum_criteria = max(overall_capacity_factor_criteria, min_capacity_factor_criteria)
    approximate_capacity_factor = 1 -refueling_to_fuel_cycle_ratio
    
    # initialize the number of reactors to satisfy the capacity factor
    num_reactors_0 =  max (1, int(np.floor(( np.ceil( demand_0 /power))*maximum_criteria/approximate_capacity_factor)) - 1) # I subtract 1 because I want at least 2 ietration before getting to the solution

    for  num_reactors in np.linspace( num_reactors_0 , 5*num_reactors_0, 4*num_reactors_0+1):
        
        capacity_factor_results = (capacity_factor_weeks_approach(int(num_reactors), power, levelization_period_weeks, demand_0 ))

        # times_array_excludingRampUp = capacity_factor_results[0]
        capacity_factor_min =    min (capacity_factor_results[1])
        overall_capacity_factor   =   capacity_factor_results[2]
        if  overall_capacity_factor>=  overall_capacity_factor_criteria:
            if capacity_factor_min >= min_capacity_factor_criteria:
                num_reactors_final = num_reactors
                break

    return num_reactors_final 
# import time
# start =time.time()
# print(num_reactors_needed_for_capacity_factor_weeks_apprioach(0, 1, 1 ,int (40*365/7), 1000))          
# end =time.time()
# duration = (end -start)
# print(f"{int(duration)} seconds")
