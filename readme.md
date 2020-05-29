ESP8266 + CC1101 Davis weather station wifi logger
--------------------------------------------------

The intention is to gather data from a Weather station made by Davis.
In this case a Vantage Vue (integrated all sensors in one package) and
push them directly to an InfluxDB instance via WiFi.

Prerequisites:
==============
- WiFi available, plus access to it. (WPA2 PSK preferred)
- Running INfluxDB instance on the same network
- ESP8266 microcontroller (NodeMCU 8266 preferred)
- CC1101 from Texas Instruments radio chip, the 868 MHz version! There are 433Mhz sold out there, read descriptions
- a couple wires
- 5V / 3.3V source, depending on what version of ESP you get. A stable 3.3V is preferred

Quick setup of HW:
==================
1, Interconnect these pins:

