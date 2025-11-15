# Frequently Asked Questions

## Do I need a hacked or modified Switch?

No! This project is intended for retail (unmodified) Switches. You do not need a hacked Switch.

However, if you do have a hacked Switch, you can skip the microcontroller since we support sys-botbase as a controller setup.

Otherwise, having a hacked Switch will not provide any additional functionality. We do not support accessing game or system memory or anything that cannot be done with a manual controller.

In short, we are not a hacking group and we prefer to keep our distance from the hacking community.


## Does this work on the Switch 2?

Yes! We have had full support for the Switch 2 since version 0.56.


## Is there any ban risk of this project?

To date, there are no known cases of anyone getting banned for using capture cards and 3rd party controllers.


## Can I use a Raspberry Pi instead of a computer?

(not to be confused with the Raspberry Pi Pico as a controller)

No. Video inference and machine learning are extremely compute intensive and have difficulty running on even slightly old laptops. You will need a powerful computer.

Furthermore, the project is large enough as it is and we need to draw the line somewhere.


## Can I use a phone or a tablet instead of a computer?

No. Same reason as above.


## Why can't you connect directly to the Switch over USB? Why do you need a microcontroller?

There are 2 categories of USB devices, "host" or "device".

- A game controller is a USB device.
- A computer's USB port is a USB host.

Unfortunately, a computer's USB port cannot be reprogrammed as a USB device. Thus you need to use a microcontroller board that acts as a USB device to both the computer and the Switch.


## Why can't you connect directly to the Switch using the computer's Bluetooth? NXBT and joycontrol can do this!

NXBT and joycontrol are both Linux only. Windows and Mac require the use of a VM which is well above the difficulty threshold for our target audience.

Linux is the only operating system that allows the low level access required to reprogram the bluetooth device to act as a wireless game controller. To do this on Windows, you would need a custom driver for the specific Bluetooth device. And we're not in the business of writing (signed) custom drivers for every Bluetooth controller on the market.

Beyond this, there are concerns about timing stability. Unlike microcontrollers, computers have much more noise due to background programs.


## I'm an old user returning after a long absence. Is my Arduino/Teensy still good?

Yes and no.

We still support the old setups (Arduino/Teensy/Pro Micro), but they are deprecated in favor of the newer controllers (ESP32, ESP32-S3, Raspberry Pi Pico W).

- If you are coming from the old "microcontroller-only" programs, you will need to purchase and setup a UART. But in this case, it's much easier and cheaper to just to abandon your old hardware and get one of the newer controller setups which do not require a UART.
- If you are coming from the older computer-control setups and already have a UART, you can continue using it. But if you have any difficulty setting it up, we are going to tell you to just abandon it and get the newer controllers.

The newer controllers are cheaper, much easier to setup, and more reliable than the old ones with manual UART wiring.




<hr>

**Discord Server:** 

[<img src="https://canary.discordapp.com/api/guilds/695809740428673034/widget.png?style=banner2">](https://discord.gg/cQ4gWxN)




