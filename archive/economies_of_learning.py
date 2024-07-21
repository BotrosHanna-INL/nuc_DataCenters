import numpy as np


def calculate_final_cost_due_to_learning_rate(initial_cost_usd_per_kw, learning_rate, num_reactors ):
    cost_reduction_sum = 0 # initizalition 
    
    for nn in range(1, num_reactors +1):# cost decreases from FOAK to NOAK and averaged over the number of reactors built
        cost_reduction_sum += ( (1 - learning_rate) **(np.log2(nn)))
    cost_reduction_factor = cost_reduction_sum/num_reactors   
    reduced_cost_used_kw =   initial_cost_usd_per_kw *  cost_reduction_factor


    return reduced_cost_used_kw
             


def calculate_break_even_cost_for_lr(lr_small, large_lr_min, large_lr_max, ref_large_reactor_cost_per_kw, num_large_reactors,  num_small_reactors, min_cost_small, max_cost_small, num_cost):
    
    large_reactor_cost_hi = calculate_final_cost_due_to_learning_rate(ref_large_reactor_cost_per_kw, large_lr_min, num_large_reactors ) # small lr leads to high cost
    large_reactor_cost_lo = calculate_final_cost_due_to_learning_rate(ref_large_reactor_cost_per_kw, large_lr_max, num_large_reactors ) # hi lr leads to small cost
    
    FOAK_cost_save =[]
    cost_tipping_point_list = []
    
    for cost_small in np.linspace(max_cost_small , min_cost_small ,num_cost):
        
        SR_reduced_cost =   calculate_final_cost_due_to_learning_rate(cost_small , lr_small, num_small_reactors )
     
        FOAK_cost_save.append(cost_small)
        cost_tipping_point = "Not Found" 
        if SR_reduced_cost<=large_reactor_cost_hi:
           
            cost_tipping_point = FOAK_cost_save[-2]
            cost_tipping_point_list.append(cost_tipping_point )
            
            if SR_reduced_cost<large_reactor_cost_lo:
                break
    
    return min(cost_tipping_point_list), max(cost_tipping_point_list)




def calculate_break_even_cost_for_lr_per_demand(lr_small, large_lr_min, large_lr_max,\
    ref_large_reactor_cost_per_kw, num_large_reactors,  num_small_reactors, min_cost_small, max_cost_small,\
        num_cost, demand, power_large, power_small):
    # This is when you have extra reactor for reliability so the demand may (may not) be smaller than the (num of reactor*power)
    large_reactor_cost_hi = (calculate_final_cost_due_to_learning_rate(ref_large_reactor_cost_per_kw, large_lr_min, num_large_reactors )) *\
        (num_large_reactors*power_large/demand) # small lr leads to high cost
    
    large_reactor_cost_lo = (calculate_final_cost_due_to_learning_rate(ref_large_reactor_cost_per_kw, large_lr_max, num_large_reactors ))*\
        (num_large_reactors*power_large/demand) # hi lr leads to small cost
         
    
    FOAK_cost_save =[]
    cost_tipping_point_list = []
    
    for cost_small in np.linspace(max_cost_small , min_cost_small ,num_cost):
        
        SR_reduced_cost =   (calculate_final_cost_due_to_learning_rate(cost_small , lr_small, num_small_reactors ))*\
            (num_small_reactors*power_small/demand)
     
        FOAK_cost_save.append(cost_small)
        cost_tipping_point = "Not Found" 
        if SR_reduced_cost<=large_reactor_cost_hi:
           
            cost_tipping_point = FOAK_cost_save[-2]
            cost_tipping_point_list.append(cost_tipping_point )
            
            if SR_reduced_cost<large_reactor_cost_lo:
                break
    
    return min(cost_tipping_point_list), max(cost_tipping_point_list)

