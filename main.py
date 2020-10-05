import cc1101_davis
import davis_decode
import utime
import WiFi
import machine
gc.collect()

#_SSID = 'BastArt'
#_PASS = '3 litry Kvasaru!'
#_TIMEOUT = 15
_DEBUG = True
#
#_INFLUX_HOST = '192.168.1.2'
#_INFLUX_PORT = '8086'
#_INFLUX_USER = 'ventil'
#_INFLUX_PASS = '3 litry Kvasaru!'
#
#_INF_DB_WEATHER = 'weather'
#_INF_DB_STATUS = 'status'
#_INF_DB_RAW = 'raw'


wifi_con = WiFi.NetSet('infra')
wifi_con.readNetworkConfig()
ips = wifi_con.connectInfra(
    wifi_con._SSID,
    wifi_con._PASS,
    wifi_con._TIMEOUT)

if _DEBUG:
    print("IPCONF: {}".format(ips))

davis = cc1101_davis.CC1101()
davis.setRegisters()
davis.setFrequency(davis.hopIndex)
decoder = davis_decode.davisDecoder(
    wifi_con._INF_DB_WEATHER,
    wifi_con._INF_DB_STATUS,
    wifi_con._INF_DB_RAW)

# Main receive loop
interpacket_time = 0
while True:
    data_length = davis.readRegister(davis.CC1101_RXBYTES)
    data = ""
    if data_length & 0x7f == 15:
        data = davis.readBurst(davis.CC1101_RXFIFO, 10)
        rssi = davis.readRssi()
        lqi = davis.readLQI()
        freqEst = davis.readStatus(davis.CC1101_FREQEST)
        freqError = davis.calcFreqError(freqEst)
        if _DEBUG:
            print("FERROR: {} (EST: {})".format(freqError, freqEst))
            print("FCOMP: {}".format(davis.freqComp))
        if davis.freqComp[davis.hopIndex] + freqEst <= 255:
            davis.freqComp[davis.hopIndex] = davis.freqComp[davis.hopIndex] + freqEst
        else:
            davis.freqComp[davis.hopIndex] = 255
        hop = davis.hopIndex
        davis.flush()
        davis.hop()
        davis.rx()
        data_int = [davis_decode.reverseBits(int(item)) for item in data]
        crc = davis.calcCrc(data_int[:8])
        if crc != 0x0000:
            print("Corrupt data CRC: {}".format(crc))
            continue
        else:
            print("Data OK, CRC: {}".format(crc))
        header = decoder.davis_id(data_int[0])
        decoder.DecodePacket(data_int)
        data_prn = "{:5} {:5} {:5} {:5} {:5} {:5} {:5} {:5} {:5} {:5}".format(
                data_int[0],
                data_int[1],
                data_int[2],
                data_int[3],
                data_int[4],
                data_int[5],
                data_int[6],
                data_int[7],
                data_int[8],
                data_int[9])
        print("{_data:60} HOP: {_hop:<5} RSSI: {_rssi:<5} LQI: {_lqi:<5} {_last}s since".format(
                _rssi=rssi,
                _hop=hop,
                _data=data_prn,
                _lqi=lqi,
                _last=interpacket_time / 10))
        if _DEBUG:
            print("Header: {} Wind: {}".format(header, decoder.wind))
            print("{}: {}/{} ({})".format(
               decoder.measurement,
               decoder.name,
               decoder.value,
               decoder.tags))
        sent_ok = False
        data_sent = None
        gc.collect()
        try:
            (sent_ok, data_sent) = davis_decode.send_to_influx(
                wifi_con._INFLUX_HOST,
                wifi_con._INFLUX_PORT,
                decoder.write_influx_db,
                wifi_con._INFLUX_USER,
                wifi_con._INFLUX_PASS,
                decoder.unit_id,
                decoder.wind,
                decoder.measurement,
                decoder.name,
                decoder.value,
                decoder.tags)
        except Exception as e:
            print("ERROR: Data send 'urequest': {}".format(e))
        try:
            (raw_sent_ok, raw_data_sent) = davis_decode.raw_send_to_influx(
                wifi_con._INFLUX_HOST,
                wifi_con._INFLUX_PORT,
                decoder.raw_influx_db,
                wifi_con._INFLUX_USER,
                wifi_con._INFLUX_PASS,
                data_int[0],
                data_int[1],
                data_int[2],
                data_int[3],
                data_int[4],
                data_int[5],
                data_int[6],
                data_int[7],
                data_int[8],
                data_int[9],
                rssi,
                lqi)
        except Exception as e:
            print("ERROR: Data send 'urequest': {}".format(e))

        if _DEBUG:
            if sent_ok:
                print("DATA SEND: {}".format(data_sent.status_code))
            else:
                print("DATA SEND FAIL: {}".format(data_sent))
        interpacket_time = 0
    else:
        interpacket_time += 1
        utime.sleep_ms(100)
    gc.collect()
