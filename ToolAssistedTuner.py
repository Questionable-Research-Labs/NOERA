from typing import Tuple
import dearpygui.dearpygui as dpg
import time
from OdrvWrapper.odrv_wrapper import Odrive_Arm
from dearpygui.demo import show_demo
show_demo()


# logger = dpg_logger.mvLogger()

# dpg.show_documentation()
# dpg.show_style_editor()
# dpg.show_debug()
# dpg.show_about()
# dpg.show_metrics()
# dpg.show_font_manager()
# dpg.show_item_registry()

ODRIVE_LOCK = False

connection_window = dpg.generate_uuid()
tuner_window = dpg.generate_uuid()


def generateTunningUI():
    # Connect to Robot Arm

    global ODRIVE_LOCK
    global arm
    if ODRIVE_LOCK:
        print("Already Connected to Odrive")
        return
    else:
        ODRIVE_LOCK = False
        print("connecting to odrive")

    arm = Odrive_Arm(actually_connect=True)    
    # Create Value Store
    with dpg.value_registry():
        x_enabled = dpg.add_bool_value(default_value=True)
        y_enabled = dpg.add_bool_value(default_value=True)
        z_enabled = dpg.add_bool_value(default_value=True)

    axis_settings = {
        "X": [],
        "Y": [],
        "Z": []
    }

    axis_graphs = {
        "X": {
            "current":
                {
                    "time": [],
                    "current": []
                }
        },
        "Y": {
            "current":
                {
                    "time": [],
                    "current": []
                }
        },
        "Z": {
            "current":
                {
                    "time": [],
                    "current": []
                }
        }
    }

    # Generate UI
    print("Connected to Odrive")
    with dpg.window(label="ODrive Tuner", id=tuner_window,) as odrive_tuner:
        dpg.delete_item(connection_window)
        dpg.set_primary_window(odrive_tuner, True)
        with dpg.menu_bar():
            def enabled_motor_callback(sender, app_data, user_data): 
                axis_id = user_data
                print("enable disable",axis_id)
                if dpg.get_value(sender):
                    print("Enabling Axis")
                    arm.enable_axis(axis_id)
                else: 
                    print("Disabling Axis")
                    arm.disable_axis(axis_id)
                # [x_enabled,y_enabled,z_enabled]
            for axis_id,store in zip(arm.axes.keys(),[x_enabled,y_enabled,z_enabled]):
                with dpg.menu(label="{} Axis".format(axis_id)):
                    dpg.add_checkbox(label="Motor Enabled", callback=enabled_motor_callback,default_value=True,user_data=axis_id,source=store)
        for axis_id in arm.axes.keys():

            with dpg.collapsing_header(label="{} Axis".format(axis_id)):
                dpg.add_text(default_value=arm.axes_descriptions[axis_id])
                with dpg.table(header_row=True):
                    tunning_labels=["Pos Gain","Vel Gain","Vel Integrator Gain","Vel Limit","Motor Current"]
                    for i in tunning_labels:
                        dpg.add_table_column(label=i)
                    axis = arm.axes[axis_id]
                    contr_config = axis.controller.config
                    default_values = [contr_config.pos_gain,contr_config.vel_gain,contr_config.vel_integrator_gain,contr_config.vel_limit,axis.motor.config.current_lim]
                    for i in range(len(tunning_labels)):
                        axis_settings[axis_id].append(
                            dpg.add_input_float(label="", default_value=default_values[i])
                            )
                        dpg.add_table_next_column()
                def set_config_button_callback(sender, app_data, user_data):
                    axis_config = arm.axes[user_data]
                    contr_config = axis_config.controller.config
                    input_values = []
                    for i in range(5):
                        input_values.append(
                            dpg.get_value(
                                axis_settings[user_data][i]
                                )
                            )
                    contr_config.pos_gain = input_values[0]
                    contr_config.vel_gain = input_values[1]
                    contr_config.vel_integrator_gain = input_values[2]
                    contr_config.vel_limit
                    axis_config.motor.config.current_lim

                dpg.add_button(label="Set Configuration",user_data=axis_id,callback=set_config_button_callback)
                def start_graphs_button_callback(sender, app_data, user_data):
                    arm.start_current_plot(axis_id=user_data)
                    arm.start_pos_plot(axis_id=user_data)
                dpg.add_button(label="Start Graphs",user_data=axis_id,callback=start_graphs_button_callback)

                # with dpg.collapsing_header(label="Info Graphs"):
                #     with dpg.plot(arm.axes[axis_id].motor.current_control.Iq_setpoint, arm.axes[axis_id].motor.current_control.Iq_measured,label="Current Pull from motor"):
                #         dpg.add_plot_axis(dpg.mvXAxis, label="x")
                #         dpg.add_plot_axis(dpg.mvYAxis, label="y")
                #         dpg.add_line_series([], [], label="0.5 + 0.5 * sin(x)", parent=dpg.last_item())
                

                
        def update_position_axes(sender, app_data):
            value: Tuple[float,float,float] = tuple(dpg.get_value(sender)[0:3])
            print("Sending Position",value)
            arm.move_async(value)
        dpg.add_3d_slider(label="Control all 3 axis in a 3D Slider",max_x=1,max_y=1,max_z=1, scale=0.5,callback=update_position_axes)

# Initialize GUI

with dpg.font_registry():
    
    # add font (set as default for entire app)
    dpg.add_font("guiResources\\OpenSans-Regular.ttf", 20, default_font=True)

with dpg.window(label="CONNECT",id=connection_window) as connect_window:
    connect_button = dpg.add_button(label="Connect To Odrive", callback=generateTunningUI)
    dpg.set_primary_window(connect_window, True)
dpg.start_dearpygui()