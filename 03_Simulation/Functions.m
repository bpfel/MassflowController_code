Model_Parameters;

powers = [24, 48, 72];
for power=powers
    flow_percentages = 0.3:0.01:1
    hold on;
    plot(flow_percentages, delta_t_max(power, flow_percentages))
end
legend({'24W', '48W', '72W'})
    

function flow_vel = flow_velocity(massflow_SI)
    crosssection = pipe_diameter*pipe_diameter/4*pi
    flow_vel = massflow_SI/(std_air_density*crosssection)
end

function pow = heater_power(massflow_SI, delta_T)
    pow = cp_air*delta_T*massflow_SI
end

function Re = reynolds_number(flow_velocity, diameter)
    Re = std_air_density*flow_velocity*diameter/air_dynamic_viscosity
end

function t_d = time_delay(flow_velocity)
    t_d = pipe_length/flow_velocity
end

function dt_max = delta_t_max(power, flow_percent)
    Model_Parameters;
    actual_flow = max_massflow_SI*flow_percent
    dt_max = power/cp_air./actual_flow
end

