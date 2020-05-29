#ESP8266 + CC1101 Davis weather station wifi logger


The intention is to gather data from a Weather station made by Davis.
In this case a Vantage Vue (integrated all sensors in one package) and
push them directly to an InfluxDB instance via WiFi.

##Prerequisites:
- WiFi available, plus access to it. (WPA2 PSK preferred)
- Running INfluxDB instance on the same network
- ESP8266 microcontroller (NodeMCU 8266 preferred)
- git, since you're here, I assume this is already settled
- Micropython tools: ampy, esptool
- serial console emulator, I use picocom
- CC1101 from Texas Instruments radio chip, the 868 MHz version! There are 433Mhz sold out there, read descriptions
- a couple wires
- 5V / 3.3V source, depending on what version of ESP you get. A stable 3.3V is preferred

##Quick setup of HW:
###1, Interconnect these pins:

ESP8266 | ESP8266 description | CC1101 | CC1101 description |
|-------|---------------------|--------|--------------------|
|GND    | GND                 | GND    | GND                |
|3V3    | Voltage In          | VCC    | Vcc, Input voltage |
|D7     | GPIO13              | Pin3   | MOSI               |
|D5     | GPIO14              | Pin4   | SCLK               |
|D6     | GPIO12              | Pin5   | MISO               |
|-      | -                   | Pin6   | GDO2               |
|LED    | -                   | Pin7   | GDO0               |
|D8     | GPIO15              | Pin8   | CSN                |

IO pin, currently configured as interrupt, when new packet is received (i.e. goes HIGH).
The functionality is currently just to light up a led, interrupt based receive is not implemented.

###2, Clone this repo, get Micropython
```
git clone https://bastart.spoton.cz/git/Ventil/esp8266_CC1101_davis_vantage_vue.git
cd esp8266_CC1101_davis_vantage_vue
wget https://micropython.org/resources/firmware/esp8266-20191220-v1.12.bin -P /tmp
```
###3, Upload Micropython, check
Need to delete the flash first, then write the custom firmware.
You need to determine which device is the one
to write to. If you have only one ESP8266, you are probably safe to use the ttyUSB0,
I will use ttyUSB1 as I have multiple UARTS on my machine
```
esptool.py --port /dev/ttyUSB1 --baud 115200  erase_flash
esptool.py v2.8
Serial port /dev/ttyUSB1
Connecting....
Detecting chip type... ESP8266
Chip is ESP8266EX
Features: WiFi
Crystal is 26MHz
MAC: cc:50:e3:56:b2:5b
Uploading stub...
Running stub...
Stub running...
Erasing flash (this may take a while)...
Chip erase completed successfully in 7.8s
Hard resetting via RTS pin...
```
Now it is time to upload uPython:
```
esptool.py --port /dev/ttyUSB1 --baud 115200 write_flash 0 /tmp/esp8266-20191220-v1.12.bin
esptool.py v2.8
Serial port /dev/ttyUSB1
Connecting....
Detecting chip type... ESP8266
Chip is ESP8266EX
Features: WiFi
Crystal is 26MHz
MAC: cc:50:e3:56:b2:5b
Uploading stub...
Running stub...
Stub running...
Configuring flash size...
Auto-detected Flash size: 4MB
Flash params set to 0x0040
Compressed 619828 bytes to 404070...
Wrote 619828 bytes (404070 compressed) at 0x00000000 in 35.8 seconds (effective 138.6 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```
And of course, when you try to get to the serial console, you should get somethinglike this
```
picocom -b 115200 /dev/ttyUSB1
picocom v3.1

port is        : /dev/ttyUSB1
flowcontrol    : none
baudrate is    : 115200
parity is      : none
databits are   : 8
stopbits are   : 1
escape is      : C-a
local echo is  : no
noinit is      : no
noreset is     : no
hangup is      : no
nolock is      : no
send_cmd is    : sz -vv
receive_cmd is : rz -vv -E
imap is        :
omap is        :
emap is        : crcrlf,delbs,
logfile is     : none
initstring     : none
exit_after is  : not set
exit is        : no

Type [C-a] [C-h] to see available commands
Terminal ready

>>>

```
###4, Freeze modules, or just upload the .mpy files
###5, Modify inte.conf
###6, Upload files
###7, Restart esp8266, check data on serial
###8, explore data in Influx

### Optionally, get grafana to plot the graphs for you
