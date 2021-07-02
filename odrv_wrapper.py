from configs.configureXYZ import check_errors
from typing import Dict, Tuple
import odrive
from odrive.enums import *
from odrive.utils import dump_errors
from typing import Union, Any

import sys
import time


class Odrive_Arm:
    """
    Wrapper for the two odrive controllers. Fancy.
    """
    odrv_X = None
    odrv_YZ = None
    axes: Union[Any, Dict[str, Any]] = None

    # Generates and Odrive Arm Object, that automatically connects to the odrive
    def __init__(self):
        """
        Setup the odrive, don't worry, black magic fuckery
        """
        self._connect_to_odrive()
        self._configure_for_trajectory()

    # Configures all axes for fancy trajectory movement
    def _configure_for_trajectory(self):
        """
        Setup the configure all axes for movement
        """
        self.check_errors()
        for axis in self.axes.values():
            axis.controller.config.input_mode = INPUT_MODE_TRAP_TRAJ

    # Blocking connection to both odrives.
    def _connect_to_odrive(self):
        """
        Connect to the odrive
        """
        print("finding YZ odrive...")
        self.odrv_YZ = odrive.find_any(serial_number="208037743548")

        assert self.odrv_YZ != None
        assert not isinstance(self.odrv_YZ, list)

        print("finding X odrive...")
        self.odrv_X = odrive.find_any(serial_number="3762364A3137")

        assert self.odrv_X != None
        assert not isinstance(self.odrv_X, list)

        self.axes = {
            "X": self.odrv_X.axis0,
            "Y": self.odrv_YZ.axis1,
            "Z": self.odrv_YZ.axis0
        }
        print("ODrives are connected, dumping previous errors")
        # ODrive dose not clear errors with a reconnection, and will refuse to take action until they are cleared
        print("YZ Odrive Errors:")
        dump_errors(self.odrv_YZ, True)
        print("X Odrive Errors:")
        dump_errors(self.odrv_X, True)
        print("\n\n")
        # If there is an error, it configures it back to idle
        for axis_id in self.axes:
            self._set_state(axis_id,AXIS_STATE_CLOSED_LOOP_CONTROL)
        # If it errers from a set state, then the configuration is broken
        self.check_errors()
        

    def _check_connected(self):
        """
        are the odrives connected? Are they? ANSWER ME!!
        """
        assert self.odrv_X != None
        assert not isinstance(self.odrv_X, list)

        assert self.odrv_YZ != None
        assert not isinstance(self.odrv_YZ, list)

        assert self.axes != None

    def check_errors(self):
        """
        Check to see if the odrive encountered any errors, will just eject if errors are found.
        """
        self._check_connected()
        for axis in self.axes.values():
            if axis.error != 0:
                print("ERROR:")
                dump_errors(self.odrv_YZ, True)
                dump_errors(self.odrv_X, True)

                print("Quiting due to error...")
                sys.exit()

    def move_axis(self, axis_id: str, location: float):
        """
        Move the selected axis to a certain position
        """
        self.check_errors()
        assert axis_id in self.axes
        self.axes[axis_id].controller.input_pos = location

    def move(self, pos: Tuple[float, float, float]):
        self.check_errors()
        self.axes["X"].controller.input_pos = pos[0]
        # TODO: Supposed to be zero? 0_0
        self.axes["Y"].controller.input_pos = pos[0]
        self.axes["Z"].controller.input_pos = pos[0]

    def _set_state(self, axis_id: str, state):
        """
        Blocking mode set of axis

        """
        assert axis_id in self.axes
        axis = self.axes[axis_id]

        previous_state = axis.current_state
        axis.requested_state = state
        retry_delay = 0.1
        transition_time = 0
        # print("waiting for transition")
        while not (axis.current_state == state or (axis.current_state != previous_state and previous_state == AXIS_STATE_IDLE) or transition_time > 1):
            time.sleep(retry_delay)
            transition_time += retry_delay
        # print("waiting for idle")

        while not (axis.current_state == state or transition_time > 5):
            time.sleep(retry_delay)
        check_errors(axis)
