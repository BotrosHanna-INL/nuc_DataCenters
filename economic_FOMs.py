import numpy as np
from parameters import construction_duration_for_power, occ_for_power,  OM_cost_per_MWh
from economies_of_learning import calculate_final_cost_due_to_learning_rate


def capital_investment(P, interest_rate):
    construction_duration = construction_duration_for_power(P)
    tot_overnight_cost = occ_for_power(P)
    
    # Interest rate from this equation (from Levi)
    B =(1+ np.exp((np.log(1+ interest_rate)) * construction_duration/12))
    C  =((np.log(1+ interest_rate)*(construction_duration/12)/3.14)**2+1)
    Interest_expenses = tot_overnight_cost*((0.5*B/C)-1)
    return (Interest_expenses + tot_overnight_cost) # this is TCI in $/kw

def tot_TCI_multiple_reactors (P, interest_rate, num_reactors): # multiple reactors of the same power

    # the capital investment of one reactor ($/kw)
    levlized_TCI = capital_investment(P, interest_rate)
    
    if P >500:
        learning_rate = 0.08
    elif P<=500 :
        learning_rate = 0.095 
    
    # the capital investment of one reactor ($/kw) after the learning rate effect
    final_TCI = calculate_final_cost_due_to_learning_rate(levlized_TCI, learning_rate, num_reactors ) # This is still cost per kw
    final_TCI_one_reactor = final_TCI *P*1000 #(Dollar)
    final_TCI_all_reactors = final_TCI_one_reactor *num_reactors 
    return final_TCI_all_reactors # (dollars)

def level_cost_of_energy( interest_rate, P, num_reactors, list_of_total_generated_MWh_per_year_from_all_reactors,\
    list_of_generated_MWh_per_year_from_all_reactors_per_demand,list_of_sold_electricity_MWh_per_year_from_all_reactors, elec_price ):
    sum_cost = 0 # initialization 
    sum_elec = 0 # initialization 
           
    for year in range( len(list_of_total_generated_MWh_per_year_from_all_reactors)):
        if year == 0:
            cap_cost =  tot_TCI_multiple_reactors (P, interest_rate, num_reactors) 
            OM_cost_per_year = 0
            elec_gen = 0
            revenue = 0
        
        elif year > 0:
         
            cap_cost = 0 
            OM_cost_per_year = OM_cost_per_MWh(P) * list_of_total_generated_MWh_per_year_from_all_reactors[year-1]
            revenue = elec_price * list_of_sold_electricity_MWh_per_year_from_all_reactors[year-1]
            elec_gen =  list_of_generated_MWh_per_year_from_all_reactors_per_demand[year-1]
        
        sum_cost += (cap_cost + OM_cost_per_year - revenue) / ((1 +interest_rate)**(year) ) 
        sum_elec += elec_gen/ ((1 + interest_rate)**year) 
    
    LCOE =  sum_cost/ sum_elec
    return LCOE 



# TCI for a mix of reactors

def tot_TCI_multiple_reactors_mix (power_list, interest_rate, num_reactors_list):
    tot_TCI_for_specific_reactor_power_list = []
    
    for i in range(len(power_list)):
        tot_TCI_for_specific_reactor_power = tot_TCI_multiple_reactors (power_list[i], interest_rate, num_reactors_list[i])
        tot_TCI_for_specific_reactor_power_list.append(tot_TCI_for_specific_reactor_power)
        
    return sum(tot_TCI_for_specific_reactor_power_list)



def level_cost_of_energy_reactor_mix( interest_rate, power_list, num_reactors_list,\
    list_of_generated_MWh_per_year_from_all_reactors_per_demand, list_of_sold_electricity_MWh_per_year_from_all_reactors, elec_price,\
        list_of_OM_cost_per_year_all_reactors):
    
    sum_cost = 0 # initialization 
    sum_elec = 0 # initialization 
           
    for year in range( len(list_of_generated_MWh_per_year_from_all_reactors_per_demand)):
        if year == 0:
            cap_cost =  tot_TCI_multiple_reactors_mix(power_list, interest_rate, num_reactors_list)
            OM_cost_per_year = 0
            elec_gen = 0
            revenue = 0
        
        elif year > 0:
         
            cap_cost = 0 
            
            OM_cost_per_year =  list_of_OM_cost_per_year_all_reactors[year-1]
            revenue = elec_price * list_of_sold_electricity_MWh_per_year_from_all_reactors[year-1]
            elec_gen =  list_of_generated_MWh_per_year_from_all_reactors_per_demand[year-1]
        
        sum_cost += (cap_cost + OM_cost_per_year - revenue) / ((1 +interest_rate)**(year) ) 
        sum_elec += elec_gen/ ((1 + interest_rate)**year) 
    
    LCOE =  sum_cost/ sum_elec
    # print("LCOE NOW is: ", LCOE)
    return LCOE