% Constants
std_air_density = 1.2922 % kg m^-3
std_temperature = 20 % degree celcius
std_pressure = 1.013 % bar
air_dynamic_viscosity = 18.5e-6 % Pa s
min_reynolds_number = 2000 %
cp_air = 1006 %joule kg^-1 K^-1
% Dimensions
pipe_length = 0.15 % m
pipe_diameter = 0.4 % m
target_delta_T = 6 % degree celsius
f_min = 0.3 %
% Factors
massflow_SI_to_slm = 1/std_air_density*1000*60
% MFC
max_massflow_slm = 100
max_massflow_SI = max_massflow_slm/massflow_SI_to_slm
