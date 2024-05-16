import numpy as np

def sample_cost(demand, P_info, LR_info, FOAK_cost_info ):
    
    P_min, P_max, P_interval = P_info
    LR_min, LR_max, LR_interval = LR_info
    min_ratio, max_ratio, cost_interval = FOAK_cost_info
    
    # #save data
    LR_list = []
    power_list = []
    initial_cost_SR_list = []
    SR_reduced_cost_list = []

    num_P = int(np.ceil( 1 +  (P_max - P_min)/ P_interval ))  #num of power samples
    num_LR = int(np.ceil(1 + (LR_max - LR_min)/ LR_interval ) )  #num of learning rate samples
    num_cost = int(np.ceil(1 + (max_ratio - min_ratio)/  cost_interval ) )  #num of cost ratio samples
  

    for P in  np.linspace(P_min , P_max ,num_P) :# between 50 and 300 MW for one SR 
        
        #number of SR required to get to the target demand
        num_reactors =int( np.ceil(demand /P))  # it has to be the ceiling

        for lr in np.linspace(LR_min , LR_max ,num_LR): # iterate through learning rate
            
            cost_reduction_sum = 0 # initizalition
            
            for nn in range(1, num_reactors +1):# cost decreases from NOAK to FOAK and averaged over the number of reactors built
                cost_reduction_sum += ( (1 - lr) **(np.log2(nn)))
            cost_reduction_factor = cost_reduction_sum/num_reactors
                
            #cost of each reactor
            for cost in np.linspace(min_ratio , max_ratio ,num_cost):
                
                # cost reduction due to Learning rate
                SR_reduced_cost =   cost *  cost_reduction_factor   
                
                
                LR_list.append(lr)
                power_list.append(P)
                initial_cost_SR_list.append(cost)
                SR_reduced_cost_list.append(SR_reduced_cost)
    full_results = np.vstack((np.array(power_list), np.array(LR_list) ,np.array(initial_cost_SR_list), np.array(SR_reduced_cost_list)))
    full_results = full_results.T
    
    reduced_cost_tol  = np.median(abs(np.diff(full_results[:,3]))) # because of sampling, we may not exact cost we want, there is a tolerance
    return full_results,  reduced_cost_tol





def calculate_tipping_learning_rate(LR_info, demand, power , ref_large_reactor_power, init_cost_ratio, n_exponent, method ):
    [lr_min, lr_max,  lr_interval] = LR_info
    num_LR = int(np.ceil(1 + (lr_max - lr_min)/ lr_interval ) )  #num of learning rate samples
    
    num_reactors =int( np.ceil(demand /power))  # it has to be the ceiling
    
    SR_reduced_cost_save = []
    lr_save = []
    
    if method == "free cost ratios":
        

        for lr in np.linspace(lr_min ,lr_max ,num_LR): 
            lr_save.append(lr)
            cost_reduction_sum = 0 # initizalition 
                    
            for nn in range(1, num_reactors +1):# cost decreases from NOAK to FOAK and averaged over the number of reactors built
                cost_reduction_sum += ( (1 - lr) **(np.log2(nn)))
            cost_reduction_factor = cost_reduction_sum/num_reactors
            SR_reduced_cost =   init_cost_ratio *  cost_reduction_factor 
            SR_reduced_cost_save.append(SR_reduced_cost)
            LR_tipping_point = "Not Found" # if the tipping point is not found_
            if SR_reduced_cost < 1:
                LR_tipping_point = lr_save[-2]
                break
        
        return LR_tipping_point     
            
    
    if method == "logarithmic curve":
        
        initial_cost_ratio = (power/ref_large_reactor_power)**(n_exponent-1)
        
        for lr in np.linspace(lr_min ,lr_max ,num_LR): 
            lr_save.append(lr)
            cost_reduction_sum = 0 # initizalition           
            for nn in range(1, num_reactors +1):# cost decreases from NOAK to FOAK and averaged over the number of reactors built
                cost_reduction_sum += ( (1 - lr) **(np.log2(nn)))
            cost_reduction_factor = cost_reduction_sum/num_reactors
            SR_reduced_cost =   initial_cost_ratio  *  cost_reduction_factor 
            SR_reduced_cost_save.append(SR_reduced_cost)
           
            LR_tipping_point = "Not Found" # if the tipping point is not found_
            
            if SR_reduced_cost < 1:
                LR_tipping_point = lr_save[-2]
                # print("hi" , LR_tipping_point )
                break
        return LR_tipping_point, initial_cost_ratio     
    
    



def calculate_tipping_cost(lr, FOAK_cost_info, demand, power ):

    min_ratio, max_ratio, cost_interval = FOAK_cost_info
    num_cost = int(np.ceil(1 + abs(max_ratio - min_ratio)/  cost_interval ) )  #num of cost ratio samples
    
    cost_reduction_sum = 0 # initizalition 
    num_reactors =int( np.ceil(demand /power))  # it has to be the ceiling
                  
    for nn in range(1, num_reactors +1):# cost decreases from NOAK to FOAK and averaged over the number of reactors built
        cost_reduction_sum += ( (1 - lr) **(np.log2(nn)))
    cost_reduction_factor = cost_reduction_sum/num_reactors
    
    FOAK_cost_save =[]
    
    for init_cost in np.linspace(min_ratio , max_ratio ,num_cost):
        
        SR_reduced_cost =   init_cost *  cost_reduction_factor
        FOAK_cost_save.append(init_cost)
        cost_tipping_point = "Not Found" 
        if SR_reduced_cost < 1:
            cost_tipping_point = FOAK_cost_save[-2]
            break
    return cost_tipping_point     





# SR_to_Large_0 = 10  
# SR_to_Large_1 = 1
# SR_to_Large_interval = 0.1
# cost_info = [SR_to_Large_0, SR_to_Large_1, SR_to_Large_interval ]


# calculate_tipping_cost(0.15, cost_info, 2000, 1 )
