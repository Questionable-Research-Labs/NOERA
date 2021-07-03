import odrive
from odrive.enums import *
from odrive.utils import dump_errors

import time
import sys


def setState(axis, state):
    previous_state = axis.current_state
    axis.requested_state = state
    retry_delay = 0.1
    transition_time = 0
    print("waiting for transition")
    while not (axis.current_state == state or (axis.current_state != previous_state and previous_state == AXIS_STATE_IDLE) or transition_time>2):
        time.sleep(retry_delay)
        transition_time += retry_delay
    print("waiting for idle")
    
    while not (axis.current_state == AXIS_STATE_IDLE or axis.current_state == AXIS_STATE_CLOSED_LOOP_CONTROL):
        time.sleep(retry_delay)
    check_errors(axis)
    

def check_errors(axis):
    if axis.error != 0:
        print("ERROR:")
        dump_errors(odrv_YZ, True)
        dump_errors(odrv_X, True)

        print("Quiting due to error...")
        sys.exit()

def main():
    print("finding YZ odrive...")
    odrv_YZ = odrive.find_any(serial_number="208037743548")

    print("finding X odrive...")
    odrv_X = odrive.find_any(serial_number="3762364A3137")

    print("Found, prexisting errors:")
    dump_errors(odrv_YZ, True)
    dump_errors(odrv_X, True)

    # Generic config
    # odrv_YZ.config.enable_brake_resistor = True
    odrv_YZ.config.brake_resistance = 0.4690000116825104

    # odrv_X.config.enable_brake_resistor = True
    odrv_X.config.brake_resistance = 0.4690000116825104

    # Individual setup
    # Z SETUP
    odrv_YZ.axis0.motor.config.resistance_calib_max_voltage = 5.0
    odrv_YZ.axis0.controller.config.pos_gain = 30.0
    odrv_YZ.axis0.controller.config.vel_gain = 0.35
    odrv_YZ.axis0.controller.config.vel_integrator_gain = 0.32

    # Y SETUP
    odrv_YZ.axis1.motor.config.resistance_calib_max_voltage = 2.0
    odrv_YZ.axis1.controller.config.pos_gain = 25.0
    odrv_YZ.axis1.controller.config.vel_gain = 0.25
    odrv_YZ.axis1.controller.config.vel_integrator_gain = 0.32

    # X SETUP
    odrv_X.axis0.motor.config.resistance_calib_max_voltage = 2.0
    odrv_X.axis0.controller.config.pos_gain = 30.0
    odrv_X.axis0.controller.config.vel_gain = 0.30
    odrv_X.axis0.controller.config.vel_integrator_gain = 0.32



    # user_input = input("Complete calibration? (yN)")
    user_input = "n"

    # Repeated setup for both axises
    for axis in [odrv_YZ.axis0, odrv_YZ.axis1, odrv_X.axis0]:
        print("Clearing errors from last axis:")
        dump_errors(odrv_YZ, True)
        axis.encoder.config.cpr = 8192
        axis.encoder.config.mode = ENCODER_MODE_INCREMENTAL
        axis.motor.config.motor_type = MOTOR_TYPE_HIGH_CURRENT
        axis.encoder.config.calib_range = 0.05
        axis.motor.config.calibration_current = 10.0
        axis.motor.config.resistance_calib_max_voltage = 5.0
        axis.controller.config.vel_limit = 15
        axis.controller.config.vel_limit_tolerance = 1.2000000476837158
        axis.motor.config.pole_pairs = 20
        axis.motor.config.current_lim = 20.0

        axis.trap_traj.config.vel_limit = 15
        axis.trap_traj.config.accel_limit = 10
        axis.trap_traj.config.decel_limit = 10
        # axis.<axis>.controller.config.inertia 

        
        

        axis.config.startup_closed_loop_control = True
        axis.config.startup_encoder_index_search = True
        axis.config.startup_encoder_offset_calibration = False
        axis.config.startup_homing = False
        axis.config.startup_motor_calibration = False

        check_errors(axis)

        # Start Index Incoder calibration
        if user_input.lower() == "y" or user_input.lower() == "yes":
            print("Running calibration on enter")
            input()
            axis.encoder.config.use_index = True
            print("Motor calibration")
            setState(axis,AXIS_STATE_FULL_CALIBRATION_SEQUENCE)
            axis.encoder.config.pre_calibrated = True
            axis.motor.config.pre_calibrated = True

            check_errors(axis)
            print("Finished config")

        else:
            print("Skipping calibration")

    if axis.encoder.config.pre_calibrated == False:
        print("ODrive disagrees with human about calibration before reboot")
        sys.exit()
    if user_input.lower() == "y" or user_input.lower() == "yes":
        print("Saving and rebooting YZ")
        #save and restart
        try:
            odrv_YZ.save_configuration()
            odrv_YZ.reboot()
            print("reboot failed")
            sys.exit()
        except Exception:
            print("Rebooting")

        print("Saving and rebooting YZ")
        #save and restart
        try:
            odrv_X.save_configuration()
            odrv_X.reboot()
            print("reboot failed")
            sys.exit()
        except Exception:
            print("Rebooting")

        print("reconnecting")
        print("finding YZ odrive...")
        odrv_YZ = odrive.find_any(serial_number="208037743548")

        print("finding X odrive...")
        odrv_X = odrive.find_any(serial_number="3762364A3137")
        print("Waiting for Closed Loop Control")
        time.sleep(5)

        for axis in [odrv_YZ.axis0, odrv_YZ.axis1, odrv_X.axis0]:
            while axis.current_state != AXIS_STATE_CLOSED_LOOP_CONTROL:
                time.sleep(0.1)
            dump_errors(odrv_YZ, True)
            if axis.encoder.config.pre_calibrated == False:
                print("ODrive disagrees with human about calibration")
                sys.exit()
            else:
                check_errors(axis)
                print("Good to go...")
                exit
    else:
        print("Saving")
                #save and restart
        try:
            odrv_YZ.save_configuration()
            odrv_YZ.reboot()
            print("reboot failed")
            sys.exit()
        except Exception:
            print("Rebooting")

        print("Saving and rebooting YZ")
        #save and restart
        try:
            odrv_X.save_configuration()
            odrv_X.reboot()
            print("reboot failed")
            sys.exit()
        except Exception:
            print("Rebooting")
        

if __name__ == "__main__":
    main()