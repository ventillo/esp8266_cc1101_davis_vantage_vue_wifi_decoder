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
- a couple wires, need to solder those tiny CC1101 pins and wires.
- 5V / 3.3V source, depending on what version of ESP you get. A stable 3.3V is preferred

##Quick setup of HW:
###1. Interconnect these pins:
The pins are marked on the NodeMcu ESP8266, on the CC1101 module, pins are counted from left, if you face the chip towards you.

ESP8266 | ESP8266 description | CC1101    | CC1101 description |
|-------|---------------------|-----------|--------------------|
|GND    | GND                 | 1- GND    | GND                |
|3V3    | Voltage In          | 2- VCC    | Vcc, Input voltage |
|D7     | GPIO13              | 3- Pin3   | MOSI               |
|D5     | GPIO14              | 4- Pin4   | SCLK               |
|D6     | GPIO12              | 5- Pin5   | MISO               |
|-      | -                   | 6- Pin6   | GDO2               |
|-      | -                   | 7- Pin7   | GDO0               |
|D8     | GPIO15              | 8- Pin8   | CSN                |

IO pin GDO0, currently configured as interrupt, when new packet is received (i.e. goes HIGH).
This currently just to lights up a led, interrupt based receive is not implemented, though sounds cool.

###2. Clone this repo, get Micropython
```
git clone https://bastart.spoton.cz/git/Ventil/esp8266_CC1101_davis_vantage_vue.git
cd esp8266_CC1101_davis_vantage_vue
wget https://micropython.org/resources/firmware/esp8266-20191220-v1.12.bin -P /tmp
```
###3. Upload Micropython, check
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
Exit from the console with Ctrl + A + X or ampy will not be able to list files
on the esp8266
###4. Freeze modules, or just upload the .mpy files
You can simply upload all the modules in question. If you modify anything in the .py
files, you need to freeze them again with mpy-cross <filename>
```
/usr/bin/ampy -p /dev/ttyUSB1 put WiFi.mpy
/usr/bin/ampy -p /dev/ttyUSB1 put cc1101_davis.mpy
/usr/bin/ampy -p /dev/ttyUSB1 put davis_decode.mpy
```

to freeze a module:
```
mpy-cross WiFi.py
ls -l WiFi.*
WiFi.mpy <-- the newly compiled (frozen) module
WiFi.py

```
###5. Modify inet.conf
Before uploading the inte.conf, please change it to your desired values.
###6, Upload files
```
/usr/bin/ampy -p /dev/ttyUSB1 put boot.py
/usr/bin/ampy -p /dev/ttyUSB1 put main.py
/usr/bin/ampy -p /dev/ttyUSB1 put inet.conf

/usr/bin/ampy -p /dev/ttyUSB1 ls
/WiFi.mpy
/boot.py
/cc1101_davis.mpy
/davis_decode.mpy
/inet.conf
/main.py

```
###7. If you haven't already, create 2 DBs in inclux
I am tempted to push the raw, undecoded data to a DB as well, but influx is not siutd for this. You can ignore the last DB creation
```
ssh 192.168.1.2
influx
create database weather
create database status
create database raw
```
###8. Restart esp8266, check data on serial
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
>>>
>>>
>>>
>>>
>>>
>>>
>>>
>>>
>>>
>>>
>>> {ll��|�#�o

              �
               $�
                 c|����|#�
                          #��nN�$oN���
                                      bp��$sl{lp�o�
                                                   �l


                                                     "
                                                      N�|�l

                                                           #��nN�$��l`�Nl or���N

                                                                                �
                                                                                 �$p�n�
                                                                                       r�ܜ�

                                                                                           bn�|$
                                                                                                ��
                                                                                                  #��on�
                                                                                                        l �n$�$`n{�ےo
                                                                                                                     l �o

                                                                                                                         ��#�ol�
                                                                                                                                ��no��{lp�o�

 r�����
       �p�
          #
           N�|��p��on�l�l �n$�$`nr����
                                      $l`{��n
                                             l$ ���o�r��n|�ll$d`#���r�l�o��o�l ��r�$�$�
                                                                                       l`��r�p��l�

                                                                                                  $`���o�l���
                                                                                                             l$`sl��b���#
                                                                                                                         ��B|
                                                                                                                             $b���#|����l$b��n��Trying... 15 more times
Trying... 14 more times
Trying... 13 more times
Trying... 12 more times
Trying... 11 more times
Trying... 10 more times
IPCONF: {'ip': '192.168.1.174', 'mask': '255.255.255.0', 'gw': '192.168.1.254', 'dns': '192.168.1.4'}
    0    10     4    35     8     4    78   196   255   255  HOP: 0     RSSI: -71.5 LQI: 127
Header: {'bat_low': 0, 'packet_id': 0, 'davis_id': 0} Wind: {'speed': 16.1, 'direction': 5.6}
False: False/False (False)
DATA SEND FAIL: ERROR measurement set False
  224    10   234    17     1     4    38    49   255   255  HOP: 1     RSSI: -70   LQI: 127
Header: {'bat_low': 0, 'packet_id': 14, 'davis_id': 0} Wind: {'speed': 16.1, 'direction': 327.6}
rain: value/17.0 ({'type': 'rain_bucket_tips'})
DATA SEND: 204
   80     9   224   255   113    15    89   230   255   255  HOP: 2     RSSI: -70   LQI: 127
Header: {'bat_low': 0, 'packet_id': 5, 'davis_id': 0} Wind: {'speed': 14.5, 'direction': 313.6}
rain: value/0.0 ({'type': 'rainrate'})
DATA SEND: 204
  128     8   252    34   233    10   229   180   255   255  HOP: 3     RSSI: -70   LQI: 127
Header: {'bat_low': 0, 'packet_id': 8, 'davis_id': 0} Wind: {'speed': 12.9, 'direction': 352.8}
temphumi: temperature/13.3 ({'type': 'external'})
DATA SEND: 204
  160     8   249   109    41     2   202    57   255   255  HOP: 4     RSSI: -69   LQI: 127
Header: {'bat_low': 0, 'packet_id': 10, 'davis_id': 0} Wind: {'speed': 12.9, 'direction': 348.6}
temphumi: humidity/62.1 ({'type': 'external'})
DATA SEND: 204
  224     9   225    17     1     2   182    58   255   255  HOP: 0     RSSI: -68   LQI: 127
Header: {'bat_low': 0, 'packet_id': 14, 'davis_id': 0} Wind: {'speed': 14.5, 'direction': 315.0}
rain: value/17.0 ({'type': 'rain_bucket_tips'})
DATA SEND: 204
   80    10   241   255   115    10   236   224   255   255  HOP: 1     RSSI: -68.5 LQI: 127
Header: {'bat_low': 0, 'packet_id': 5, 'davis_id': 0} Wind: {'speed': 16.1, 'direction': 337.4}
rain: value/0.0 ({'type': 'rainrate'})
DATA SEND: 204
  128    16   233    34   219    10    39   214   255   255  HOP: 2     RSSI: -68.5 LQI: 127
Header: {'bat_low': 0, 'packet_id': 8, 'davis_id': 0} Wind: {'speed': 25.7, 'direction': 326.2}
temphumi: temperature/13.2 ({'type': 'external'})
```
And with '_DEBUG' set to False on line 7, in main.py:
You can see the raw data that are comming in from the Davis weather station.

```
>>>
MPY: soft reboot
Trying... 15 more times
    0    17   244   212   193   138    98    76   255   255  HOP: 0     RSSI: -68   LQI: 127
  224    13     3    17     3     3    32   253   255   255  HOP: 1     RSSI: -68.5 LQI: 127
   80    13     5   255   112     2    10   211   255   255  HOP: 2     RSSI: -68   LQI: 127
  128     9   236    34   203     2   181   206   255   255  HOP: 3     RSSI: -68.5 LQI: 127
  160    11   252   106    43     2   123    92   255   255  HOP: 4     RSSI: -69   LQI: 127
  224    13   247    17     3     6    37   228   255   255  HOP: 0     RSSI: -68.5 LQI: 127
   80    12     6   255   113     2     8   111   255   255  HOP: 1     RSSI: -69   LQI: 127
  128     9   239    34   203     3    62    51   255   255  HOP: 2     RSSI: -70   LQI: 127
   32     8   232   212   195   128    93   215   255   255  HOP: 3     RSSI: -70.5 LQI: 127
  224     6   239    17     3     3     7   218   255   255  HOP: 4     RSSI: -69.5 LQI: 127
   80     7   237   255   115     7    72   162   255   255  HOP: 0     RSSI: -69   LQI: 127
  128     9    14    34   203     0   252    14   255   255  HOP: 1     RSSI: -68.5 LQI: 127
```

If you are interested in the packet format, please:
```
  Header byte0  byte1 byte2 byte3 byte4 byte5 byte6 byte7 byte8 Freq       Sig_strength Link_quality
  224    13     3     17    3     3     32    253   255   255   HOP: 1     RSSI: -68.5  LQI: 127
```

###9, explore data in Influx
You're all set, let's look at the data
```
ssh 192.168.1.2
influx
> use weather
Using database weather
> select * from wind where time > now() - 1m group by type
name: wind
tags: type=direction
time                davis_id value
----                -------- -----
1590755264047546640 0        23.8
1590755266495686261 0        12.6
1590755269170611760 0        315
1590755271670765583 0        4.2
1590755274297615725 0        340.2
1590755276695612090 0        351.4
1590755279347820779 0        14
1590755282048791933 0        14
1590755284420807397 0        5.6
1590755287147874950 0        5.6
1590755289521471177 0        25.2
1590755292271754999 0        323.4
1590755294748104920 0        351.4
1590755297195883784 0        350
1590755302322174318 0        330.4
1590755317723159515 0        333.2
1590755320496027169 0        341.6

name: wind
tags: type=speed
time                davis_id value
----                -------- -----
1590755264047546640 0        20.9
1590755266495686261 0        20.9
1590755269170611760 0        16.1
1590755271670765583 0        25.7
1590755274297615725 0        24.1
1590755276695612090 0        22.5
1590755279347820779 0        24.1
1590755282048791933 0        22.5
1590755284420807397 0        20.9
1590755287147874950 0        17.7
1590755289521471177 0        20.9
1590755292271754999 0        22.5
1590755294748104920 0        19.3
1590755297195883784 0        22.5
1590755302322174318 0        20.9
1590755317723159515 0        11.3
1590755320496027169 0        12.9

name: wind
tags: type=windgust
time                davis_id value
----                -------- -----
1590755279347820779 0        25.7494
```
### Optionally, get grafana to plot the graphs for you
