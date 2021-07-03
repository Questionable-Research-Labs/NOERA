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

    valid_movement_range = {
        "X": (-0.3, 0.1),
        "Y": (-0.3, 0),
        "Z": (-0.20, 0)
    }

    # Generates and Odrive Arm Object, that automatically connects to the odrive
    def __init__(self):
        """
        Setup the odrive, don't worry, black magic fuckery
        """
        self._connect_to_odrive()
        self._reset_odrive()

    # Configures all axes for fancy trajectory movement
    def _configure_for_trajectory(self):
        """
        Setup the configure all axes for movement
        """
        self.check_errors()
        for axis in self.axes.values():
            axis.controller.config.input_mode = INPUT_MODE_TRAP_TRAJ

    def _reset_odrive(self):
        self.check_errors()
        # If there is an error, it configures it back to idle
        for axis_id in self.axes:
            self._set_state(axis_id, AXIS_STATE_CLOSED_LOOP_CONTROL)
            self.axes[axis_id].controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
        time.sleep(0.1)
        # Back to Zero Zero we go
        self.move((0.5, 0.5, 0.5))

        self._configure_for_trajectory()

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
                print(axis.error)
                print("Checking YZ")
                dump_errors(self.odrv_YZ, True)
                print("Checking X")

                dump_errors(self.odrv_X, True)

                print("Quiting due to error...")
                sys.exit()

    def move_axis(self, axis_id: str, pos: float):
        """
        Move the selected axis to a certain position
        """
        self.check_errors()
        assert axis_id in self.axes
        scaled_pos = self._convert_to_odrive_units(axis_id,pos)
        self.axes[axis_id].controller.input_pos = scaled_pos

    def move(self, pos: Tuple[float, float, float]):
        scaled_pos: Tuple[float, float, float] = tuple(map(
            lambda axis_id_and_pos:
                self._convert_to_odrive_units(
                    list(self.valid_movement_range.keys())[axis_id_and_pos[0]],
                    axis_id_and_pos[1]
                ),
            enumerate(list(pos))
        ))
        self.check_errors()
        self.axes["X"].controller.input_pos = scaled_pos[0]
        # TODO: Supposed to be zero? 0_0
        self.axes["Y"].controller.input_pos = scaled_pos[1]
        self.axes["Z"].controller.input_pos = scaled_pos[2]
    
    def move_blocking(self, pos: Tuple[float, float, float]):
        scaled_pos: Tuple[float, float, float] = tuple(map(
            lambda axis_id_and_pos:
                self._convert_to_odrive_units(
                    list(self.valid_movement_range.keys())[axis_id_and_pos[0]],
                    axis_id_and_pos[1]
                ),
            enumerate(list(pos))
        ))
        self.check_errors()
        self.axes["X"].controller.input_pos = scaled_pos[0]
        # TODO: Supposed to be zero? 0_0
        self.axes["Y"].controller.input_pos = scaled_pos[1]
        self.axes["Z"].controller.input_pos = scaled_pos[2]

        while not self._check_trajectory_done():
            time.sleep(0.05)


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

    def _convert_to_odrive_units(self, axis_id: str, input_pos: float) -> float:
        assert input_pos >= 0 and input_pos <= 1
        assert axis_id in self.axes

        (axis_min, axis_max) = self.valid_movement_range[axis_id]
        axis_range = axis_max-axis_min
        input_scaled = input_pos*axis_range + axis_min

        return input_scaled
    
    def _check_trajectory_done(self) -> bool:
        complete = True
        for axis_id in self.axes:
            complete = complete and self.axes[axis_id].controller.trajectory_done
            # print(axis_id,self.axes[axis_id].controller.trajectory_done)
        return complete
