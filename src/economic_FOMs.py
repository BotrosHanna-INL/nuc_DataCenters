import numpy as np
from parameters import construction_duration_for_power_FOAK, occ_for_power_FOAK,  OM_cost_per_MWh, LR_for_power, occ_for_power_FOAK_thermal, OM_cost_per_MWh_thermal
from economies_of_learning import calculate_final_cost_due_to_learning_rate


def capital_investment_FOAK(P, interest_rate):
    construction_duration = construction_duration_for_power_FOAK(P)
    tot_overnight_cost = occ_for_power_FOAK(P)
    
    # Interest rate from this equation (from Levi)
    B =(1+ np.exp((np.log(1+ interest_rate)) * construction_duration/12))
    C  =((np.log(1+ interest_rate)*(construction_duration/12)/3.14)**2+1)
    Interest_expenses = tot_overnight_cost*((0.5*B/C)-1)
    return (Interest_expenses + tot_overnight_cost) # this is TCI in $/kw


def capital_investment_FOAK_thermal(P_thermal, interest_rate):
    
    P = P_thermal * 0.35 # assume thermal effieiency is 35%
    construction_duration = construction_duration_for_power_FOAK(P)
    tot_overnight_cost = occ_for_power_FOAK_thermal(P_thermal)
    
    # Interest rate from this equation (from Levi)
    B =(1+ np.exp((np.log(1+ interest_rate)) * construction_duration/12))
    C  =((np.log(1+ interest_rate)*(construction_duration/12)/3.14)**2+1)
    Interest_expenses = tot_overnight_cost*((0.5*B/C)-1)
    return (Interest_expenses + tot_overnight_cost) # this is TCI in $/kw





def tot_TCI_multiple_reactors_starting_from_FOAK (P, interest_rate, num_reactors): # multiple reactors of the same power

    # the capital investment of one reactor ($/kw)
    levlized_TCI = capital_investment_FOAK(P, interest_rate)
    
    learning_rate = LR_for_power(P)
    
    # the capital investment of one reactor ($/kw) after the learning rate effect
    final_TCI = calculate_final_cost_due_to_learning_rate(levlized_TCI, learning_rate, num_reactors ) # This is still cost per kw
    final_TCI_one_reactor = final_TCI *P*1000 #(Dollar)
    final_TCI_all_reactors = final_TCI_one_reactor *num_reactors 
    return final_TCI_all_reactors # (dollars)



def tot_TCI_multiple_reactors_starting_from_BOAK (P, interest_rate, num_reactors): # multiple reactors of the same power

    # the capital investment of one reactor ($/kw)
    levlized_TCI = capital_investment_FOAK(P, interest_rate)
    
    learning_rate = LR_for_power(P)
    
    # the capital investment of one reactor ($/kw) after the learning rate effect
    # to start from BOAK, I add extra reactor. Next, I remove FOAK
    final_TCI_with_extra_ractor = calculate_final_cost_due_to_learning_rate(levlized_TCI, learning_rate, num_reactors+1 ) # This is still cost per kw
    final_TCI_one_reactor = final_TCI_with_extra_ractor *P*1000 #(Dollar)
    final_TCI_all_reactors_with_extra_ractor = final_TCI_one_reactor *(num_reactors +1)
    final_TCI_all_reactors_starting_from_BOAK = final_TCI_all_reactors_with_extra_ractor -  levlized_TCI*P*1000
    return final_TCI_all_reactors_starting_from_BOAK# (dollars)




def tot_TCI_multiple_reactors_starting_from_BOAK_thermal (P_thermal, interest_rate, num_reactors): # multiple reactors of the same power (thermal power for heat applications)

    # the capital investment of one reactor ($/kw)
    levlized_TCI = capital_investment_FOAK_thermal(P_thermal, interest_rate)
    
    learning_rate = LR_for_power(P_thermal*0.35) # The power is 35% the thermal power
    
    # the capital investment of one reactor ($/kw) after the learning rate effect
    # to start from BOAK, I add extra reactor. Next, I remove FOAK
    final_TCI_with_extra_ractor = calculate_final_cost_due_to_learning_rate(levlized_TCI, learning_rate, num_reactors+1 ) # This is still cost per kw
    final_TCI_one_reactor = final_TCI_with_extra_ractor *P_thermal*0.35*1000 #(Dollar)
    final_TCI_all_reactors_with_extra_ractor = final_TCI_one_reactor *(num_reactors +1)
    final_TCI_all_reactors_starting_from_BOAK = final_TCI_all_reactors_with_extra_ractor -  levlized_TCI*P_thermal*0.35*1000
    return final_TCI_all_reactors_starting_from_BOAK# (dollars)



# 1000, 6721
#100, 6468
#10, 5361
#1: 3639

# print((tot_TCI_multiple_reactors_starting_from_FOAK (P, 0.06, N))/(P*N*1000))
# print((tot_TCI_multiple_reactors_starting_from_BOAK (P, 0.06, N))/(P*N*1000))


#starting from the second reactor
def level_cost_of_energy_starting_from_BOAK( interest_rate, P, num_reactors, list_of_total_generated_MWh_per_year_from_all_reactors,\
    list_of_generated_MWh_per_year_from_all_reactors_per_demand,list_of_sold_electricity_MWh_per_year_from_all_reactors, elec_price ):
    sum_cost = 0 # initialization 
    sum_elec = 0 # initialization 
           
    for year in range( len(list_of_total_generated_MWh_per_year_from_all_reactors)):
        if year == 0:
            cap_cost = tot_TCI_multiple_reactors_starting_from_BOAK(P, interest_rate, num_reactors) 
            OM_cost_per_year = 0
            elec_gen = 0
            revenue = 0
        
        elif year > 0:
         
            cap_cost = 0 
            OM_cost_per_year = OM_cost_per_MWh(P, num_reactors) * list_of_total_generated_MWh_per_year_from_all_reactors[year-1]
            revenue = elec_price * list_of_sold_electricity_MWh_per_year_from_all_reactors[year-1]
            elec_gen =  list_of_generated_MWh_per_year_from_all_reactors_per_demand[year-1]
        
        sum_cost += (cap_cost + OM_cost_per_year - revenue) / ((1 +interest_rate)**(year) ) 
        sum_elec += elec_gen/ ((1 + interest_rate)**year) 
    
    LCOE =  sum_cost/ sum_elec
    return LCOE 




def level_cost_of_energy_starting_from_BOAK_thermal( interest_rate, P_thermal, num_reactors, list_of_total_generated_MWh_per_year_from_all_reactors,\
    list_of_generated_MWh_per_year_from_all_reactors_per_demand ):
    sum_cost = 0 # initialization 
    sum_thermal = 0 # initialization 
    
    P = 0.35 * P_thermal  
    
    for year in range( len(list_of_total_generated_MWh_per_year_from_all_reactors)):
        if year == 0:
            cap_cost = tot_TCI_multiple_reactors_starting_from_BOAK_thermal (P_thermal, interest_rate, num_reactors)
            OM_cost_per_year = 0
            thermal_gen = 0
         
        
        elif year > 0:
         
            cap_cost = 0 
            OM_cost_per_year = OM_cost_per_MWh_thermal(P_thermal, num_reactors) * list_of_total_generated_MWh_per_year_from_all_reactors[year-1] # This is cost per MWe
            thermal_gen =  (list_of_generated_MWh_per_year_from_all_reactors_per_demand[year-1])/0.35 # assuming efficiency is 35%
        
        sum_cost += (cap_cost + OM_cost_per_year ) / ((1 +interest_rate)**(year) ) 
        sum_thermal += thermal_gen/ ((1 + interest_rate)**year)  # total of thermal energy
    
    LCOH =  sum_cost/ sum_thermal
    return LCOH 




# TCI for a mix of reactors

# def tot_TCI_multiple_reactors_mix (power_list, interest_rate, num_reactors_list):
#     tot_TCI_for_specific_reactor_power_list = []
    
#     for i in range(len(power_list)):
#         tot_TCI_for_specific_reactor_power = tot_TCI_multiple_reactors (power_list[i], interest_rate, num_reactors_list[i])
#         tot_TCI_for_specific_reactor_power_list.append(tot_TCI_for_specific_reactor_power)
        
#     return sum(tot_TCI_for_specific_reactor_power_list)



# TCI for a mix of reactors (starting from BOAK)


"""

THE REACTORS MIX

"""


def tot_TCI_multiple_reactors_mix_starting_from_BOAK(power_list, interest_rate, num_reactors_list):
    tot_TCI_for_specific_reactor_power_list = []
    
    for i in range(len(power_list)):
        tot_TCI_for_specific_reactor_power = tot_TCI_multiple_reactors_starting_from_BOAK (power_list[i], interest_rate, num_reactors_list[i])
        tot_TCI_for_specific_reactor_power_list.append(tot_TCI_for_specific_reactor_power)
        
    return sum(tot_TCI_for_specific_reactor_power_list)






def tot_TCI_multiple_reactors_mix_starting_from_BOAK_thermal(power_list, interest_rate, num_reactors_list):
    tot_TCI_for_specific_reactor_power_list = []
    
    for i in range(len(power_list)):
        tot_TCI_for_specific_reactor_power = tot_TCI_multiple_reactors_starting_from_BOAK_thermal (power_list[i]/0.35, interest_rate, num_reactors_list[i])
        tot_TCI_for_specific_reactor_power_list.append(tot_TCI_for_specific_reactor_power)
        
    return sum(tot_TCI_for_specific_reactor_power_list)











# def level_cost_of_energy_reactor_mix( interest_rate, power_list, num_reactors_list,\
#     list_of_generated_MWh_per_year_from_all_reactors_per_demand, list_of_sold_electricity_MWh_per_year_from_all_reactors, elec_price,\
#         list_of_OM_cost_per_year_all_reactors):
    
#     sum_cost = 0 # initialization 
#     sum_elec = 0 # initialization 
           
#     for year in range( len(list_of_generated_MWh_per_year_from_all_reactors_per_demand)):
#         if year == 0:
#             cap_cost =  tot_TCI_multiple_reactors_mix(power_list, interest_rate, num_reactors_list)
#             OM_cost_per_year = 0
#             elec_gen = 0
#             revenue = 0
        
#         elif year > 0:
         
#             cap_cost = 0 
            
#             OM_cost_per_year =  list_of_OM_cost_per_year_all_reactors[year-1]
#             revenue = elec_price * list_of_sold_electricity_MWh_per_year_from_all_reactors[year-1]
#             elec_gen =  list_of_generated_MWh_per_year_from_all_reactors_per_demand[year-1]
        
#         sum_cost += (cap_cost + OM_cost_per_year - revenue) / ((1 +interest_rate)**(year) ) 
#         sum_elec += elec_gen/ ((1 + interest_rate)**year) 
    
#     LCOE =  sum_cost/ sum_elec
#     # print("LCOE NOW is: ", LCOE)
#     return LCOE


def level_cost_of_energy_reactor_mix_starting_from_BOAK( interest_rate, power_list, num_reactors_list,\
    list_of_generated_MWh_per_year_from_all_reactors_per_demand,  list_of_sold_electricity_MWh_per_year_from_all_reactors,  elec_price,\
        list_of_OM_cost_per_year_all_reactors):
    
    sum_cost = 0 # initialization 
    sum_elec = 0 # initialization 
           
    for year in range( len(list_of_generated_MWh_per_year_from_all_reactors_per_demand)):
        if year == 0:
            cap_cost =  tot_TCI_multiple_reactors_mix_starting_from_BOAK(power_list, interest_rate, num_reactors_list)
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
