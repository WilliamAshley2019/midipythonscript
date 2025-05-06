# midipythonscript
This is a script I have started for reading midi sysex, and other midi information - only working as intended for midi sysex currently. The long term project goals are to get it to read midi cc, midi sysex and mmc, and allow those things to be mapped to and from midi cc, midi sysex and mmc and be detected as a midi device readable by fl studio, etc

As FL Studio only works with MIDI CC, the reason for this project is to convert my DDX3216 mmc and midi sysex information into midi cc data that is able to be interfaced with by fl studio. 

The current status is that I am able to select the midi device and read the sysex data.   

What needs to be done still is to map those sysex commands to a txt file etc.. that will store the map information that is a virtual midi device that fl studio can read.

Likewise I am trying to sort out the rs232 to usb driver functions so that the mmc data can be read and sent.
