#ESP8266 + CC1101 Davis weather station wifi logger


The intention is to gather data from a Weather station made by Davis.
In this case a Vantage Vue (integrated all sensors in one package) and
push them directly to an InfluxDB instance via WiFi.

##Prerequisites:
- WiFi available, plus access to it. (WPA2 PSK preferred)
- Running INfluxDB instance on the same network
- ESP8266 microcontroller (NodeMCU 8266 preferred)
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

###2, get Micropython
###3, Upload Micropython
###4, Freeze modules, or just upload the .mpy files
###5, Modify inte.conf
###6, Upload files
###7, Restart esp8266
###8, explore data in Influx
