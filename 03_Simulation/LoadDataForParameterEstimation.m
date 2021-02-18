data = load('Measurement_MassflowSensor_2021-02-13_15-13-52_StepResponseFullheatingPower.mat')
time = (data.Time - data.Time(1))';
delta_t = data.Temperature_Difference';
pwm = data.PWM';

% define needed workspace variables
coil_specific_heat_transfer = 20;
coil_thermal_timeconstant = 20;
coil_voltage = 20;