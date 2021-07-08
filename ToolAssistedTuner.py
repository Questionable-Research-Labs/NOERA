from typing import Tuple
import dearpygui.dearpygui as dpg
import time
from OdrvWrapper.odrv_wrapper import Odrive_Arm
import dearpygui.logger as dpg_logger

logger = dpg_logger.mvLogger()

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

        string_value = dpg.add_string_value(default_value="Default string")

    # Generate UI
    print("Connected to Odrive")
    with dpg.window(label="ODrive Tuner", id=tuner_window,) as odrive_tuner:
        dpg.delete_item(connection_window)
        dpg.set_primary_window(odrive_tuner, True)
        with dpg.menu_bar():
            def enabled_motor_callback(sender, app_data, user_data): 
                axis_id = user_data
                if arm.axes_enabled[axis_id]:
                    arm.disable_axis(axis_id)
                else: 
                    arm.enable_axis(axis_id)
                # [x_enabled,y_enabled,z_enabled]
            for axis,store in zip(arm.axes.keys(),[x_enabled,y_enabled,z_enabled]):
                with dpg.menu(label="{} Axis".format(axis)):
                    dpg.add_checkbox(label="Motor Enabled", drop_callback=enabled_motor_callback,default_value=True,user_data=axis,source=store)
        for axis in arm.axes.keys():

            with dpg.collapsing_header(label="{} Axis".format(axis)):
                dpg.add_text(default_value="This is the motor parallel to the top of the arm that swings it left to right")
        def update_position_axes(sender, app_data):
            value: Tuple[float,float,float] = tuple(dpg.get_value(sender)[0:3])
            print("Sending Position",value)
            arm.move_async(value)
        dpg.add_3d_slider(label="Yes",max_x=1,max_y=1,max_z=1, scale=0.5,callback=update_position_axes)

        
    time.sleep(5)


# Initialize GUI

with dpg.font_registry():
    
    # add font (set as default for entire app)
    dpg.add_font("guiResources\\OpenSans-Regular.ttf", 20, default_font=True)

with dpg.window(label="CONNECT",id=connection_window) as connect_window:
    connect_button = dpg.add_button(label="Connect To Odrive", callback=generateTunningUI)
    dpg.set_primary_window(connect_window, True)
dpg.start_dearpygui()