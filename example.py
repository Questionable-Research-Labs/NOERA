from odrv_wrapper import Odrive_Arm
import time
import random

print("Initialize")
arm = Odrive_Arm()
# pos_1 = float(input("pos 1:"))
# pos_2 = float(input("pos 2:"))
x = 1

arm.axes["Y"].requested_state = 2

while True:
    # arm.move((0.1,-0.1,0.1))
    pos = (random.random(),random.random(),random.random())
    print("Times run: " + str(x) + ", pos:" + str(pos))
    arm.move_blocking(pos)

    x = x + 1
    
# at 0.5s delay it ran: 24, 32
# at 1s delay it ran: 288