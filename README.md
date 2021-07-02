# NOERA | Robot Odrive Arm

## Odrive Configuration

### Abstraction Layer

The `odrv_wrapper.py` contains a class which abstracts away the abstraction of the odrive interface.

### Axes Mapping

#### X Axis
Odrive `3762364A3137`, axis 0. This is the motor parallel to the top of the arm that swings it left to right

#### Y Axis
Odrive `208037743548`, axis 1. This is the motor motor running through the gear, responsible for moving the end of the arm up and down

#### Z Axis
Odrive `208037743548`, axis 0. This is the motor running the solid arm attachment in the middle, moves it end of the arm back, and forwards, and a bit up and down.

## Setup

First of all, you need to install Anaconda (python version of NVM) so we can get the correct packages and version of python.

> You need anaconda in path

Once it is installed, open up a new shell and cerate an ENV for odrive using:

```
conda create -n odrive python=3.8
```

Now enter the anaconda environment, this overrides your current shells environment variables with the correct python version:

```
conda activate odrive
```
Now install the odrive package

> The latest is `0.5.2`, but there is a [regression that freezes odrive when you connect more than one](https://github.com/odriverobotics/ODrive/issues/591)

```
pip install odrive==0.5.1
```

Now read the OS specific instructions to finish the setup

### Linux Finalization

Check you have permission to use the USB ports if you haven't directly accessed a usb device before, in debian based OS's this means adding yourself to the `dialout` group.

One simple command for them debian users.

```
sudo adduser $USER dialout
```

You are done, make sure you are able to plug in the 2 USB cables and Power cords, start the CLI tool and make sure both ODrives connect.

```
odrivetool
```

## Windows finalization

> Good Luck.

The first thing you need to do is to override the default drivers, this is based off this [forum](https://discourse.odriverobotics.com/t/exception-in-thread-thread-1/1136/3).

One device at a time, needed for both devices:

> Use the [Zadig](https://zadig.akeo.ie/) utility to set ODrive driver to libusb-win32.
Check ‘List All Devices’ from the options menu, and select ‘ODrive 3.x Native Interface (Interface 2)’. With that selected in the device list choose ‘libusb-win32’ from the target driver list and then press the large ‘install driver’ button.

Now, in theory, with a fair sprinklings of luck, it will work. Activate the Anaconda ODrive enviroment, and run:

```
odrivetool
```
You should see both odrive connect.