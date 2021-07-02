from odrv_wrapper import Odrive_Arm

print("Initialize")
arm = Odrive_Arm()
x_location = float(input("Move X to:"))
arm.move((0.1,0.1,0.1))
print("Done")