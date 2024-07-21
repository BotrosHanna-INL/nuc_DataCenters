import numpy as np
from scipy.optimize import curve_fit


# Ref parameters based on the GAIN's Database Spreadsheet: https://gain.inl.gov/content/uploads/4/2024/06/INL-RPT-24-77048-R1.xlsx
power_large_ref = 1000 # MWe
power_SMR_ref = 200 # MWe # the average power of the SMR in the sheet is 200 
power_micro_ref = 5 # MW 

# baseline learning rate from https://www.osti.gov/biblio/2371533
LR_large = 0.08
LR_small = 0.095 # (for SMR and microreactors)
LR_std = 0.03 #(based on the data in the spreadsheet : https://gain.inl.gov/content/uploads/4/2024/06/INL-RPT-24-77048-R1.xlsx )

# Inflation Multiplier from 2019 to 2022: https://fred.stlouisfed.org/series/GDPDEF#0
inf_mult_19_22 = 117.965/104.004



#### OCC Cost ######
# ref: https://www.osti.gov/biblio/2371533

OCC_large_conservative = 7750 # USD/kW

# Since the cost if from the Gain report is 2nd of a kind cost, I convert it to first of a kind cost (assuming learning rate)

OCC_large_conservative_FOAK = OCC_large_conservative / (    (1 - LR_large)**(np.log2(2))   )

# OCC_large_moderate = 5750 # 
 

# SMR
OCC_SMR_conservative = 10000 # USD/kW
# Since the cost if from the Gain report is 2nd of a kind cost, I convert it to first of a kind cost (assuming learning rate)

OCC_SMR_conservative_FOAK = OCC_SMR_conservative / (    (1 - LR_small)**(np.log2(2))   )
# OCC_SMR_moderate = 7750 



#Microreactors\n# from the lit review : https://www.osti.gov/biblio/1986466: Table 17 (scaled data) only OCC. The data that had the financing cost were excluded
# # all of them are multuplied by (inflation multuplier from 2019 to 2022) 

MR_cost_1  = 10000 * inf_mult_19_22
MR_cost_2 = + 15000 *inf_mult_19_22
MR_cost_3 =  20000 *inf_mult_19_22
MR_cost_4 = 3996 * inf_mult_19_22
MR_cost_5 = 8276  * inf_mult_19_22
MR_cost_6 = 14973 * inf_mult_19_22
MR_cost_average =np.mean ([MR_cost_1,MR_cost_2, MR_cost_3, MR_cost_4,MR_cost_5, MR_cost_6 ])
MR_cost_std = np.std ([MR_cost_1,MR_cost_2, MR_cost_3, MR_cost_4,MR_cost_5, MR_cost_6 ])

OCC_micro_conservative = MR_cost_average + MR_cost_std # USD/kW

# These are the original data (no manipulation) so I will use them as the FOAK costs
OCC_mico_conservative_FOAK  = OCC_micro_conservative 
# OCC_micro_moderate = MR_cost_average



# now lets do curve fitting\n
def large_reactor_func(x, a, b):  
    return a*(x**b)

xdata1_OCC = [ power_large_ref,  power_SMR_ref,power_micro_ref ]
ydata1_OCC = [ OCC_large_conservative_FOAK,  OCC_SMR_conservative_FOAK, OCC_mico_conservative_FOAK  ]
popt1, p_cov1 = curve_fit(large_reactor_func, xdata1_OCC , ydata1_OCC)

def occ_for_power(P):
    return popt1[0] *(P**popt1[1]) # $/kw


# print(occ_for_power(7))


##### O & M COST   #####

# One of the shortcomings here is that the O&M cost is independent of the fuel lifetime
#Large reactor O&M Costs 
OM_large_hi = 39.8 # Total O&M ($/MWh)
# OM_large_medium = 34.6 # Total O&M ($/MWh)


# SMR
OM_SMR_hi = 41.4  # Total O&M ($/MWh)     
# OM_SMR_medium = 30.2 # Total O&M ($/MWh)


#Microreactors
# https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_66425.pdf: TABLE 18
# # multuplied by (inflation multuplier from 2019 to 2022) 

OM_Micro_Avg = inf_mult_19_22 *np.mean([69, 103, 137, 125, 136, 59]) # $/MWh
OM_Micro_std = inf_mult_19_22 *np.std([69, 103, 137, 125, 136, 59]) # $/MWh
OM_Mirco_medium = OM_Micro_Avg # $/MWh

OM_Mirco_hi = OM_Micro_Avg+OM_Micro_std # $/MWh



def func_OM(x, a, b):  # Curve fitting for O&M cost = f (power)
    return a*(x**b)

xdata_OM = [ power_large_ref,  power_SMR_ref, power_micro_ref ]
ydata_OM = [ OM_large_hi,  OM_SMR_hi, OM_Mirco_hi  ]
popt_OM, p_cov_OM = curve_fit(func_OM, xdata_OM  , ydata_OM)

def OM_cost_per_MWh(power):
    if power == 0:
        return 0
    else:
        return  popt_OM[0] *(power**popt_OM[1]) # O&M cost: $/Mwh 
    
    
 
##### Construction Duration #####


# Data from: https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_107010.pdf

cons_duration_large_conservative = 125 #(months)
cons_duration_SMR_conservative = 71 #(months)
cons_duration_micro_conservative = 36 #(months) # I assumed this!

# Curve fitting

def func_construction(x, a, b):  # Curve fitting for construction duration = f( power)
    return a*(x**b)
xData_duration = [ power_large_ref,  power_SMR_ref, power_micro_ref ]
yData_duration = [cons_duration_large_conservative , cons_duration_SMR_conservative , cons_duration_micro_conservative ]
popt_, p_cov_ = curve_fit(func_construction, xData_duration   ,yData_duration)


def construction_duration_for_power(P):
    if P == 0:
        return 0
    else:
        return popt_[0] *(P**popt_[1])
        
        

 
##### Fuel Cycle: Fuel cycle length   && refueling duration
    
def refueling_duration_estimate(reactor_power):
    # For now, assume that the refueling duration is always 4 weeks and not a runction of reactor power 
    if reactor_power > 0:
        return 4


# fuel lifetime
def fuel_cycle_length(reactor_power): 
    # The fuel cycle length is assume to be 2, 3, 4, years for large, SMR, mico reactors respectively
    
    if reactor_power > 500:
        lifetime = int(np.floor(2*365/7)) # weeks (2 years)
        
    elif reactor_power<= 500 and reactor_power >50:
        lifetime = int(np.floor(3*365/7))# weeks (3 years)
        
    elif  reactor_power <=50:   
        lifetime = int(np.floor(4*365/7))# weeks (4 years)
         
    return lifetime     # Total cycle length in weeks



# specify colors for each power (for plotting)
def color_of(power):
    pwr_list = [1000, 500, 300, 200, 100  ,50, 20, 5, 1]
    colors_list = ['tab:brown' ,'b', 'g', 'r', 'c', 'm', 'y', 'k', 'tab:orange']
    for i in range (len(pwr_list)):
        if power == pwr_list[i]:
            the_color = colors_list[i]
    return the_color




def repeat_elements(elements, counts):
    result = []
    for element, count in zip(elements, counts):
        result.extend([element] * count)
    return result

# # Example usage:
# numbers = [1, 2, 3]
# repeat_counts = [2, 3, 1]




# Learning rate for mi(croreactors
lr_factory = 0.24285492 # https://www.tandfonline.com/doi/full/10.1080/00295450.2023.2206779
Lr_site = 0.08 # assumption

factory_contribution_to_cost = 0.4 #https://www.tandfonline.com/doi/full/10.1080/00295450.2023.2206779
site_contribution_to_cost = 1 -factory_contribution_to_cost  
Num_of_units = 100 #https://www.tandfonline.com/doi/full/10.1080/00295450.2023.2206779


LR_tot_micro = 1 - np.exp((np.log(factory_contribution_to_cost*( (1-lr_factory)**np.log2(Num_of_units)) +\
    site_contribution_to_cost*((1-Lr_site)**np.log2(Num_of_units)))) / np.log2(Num_of_units))

print(LR_tot_micro)

def func_LR(x, a, b):  # Curve fitting for LR = f (power)
    return a*(x**b)

xData_LR = [power_large_ref,  power_SMR_ref, 5] # 0.02 from the MARVEL paper: https://www.tandfonline.com/doi/full/10.1080/00295450.2023.2206779
yData_LR = [LR_large, LR_small, LR_tot_micro]
popt_lr_, p_cov_lr_ = curve_fit(func_LR, xData_LR   ,yData_LR)

def LR_for_power(P):
    if P == 0:
        return 0
    else:
        return popt_lr_[0] *(P**popt_lr_[1])



# data for the refueling interval: https://world-nuclear.org/information-library/nuclear-fuel-cycle/nuclear-power-reactors/small-nuclear-power-reactors
# 1: AHTR/FHR: interval avg = (2.5 + 4)/2 = 3.25 years (power = 50MWe) or up to 4 years
# 
# # https://world-nuclear.org/information-library/nuclear-fuel-cycle/nuclear-power-reactors/small-nuclear-power-reactors
#KLT-40s P = 35 MWe, 


# Curve fitting for the O&MC cost change with the number of units
def func_OM_reduction(x, a):  # Curve fitting for LR = f (power)
    return (a/x) +1-a

# Source
# https://www.osti.gov/biblio/713993: Table2
x_OM = [1, 2, 4, 8] # number of units
y_OM = [1, 0.729032258, 0.606451613, 0.574193548] # This is the O&M cost per unit
popt_om1_, p_cov_lr_ = curve_fit(func_OM_reduction, x_OM   , y_OM)

print("hh",popt_om1_)
# def OM_cost_reduction_factor(number_of_units):

#     return (number_of_units/popt_om1_[0]) + 1-number_of_units/popt_om1_[0] 
# print(OM_cost_reduction_factor(10))