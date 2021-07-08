from OdrvWrapper.odrv_wrapper import Odrive_Arm
import random

print("Initialize")
arm = Odrive_Arm()


while True:
    # Move to random point, this blocks the thread until the move is complete
    arm.move_blocking( (random.random(),random.random(),random.random()))