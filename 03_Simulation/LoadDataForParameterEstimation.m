data = load('Measurement_MassflowSensor_2021-02-13_15-13-52_StepResponseFullheatingPower.mat')
time = (data.Time - data.Time(1))';
delta_t = data.Temperature_Difference';
pwm = data.PWM';