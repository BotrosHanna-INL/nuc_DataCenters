import numpy as np




# def sample_cost(demand, P_info, LR_info, FOAK_cost_info ):
    
#     P_min, P_max, P_interval = P_info
#     LR_min, LR_max, LR_interval = LR_info
#     min_ratio, max_ratio, cost_interval = FOAK_cost_info
    
#     # #save data
#     LR_list = []
#     power_list = []
#     initial_cost_SR_list = []
#     SR_reduced_cost_list = []

#     num_P = int(np.ceil( 1 +  (P_max - P_min)/ P_interval ))  #num of power samples
#     num_LR = int(np.ceil(1 + (LR_max - LR_min)/ LR_interval ) )  #num of learning rate samples
#     num_cost = int(np.ceil(1 + (max_ratio - min_ratio)/  cost_interval ) )  #num of cost ratio samples
  

#     for P in  np.linspace(P_min , P_max ,num_P) :# between 50 and 300 MW for one SR 
        
#         #number of SR required to get to the target demand
#         num_reactors =int( np.ceil(demand /P))  # it has to be the ceiling

#         for lr in np.linspace(LR_min , LR_max ,num_LR): # iterate through learning rate
            
#             cost_reduction_sum = 0 # initizalition
            
#             for nn in range(1, num_reactors +1):# cost decreases from NOAK to FOAK and averaged over the number of reactors built
#                 cost_reduction_sum += ( (1 - lr) **(np.log2(nn)))
#             cost_reduction_factor = cost_reduction_sum/num_reactors
                
#             #cost of each reactor
#             for cost in np.linspace(min_ratio , max_ratio ,num_cost):
                
#                 # cost reduction due to Learning rate
#                 SR_reduced_cost =   cost *  cost_reduction_factor   
                
                
#                 LR_list.append(lr)
#                 power_list.append(P)
#                 initial_cost_SR_list.append(cost)
#                 SR_reduced_cost_list.append(SR_reduced_cost)
#     full_results = np.vstack((np.array(power_list), np.array(LR_list) ,np.array(initial_cost_SR_list), np.array(SR_reduced_cost_list)))
#     full_results = full_results.T
    
#     reduced_cost_tol  = np.median(abs(np.diff(full_results[:,3]))) # because of sampling, we may not exact cost we want, there is a tolerance
#     return full_results,  reduced_cost_tol





# def calculate_tipping_learning_rate(LR_info, demand, power , ref_large_reactor_power, init_cost_ratio, n_exponent, method ):
#     [lr_min, lr_max,  lr_interval] = LR_info
#     num_LR = int(np.ceil(1 + (lr_max - lr_min)/ lr_interval ) )  #num of learning rate samples
    
#     num_reactors =int( np.ceil(demand /power))  # it has to be the ceiling
    
#     SR_reduced_cost_save = []
#     lr_save = []
    
#     if method == "free cost ratios":
        

#         for lr in np.linspace(lr_min ,lr_max ,num_LR): 
#             lr_save.append(lr)
#             cost_reduction_sum = 0 # initizalition 
                    
#             for nn in range(1, num_reactors +1):# cost decreases from NOAK to FOAK and averaged over the number of reactors built
#                 cost_reduction_sum += ( (1 - lr) **(np.log2(nn)))
#             cost_reduction_factor = cost_reduction_sum/num_reactors
#             SR_reduced_cost =   init_cost_ratio *  cost_reduction_factor 
#             SR_reduced_cost_save.append(SR_reduced_cost)
#             LR_tipping_point = "Not Found" # if the tipping point is not found_
#             if SR_reduced_cost < 1:
#                 LR_tipping_point = lr_save[-2]
#                 break
        
#         return LR_tipping_point     
            
    
#     if method == "logarithmic curve":
        
#         initial_cost_ratio = (power/ref_large_reactor_power)**(n_exponent-1)
        
#         for lr in np.linspace(lr_min ,lr_max ,num_LR): 
#             lr_save.append(lr)
#             cost_reduction_sum = 0 # initizalition           
#             for nn in range(1, num_reactors +1):# cost decreases from NOAK to FOAK and averaged over the number of reactors built
#                 cost_reduction_sum += ( (1 - lr) **(np.log2(nn)))
#             cost_reduction_factor = cost_reduction_sum/num_reactors
#             SR_reduced_cost =   initial_cost_ratio  *  cost_reduction_factor 
#             SR_reduced_cost_save.append(SR_reduced_cost)
           
#             LR_tipping_point = "Not Found" # if the tipping point is not found_
            
#             if SR_reduced_cost < 1:
#                 LR_tipping_point = lr_save[-2]
               
#                 break
#         return LR_tipping_point, initial_cost_ratio     
    
    



# def calculate_tipping_cost(lr, FOAK_cost_info, demand, power ):

# #     min_ratio, max_ratio, cost_interval = FOAK_cost_info
# #     num_cost = int(np.ceil(1 + abs(max_ratio - min_ratio)/  cost_interval ) )  #num of cost ratio samples
    

# #     FOAK_cost_save =[]
    
# #     for init_cost in np.linspace(min_ratio , max_ratio ,num_cost):
        
# #         SR_reduced_cost =   init_cost *  cost_reduction_factor
# #         FOAK_cost_save.append(init_cost)
# #         cost_tipping_point = "Not Found" 
# #         if SR_reduced_cost < 1:
# #             cost_tipping_point = FOAK_cost_save[-2]
# #             break
# #     return cost_tipping_point     






def calculate_final_cost_due_to_learning_rate(initial_cost_usd_per_kw, learning_rate, num_reactors ):
    cost_reduction_sum = 0 # initizalition 
    
    for nn in range(1, num_reactors +1):# cost decreases from NOAK to FOAK and averaged over the number of reactors built
        cost_reduction_sum += ( (1 - learning_rate) **(np.log2(nn)))
    cost_reduction_factor = cost_reduction_sum/num_reactors   
    reduced_cost_used_kw =   initial_cost_usd_per_kw *  cost_reduction_factor


    return reduced_cost_used_kw
 

def reactor_on_durations(delay, fuel_lifetime, refuel_period, levelization ):

    fuel_cycle_start = delay # initizalition
    cycle_num = 0
    fuel_cycle_start_list = []
    fuel_cycle_end_list = []
    
    while (fuel_cycle_start - delay) < levelization:

        fuel_cycle_start = delay +cycle_num*(fuel_lifetime+refuel_period)
        fuel_cycle_end = fuel_cycle_start+ fuel_lifetime
        cycle_num = cycle_num +1
        
        if fuel_cycle_start< levelization:
            fuel_cycle_start_list.append(fuel_cycle_start)
            fuel_cycle_end_list.append(fuel_cycle_end )
    
    if fuel_cycle_end_list[-1 ] > levelization: 
        fuel_cycle_end_list[-1 ]= levelization
    
    return fuel_cycle_start_list, fuel_cycle_end_list     
        


 
def calculate_duty_cycle(inital_delay, fuel_lifetime, refuel_period, levelization, power, t):
    
    fuel_cycle_durations = reactor_on_durations(inital_delay, fuel_lifetime,  refuel_period, levelization )
    fuel_cycle_start = fuel_cycle_durations[0]
    fuel_cycle_end = fuel_cycle_durations[-1]

    
    # initialize
    power_dict  = {}
    if t in range(levelization+1):
        
        power_dict[t] = 0
        

    for n in range(len(fuel_cycle_start )):
        start_time = fuel_cycle_start[n]
        
        end_time = fuel_cycle_end [n]

        if t in range(start_time, end_time +1):
            power_dict[t] = power
    

    return power_dict[t]        





def calculate_schedule_multiple_reactors(fuel_lifetime, refueling_period, num_reactors, power, levelization_period):
    
    if num_reactors <= (fuel_lifetime/refueling_period):
        initial_delay_list =list(refueling_period*np.linspace(0,  num_reactors-1, num_reactors) )
        P_list_tot = []
        for i in range(len(initial_delay_list)):
            
            delay = initial_delay_list[i] 
            
            t_list = []
            P_list = []

            for time in range(levelization_period+1):
            
                P = calculate_duty_cycle( int( delay), fuel_lifetime, refueling_period, levelization_period, power, time)
            
                t_list.append(time)
                P_list.append(P)

            P_list_tot.append(P_list)
    elif num_reactors > (fuel_lifetime/refueling_period):
        
        num_reactors_down_max = int(np.ceil(num_reactors * refueling_period/fuel_lifetime))
        num_reactors_down_min = int(np.floor(num_reactors * refueling_period/fuel_lifetime))

        # how many times the celing value is used
        num_reactors_down_max_freq = int(np.ceil((num_reactors * refueling_period )% fuel_lifetime)/refueling_period) 
        num_reactors_down_min_freq = int(fuel_lifetime /refueling_period)- num_reactors_down_max_freq

        reactor_down_list1 = [num_reactors_down_max ]*num_reactors_down_max_freq
        reactor_down_list2 = [num_reactors_down_min ]*num_reactors_down_min_freq
        reactor_down_list = reactor_down_list1  + reactor_down_list2

        assert len(reactor_down_list  ) == int(fuel_lifetime/refueling_period ) , "There is an assertion error. review!"

        initial_delay_list = []
        for n in np.linspace(0,  int(fuel_lifetime/refueling_period )-1, int(fuel_lifetime/refueling_period )):

            delay_list = [n*refueling_period] * reactor_down_list [int(n)]
            initial_delay_list.append(delay_list )
        initial_delay_list = list(np.hstack(initial_delay_list))


        P_list_tot = []
        for i in range(len(initial_delay_list)):
            
            delay = initial_delay_list[i] 
            
            t_list = []
            P_list = []

            for time in range(levelization_period+1):
            
                P = calculate_duty_cycle( int( delay), fuel_lifetime, refueling_period, levelization_period, power, time)
            
                t_list.append(time)
                P_list.append(P)

            P_list_tot.append(P_list)
    
    fullPower_duration = initial_delay_list[-1]
    
    return  t_list,  P_list_tot, fullPower_duration        
            
            
            


def capacity_factor(fuel_lifetime, refueling_period, num_reactors, power1, levelization_period, demand):
    
    schedule = calculate_schedule_multiple_reactors(fuel_lifetime, refueling_period, num_reactors, power1, levelization_period) 
    times =  schedule[0]
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
    tot_actual_output_t = sum(tot_actual_output_t)
    overall_capacity_factor = tot_actual_output_t/tot_nom_output

    return times_array_excludingRampUp, capacity_factor_t, overall_capacity_factor                 



def num_reactors_needed_for_capacity_factor(overall_capacity_factor_criteria, min_capacity_factor_criteria,fuel_lifetime, refueling_period, power, levelization_period, demand_0):
    
    num_reactors_0 =  int( np.ceil( demand_0 /power))
    for  num_reactors in np.linspace( num_reactors_0 , 5*num_reactors_0, 4*num_reactors_0+1):
        capacity_factor_results = (capacity_factor(fuel_lifetime, refueling_period, int(num_reactors), power, levelization_period, demand_0 ))
        
        # times_array_excludingRampUp = capacity_factor_results[0]
        capacity_factor_min =    min (capacity_factor_results[1])
        overall_capacity_factor   =   capacity_factor_results[2]
        
        if  overall_capacity_factor>=  overall_capacity_factor_criteria:
            if capacity_factor_min >= min_capacity_factor_criteria:
                num_reactors_final = num_reactors
                break

    return num_reactors_final        






def calculate_tipping_LR(lr_min, lr_max, lr_interval, small_reactor_cost, num_small_reactors ,num_large_reactors ,  ref_large_reactor_lr, ref_large_reactor_cost_per_kw ):
    
    # #Step1 : calculate cost of the large reactor
    large_reactor_cost = calculate_final_cost_due_to_learning_rate(ref_large_reactor_cost_per_kw, ref_large_reactor_lr, num_large_reactors )
    
    num_LR = int(np.ceil(1 + (lr_max - lr_min)/ lr_interval ) )  #num of learning rate samples
    
    SR_reduced_cost_save = []
    lr_save = []
    for lr in np.linspace(lr_min ,lr_max ,num_LR): 
        lr_save.append(lr)
        SR_reduced_cost = calculate_final_cost_due_to_learning_rate(small_reactor_cost, lr, num_small_reactors )
        SR_reduced_cost_save.append(SR_reduced_cost)
        
        LR_tipping_point = "Not Found" # if the tipping point is not found_
        if SR_reduced_cost < large_reactor_cost:
            LR_tipping_point = lr_save[-2]
            break

    return LR_tipping_point     





def calculate_break_even_cost_for_lr(lr_small, large_lr_min, large_lr_max, ref_large_reactor_cost_per_kw, num_large_reactors,  num_small_reactors, min_cost_small, max_cost_small, num_cost):
    large_reactor_cost_hi = calculate_final_cost_due_to_learning_rate(ref_large_reactor_cost_per_kw, large_lr_min, num_large_reactors ) # small lr leads to high cost
    large_reactor_cost_lo = calculate_final_cost_due_to_learning_rate(ref_large_reactor_cost_per_kw, large_lr_max, num_large_reactors ) # hi lr leads to small cost
    print(large_reactor_cost_hi, large_reactor_cost_lo)
    
    FOAK_cost_save =[]
    cost_tipping_point_list = []
    
    for cost_small in np.linspace(max_cost_small , min_cost_small ,num_cost):
        
        SR_reduced_cost =   calculate_final_cost_due_to_learning_rate(cost_small , lr_small, num_small_reactors )
     
        FOAK_cost_save.append(cost_small)
        cost_tipping_point = "Not Found" 
        print(SR_reduced_cost)
        if SR_reduced_cost<=large_reactor_cost_hi:
            print("yes")
           
            cost_tipping_point = FOAK_cost_save[-2]
            cost_tipping_point_list.append(cost_tipping_point )
            
            if SR_reduced_cost<large_reactor_cost_lo:
                break
    
    return min(cost_tipping_point_list), max(cost_tipping_point_list)





def calculate_all_tipping_costs(LR_interval, small_lr_min, small_lr_max, large_lr_min, large_lr_max,ref_large_reactor_cost_per_kw, num_large_reactors,  num_small_reactors, min_cost_small, max_cost_small, num_cost):
    
    num_LR = int(np.ceil(1 + (small_lr_max-small_lr_min)/ LR_interval ) )  #num of learning rate samples
    all_tipping_costs = []
    for lr_small in np.linspace(small_lr_min , small_lr_max, num_LR):
        results = calculate_break_even_cost_for_lr(lr_small, large_lr_min, large_lr_max, ref_large_reactor_cost_per_kw, num_large_reactors,  num_small_reactors, min_cost_small, max_cost_small, num_cost)
        all_tipping_costs.append(results)
    
        
    all_tipping_costs_list =  [item for t in all_tipping_costs for item in t]    
    return min(all_tipping_costs_list), max(all_tipping_costs_list)     


large_cost_should_be_per_kw = 7833
# ref_large_reactor_cost_per_kw = large_cost_should_be_per_kw

# # min_cost_small = large_cost_should_be_per_kw
# # max_cost_small = 6*large_cost_should_be_per_kw
# # num_cost = 300
# LR_interval = 0.02


# # # for smaller reactors
# small_lr_expected_lo = 0.05
# small_lr_expected_hi = 0.15

# large_lr_expected_lo = 0.05
# large_lr_expected_hi = 0.1
vogtle3_power = 1117
# demand = 500
# power = 300
# num_large_reactors = int(np.ceil(demand/vogtle3_power ))
# num_small_reactors =  int(np.ceil(demand/power))
        
# breakeven_points  = calculate_all_tipping_costs(LR_interval, small_lr_expected_lo, small_lr_expected_hi,\
            # The above code appears to be defining variables in Python related to large and small
            # reactors, including expected cost ranges, number of reactors, and cost per kilowatt.
            # large_lr_expected_lo, large_lr_expected_hi, ref_large_reactor_cost_per_kw, num_large_reactors,  num_small_reactors, min_cost_small, max_cost_small, num_cost)
            
            
# demand = 6000
# # ref_large_reactor_cost_per_kw = large_cost_should_be_per_kw
# power = 1
# cost_low = large_cost_should_be_per_kw  # * ((power/ vogtle3_power)**(0.9-1))
# cost_high = 8*cost_low 
# num_cost = 300   

# num_large_reactors = int(np.ceil(demand/vogtle3_power ))
# num_small_reactors =  int(np.ceil(demand/power))
# breakeven_points  = calculate_all_tipping_costs(LR_interval, small_lr_expected_lo, small_lr_expected_hi,\
#             large_lr_expected_lo, large_lr_expected_hi, ref_large_reactor_cost_per_kw, num_large_reactors,  num_small_reactors, cost_low, cost_high, num_cost)




#economies of scale exponents
n_expo_min = 0.2
n_expo_max = 0.8

demand = 2000
power = 1000
num_cost = 50

cost_lo = large_cost_should_be_per_kw *  ((power/ vogtle3_power)**(n_expo_max-1))
print(cost_lo,large_cost_should_be_per_kw, "ttt" )

cost_hi =  2 *cost_lo

num_large_reactors = int(np.ceil(demand/vogtle3_power ))
num_small_reactors =  int(np.ceil(demand/power))
lr_interval = 0.001
# for smaller reactors
small_lr_expected_lo = 0.05
small_lr_expected_hi = 0.15

large_lr_expected_lo = 0.05
large_lr_expected_hi = 0.1

ref_large_reactor_cost_per_kw = large_cost_should_be_per_kw


breakeven_points  = calculate_all_tipping_costs(lr_interval, small_lr_expected_lo, small_lr_expected_hi, large_lr_expected_lo, large_lr_expected_hi, ref_large_reactor_cost_per_kw, num_large_reactors,  num_small_reactors, cost_lo, cost_hi, num_cost)