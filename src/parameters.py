import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings("ignore")


# Ref parameters based on the GAIN's Database Spreadsheet: https://gain.inl.gov/content/uploads/4/2024/06/INL-RPT-24-77048-R1.xlsx
power_large_ref = 1000 # MWe
power_SMR_ref = 200 # MWe # the average power of the SMR in the sheet is 200 
power_micro_ref = 5 # MW # The microreactor power: https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_66425.pdf

# baseline learning rate from https://www.osti.gov/biblio/2371533
LR_large_reactor = 0.08
LR_SMR = 0.095 # (for SMR)
LR_std = 0.03 #(based on the data in the spreadsheet : https://gain.inl.gov/content/uploads/4/2024/06/INL-RPT-24-77048-R1.xlsx )


# Learning rate for microreactors
lr_factory = 0.24285492 # https://www.tandfonline.com/doi/full/10.1080/00295450.2023.2206779
Lr_site = 0.08 # assumption (similar to large reactors)

factory_contribution_to_cost = 0.4  #https://www.tandfonline.com/doi/full/10.1080/00295450.2023.2206779 # This is build on 5 MW reactor
site_contribution_to_cost = 1 - factory_contribution_to_cost  
Num_of_units = 100  #https://www.tandfonline.com/doi/full/10.1080/00295450.2023.2206779


LR_tot_micro = 1 - np.exp((np.log(factory_contribution_to_cost*( (1-lr_factory)**np.log2(Num_of_units)) +\
    site_contribution_to_cost*((1-Lr_site)**np.log2(Num_of_units)))) / np.log2(Num_of_units))

def func_LR(x, a, b):  # Curve fitting for LR = f (power)
    return a*(x**b)

xData_LR = [power_large_ref,  power_SMR_ref, power_micro_ref]
yData_LR = [LR_large_reactor , LR_SMR, LR_tot_micro]
popt_lr_, _ = curve_fit(func_LR, xData_LR   ,yData_LR)

def LR_for_power(P):
    return popt_lr_[0] *(P**popt_lr_[1])

#### OCC Cost ######
# ref: https://www.osti.gov/biblio/2371533

OCC_large_conservative_BOAK = 7750 # USD/kW
OCC_large_moderate_BOAK = 5750 # USD/kW
OCC_large_advanced_BOAK = 5250 # USD/kW


# SMR
OCC_SMR_conservative_BOAK = 10000 # USD/kW
OCC_SMR_moderate_BOAK = 8000 # USD/kW
OCC_SMR_advanced_BOAK = 5500 # USD/kW

# Since the cost if from the Gain report is 2nd of a kind cost, I convert it to first of a kind cost (assuming learning rate)
# OCC_SMR_conservative_FOAK = OCC_SMR_conservative / (    (1 - LR_SMR )**(np.log2(2))   )

#Microreactors\n# from the lit review : https://www.osti.gov/biblio/1986466: Table 17 (scaled data) only OCC. The data that had the financing cost were excluded
# # all of them are multuplied by (inflation multuplier from 2019 to 2022) 

# # Inflation Multiplier from 2019 to 2022: https://fred.stlouisfed.org/series/GDPDEF#0
inf_mult_19_22 = 117.965/104.004 # you need to multiply by the multiper for inflation first: inf_mult_19_22 

OCC_micro_conservative_BOAK = 17000*inf_mult_19_22  # USD/kW
OCC_micro_moderate_BOAK = 13000*inf_mult_19_22  # USD/kW
OCC_micro_advanced_BOAK = 8000*inf_mult_19_22  # USD/kW


# now lets do curve fitting\n
def boak_occ_func(x, a, b):  
    return a*(x**b)

xdata1_OCC = [ power_large_ref, power_large_ref,power_large_ref,\
    power_SMR_ref,power_SMR_ref,power_SMR_ref,
    power_micro_ref,power_micro_ref,power_micro_ref  ]

ydata1_OCC = [ OCC_large_conservative_BOAK , OCC_large_moderate_BOAK, OCC_large_advanced_BOAK,\
    OCC_SMR_conservative_BOAK, OCC_SMR_moderate_BOAK,  OCC_SMR_advanced_BOAK ,\
        OCC_micro_conservative_BOAK, OCC_micro_moderate_BOAK, OCC_micro_advanced_BOAK]

popt_OCC, _ = curve_fit(boak_occ_func, xdata1_OCC , ydata1_OCC)



def occ_for_power_BOAK(P):
    # A function that calculates the BOAK OCC
    return popt_OCC[0] *(P**popt_OCC[1]) # $/kw


def occ_for_power_FOAK(P):
    # A function that calculates the FOAK OCC from the BOAK
    lr = LR_for_power(P)
    BOAK_cost = occ_for_power_BOAK(P)
    FOAK_cost = BOAK_cost / (    (1 - lr )**(np.log2(2))   )
    return FOAK_cost 


def occ_for_power_FOAK_thermal(P_th):
    # A function that calculates the FOAK OCC from the BOAK

    # assuming that the efficiency is 35%
    # electric power is 0.35 * thermal power
    P = 0.35*P_th
    lr = LR_for_power(P)
    BOAK_cost = occ_for_power_BOAK(P)
    FOAK_cost = BOAK_cost / (    (1 - lr )**(np.log2(2))   )

    # Accoding to the https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_107010.pdf (sectiomn 8.3.1), the OCC should be reduced for heat application
    # The multiplier is 0.795
    
    return 0.795*FOAK_cost 


# ref: https://www.osti.gov/biblio/2371533

OM_large_conservative = 40 # USD/MWh
OM_large_moderate = 35 # USD/MWh
OM_large_advanced = 26 # USD/MWh

OM_SMR_conservative = 41# USD/MWh
OM_SMR_moderate = 30 # USD/MWh
OM_SMR_advanced = 27 # USD/MWh

# REf: https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_66425.pdf
# inflation  multiplier is appled
OM_micro_conservative = 135*inf_mult_19_22  # USD/MWh
OM_micro_moderate = 100*inf_mult_19_22  # USD/MWh
OM_micro_advanced = 70*inf_mult_19_22  # USD/MWh


def func_OM(x, a, b):  # Curve fitting for O&M cost = f (power)
    return a*(x**b)


xdata_OM = [ power_large_ref, power_large_ref,power_large_ref,\
    power_SMR_ref,power_SMR_ref,power_SMR_ref,
    power_micro_ref,power_micro_ref,power_micro_ref  ]

ydata_OM = [ OM_large_conservative , OM_large_moderate, OM_large_advanced,\
    OM_SMR_conservative, OM_SMR_moderate,  OM_SMR_advanced ,\
        OM_micro_conservative, OM_micro_moderate, OM_micro_advanced]

popt_OM, _ = curve_fit(boak_occ_func, xdata1_OCC , ydata1_OCC)


popt_OM, _ = curve_fit(func_OM, xdata_OM  , ydata_OM) # This is O&M cost fitting for FOAK reactor


def OM_for_power_one_unit(P):
    # A function that calculates O&M cost
    return popt_OM[0] *(P**popt_OM[1]) # $/kw


# The cost reduction due to building multiple units
OM_data_mult_unit = pd.read_excel('src/multi_unit.xlsx', sheet_name='Sheet3')
# X is the number of units,  Y is the cost reduction multiplier
x1_OM = OM_data_mult_unit['DOE 1987 - Num Units'].tolist()
x2_OM = OM_data_mult_unit['# of Units: NEI'].tolist()
x3_OM = OM_data_mult_unit['number of units:ICONE 2008'].tolist()
x_mult_unit = x1_OM + x2_OM + x3_OM

y1_OM = OM_data_mult_unit['BECHTEL 1987'].tolist()
y2_OM = OM_data_mult_unit['NEI 2023'].tolist()
y3_OM = OM_data_mult_unit['Carelli 2008'].tolist()
y_mult_unit = y1_OM + y2_OM + y3_OM

# remove nan values
x_mult_unit_clean = [x for x in x_mult_unit if str(x) != 'nan']
y_mult_unit_clean = [x for x in y_mult_unit if str(x) != 'nan']




"""
the cumulative cost multiplier is assumed to follow https://www.osti.gov/servlets/purl/6511284 (table 4.24): "case 3"
assumption u have a cost fraction that does not scale (a) and the remaning cost (1-a) increasese linearly with the number of units
total cost = a + (1-a) * number of units
cost per unit = a /number of units   + (1-a)
"""
def OM_multiple(x, a):  # Curve fitting for O&M cost cost reduction factor = f (number of units)
    return (a/x) + 1-a

popt_OM_multiple, _ = curve_fit(OM_multiple, x_mult_unit_clean  ,y_mult_unit_clean) 



def OM_cost_per_MWh(power, number_of_units):
    if power == 0:
        return 0
    else:
        OM_cost_one_unit = OM_for_power_one_unit(power)
        OM_cost_reduction_factor = (popt_OM_multiple[0]/number_of_units) + 1-popt_OM_multiple[0]
        OM_cost_multiple_units = OM_cost_one_unit * OM_cost_reduction_factor
        return  OM_cost_multiple_units # O&M cost for all the units ($/MWh)

def OM_cost_per_MWh_thermal(power_thermal, number_of_units):
    
    # assuming that the power (electric) = 0.35 * thermal power
    power = 0.35*power_thermal
    if power == 0:
        return 0
    else:
        OM_cost_one_unit = OM_for_power_one_unit(power)
        OM_cost_reduction_factor = (popt_OM_multiple[0]/number_of_units) + 1-popt_OM_multiple[0]
        OM_cost_multiple_units = OM_cost_one_unit * OM_cost_reduction_factor
        
        # According to https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_107010.pdf (sec 8.3.1), the cost is 0.966 less
        return   0.966*OM_cost_multiple_units # O&M cost for all the units ($/MWh) # note that this is the cost per MWh electric

##### Construction Duration #####

# Data from: https://inldigitallibrary.inl.gov/sites/sti/sti/Sort_107010.pdf

cons_duration_large_conservative = 125 #(months)
cons_duration_large_moderate     = 82 #(months)
cons_duration_large_advanced     = 60 #(months)

cons_duration_SMR_conservative = 71 #(months)
cons_duration_SMR_moderate = 55 #(months)
cons_duration_SMR__advanced = 43 #(months)


# ref: https://www.nei.org/CorporateSite/media/filefolder/resources/reports-and-briefs/Road-map-micro-reactors-department-defense-201810.pdf
# check page 9: "Thus, it is estimated that on-site construction for the first microreactor can be performed in 18 months to 36 months, with a nominal target of 24 months."
cons_duration_micro_conservative = 36 #(months) 
cons_duration_micro_moderate = 24 #(months) 
cons_duration_micro_advanced = 18  #(months) 

# Curve fitting

def func_construction(x, a, b):  # Curve fitting for construction duration = f( power)
    return a*(x**b)
xData_duration = [ power_large_ref, power_large_ref, power_large_ref,  power_SMR_ref, power_SMR_ref, power_SMR_ref, power_micro_ref,  power_micro_ref,  power_micro_ref ]
yData_duration = [cons_duration_large_conservative ,cons_duration_large_moderate ,cons_duration_large_advanced ,\
    cons_duration_SMR_conservative , cons_duration_SMR_moderate , cons_duration_SMR__advanced,\
        cons_duration_micro_conservative, cons_duration_micro_moderate , cons_duration_micro_advanced ]

popt_construction, _ = curve_fit(func_construction, xData_duration   ,yData_duration)


def construction_duration_for_power_BOAK(P):
    if P == 0:
        return 0
    else:
        return popt_construction[0] *(P**popt_construction[1])



def  construction_duration_for_power_FOAK(P):
    # A function that calculates the FOAK construction duration from the BOAK
    lr = LR_for_power(P)
    BOAK_duration = construction_duration_for_power_BOAK(P)
    FOAK_duration = BOAK_duration / (    (1 - lr )**(np.log2(2))   )
    return FOAK_duration



 
##### Fuel Cycle: Fuel cycle length   && refueling duration
    
def refueling_duration_estimate(reactor_power):
    # For now, assume that the refueling duration is always 4 weeks and not a runction of reactor power 
    if reactor_power > 0:
        return 4

"""
fuel lifetime: 
for reactors of capacities larger than or equal to 200, it would be 24 months (2 years) because:
new large reactors are expected to have 24 cycle length. SMRs such as NuSclae and BWXT have 24 fuel cycle lengh
We use the microreactor of Radiant as a reference (1MW, 5 year interval) and interpolate between 1 MW to 200 MW to estimate the fuel length 
"""
# first step: curve fitting between 1 and 200 MW
def func_refueling_interval(x, a, b): 
    return a*(x**b)

xData_refuel_interval = [ 1, 200 ] # MW 
yData_refuel_interval = [5, 2] # the refueling intervals 5 years and 2 years 
popt_refuel_interval, _ = curve_fit(func_refueling_interval, xData_refuel_interval   , yData_refuel_interval)



def fuel_cycle_length(reactor_power): 
    # if power is smaller than 200, the inerval is 2 years    
    if reactor_power >= 200 and reactor_power <= 1000:
        lifetime_weeks = int(np.floor(2*365/7)) # weeks (2 years)
        
    elif reactor_power< 200 and reactor_power >= 1:
        lifetime = popt_refuel_interval[0] *(reactor_power**popt_refuel_interval[1]) # in years
        lifetime_weeks = int(np.floor(lifetime*365/7)) # in weeks
         
    return lifetime_weeks    # Total cycle length in weeks



# specify colors for each power (for plotting)
def color_of(power):
    pwr_list = [1000, 500, 300, 200, 100  ,50, 20, 5, 1]
    colors_list = ['tab:brown' ,'b', 'g', 'r', 'c', 'm', 'y', 'k', 'tab:orange']
    for i in range (len(pwr_list)):
        if power == pwr_list[i]:
            the_color = colors_list[i]
    return the_color



# to create a list of capacities that are repeated N times.
def repeat_elements(elements, counts):
    result = []
    for element, count in zip(elements, counts):
        result.extend([element] * count)
    return result
