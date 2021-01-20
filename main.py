import cc1101_davis
import davis_decode
import utime
import WiFi
import machine
gc.collect()

DEBUG = True

wifi_con = WiFi.NetSet('infra')
wifi_con.readNetworkConfig()
ips = wifi_con.connectInfra(
    wifi_con._SSID,
    wifi_con._PASS,
    wifi_con._TIMEOUT)

if DEBUG:
    print("IPCONF: {}".format(ips))

gc.collect()

davis = cc1101_davis.CC1101()
davis.setRegisters()
davis.setFrequency(davis.hopIndex)
decoder = davis_decode.davisDecoder(
    wifi_con._INF_DB_WEATHER,
    wifi_con._INF_DB_STATUS,
    wifi_con._INF_DB_RAW)

gc.collect()

# Main receive loop
interpacket_time = 0
while True:
    try:
        data_int = davis.rxPacket()
    except Exception as e:
        raise e
        print(b"Rx EXCEPTION: {}".format(e))
        continue
    if data_int:
        header = decoder.davis_id(data_int[0])
        decoder.DecodePacket(data_int)
        data_prn = b"{:5} {:5} {:5} {:5} {:5} {:5} {:5} {:5} {:5} {:5}".format(
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
        print(b"{_data:60} HOP: {_hop:<5} RSSI: {_rssi:<5} LQI: {_lqi:<5} {_last}s since".format(
                _rssi=davis.rssi,
                _hop=davis.hopIndex,
                _data=data_prn,
                _lqi=davis.lqi,
                _last=interpacket_time / 10))
        if DEBUG:
            print(b"Header: {} Wind: {}".format(header, decoder.wind))
            print(b"{}: {}/{} ({})".format(
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
            raise e
            print(b"ERROR: Data send 'urequest': {}".format(e))
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
                davis.rssi,
                davis.lqi)
        except Exception as e:
            raise e
            print(b"ERROR: Data send 'urequest': {}".format(e))

        if DEBUG:
            if sent_ok:
                print(b"DATA SEND: {}".format(data_sent.status_code))
            else:
                print(b"DATA SEND FAIL: {}".format(data_sent))
        interpacket_time = 0
    else:
        interpacket_time += 1
        utime.sleep_ms(100)
    gc.collect()
