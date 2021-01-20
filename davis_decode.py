import urequests
import machine

try:
    _DEBUG = DEBUG
except:
    _DEBUG = False

def send_to_influx(host, port, db, user, password, davis_unit_id, wind, measurement, name, value, tags):
    post = "http://{}:{}/write?db={}".format(host, port, db)
    if _DEBUG:
        print(b"SENDING TO: {}".format(post))
    if measurement is False:
        return (False, b"ERROR measurement set False")
    if measurement is None:
        data = "wind,type=speed,davis_id={_davis_id} value={_speed}\n wind,type=direction,davis_id={_davis_id} value={_direction}".format(
            _davis_id = davis_unit_id,
            _speed=wind['speed'],
            _direction=wind['direction'])
        if _DEBUG:
            print(b"SEND WIND only: {}")
    else:
        for tag in tags.keys():
            measurement = "{},{}={}".format(measurement, tag, tags[tag])
        data = "{_measure},davis_id={_davis_id} {_name}={_value}\n wind,type=speed,davis_id={_davis_id} value={_speed}\n wind,type=direction,davis_id={_davis_id} value={_direction}".format(
            _measure=measurement,
            _name=name,
            _value=value,
            _davis_id = davis_unit_id,
            _speed=wind['speed'],
            _direction=wind['direction'])
    if _DEBUG:
        print(b"POST_DATA: {}".format(data))
    try:
        return (True, urequests.post(post, data=data))
    except Exception as e:
        if e.args[0] == 103:
            machine.reset()
        else:
            return (False, b"ERROR sending data to influx: {}".format(e))

def raw_send_to_influx(host, port, db, user, password, b0, b1, b2, b3, b4, b5, b6, b7, b8, b9, rssi, lqi):
    post = "http://{}:{}/write?db={}".format(host, port, db)
    if _DEBUG:
        print(b"SENDING TO: {}".format(post))
    data = "data b0={_b0},b1={_b1},b2={_b2},b3={_b3},b4={_b4},b5={_b5},b6={_b6},b7={_b7},b8={_b8},b9={_b9},rssi={_rssi},lqi={_lqi}".format(
            _b0=b0, _b1=b1, _b2=b2, _b3=b3,
            _b4=b4, _b5=b5, _b6=b6, _b7=b7,
            _b8=b8, _b9=b9, _rssi=rssi, _lqi=lqi)
    if _DEBUG:
        print(b"POST_DATA: {}".format(data))
    try:
        return (True, urequests.post(post, data=data))
    except Exception as e:
        if e.args[0] == 103:
            machine.reset()
        else:
            return (False, b"ERROR sending RAW data to influx: {}".format(e))

def reverseBits(data):
    data = "{:08b}".format(data)
    z = ""
    for i in range(len(data),0,-1):
        z = z + (data[i-1])
    return int(z, 2)


class davisDecoder(object):
    def __init__(self, weather_db, stat_db, raw_db):
        __name__ = 'Davis value decoder class'
        self.weather_influx_db = weather_db
        self.stat_influx_db = stat_db
        self.raw_influx_db = raw_db

    def byte_split(self, data):
        msb = data >> 4
        lsb = data & 0b00001111
        result = {"MSB": msb, "LSB": lsb}
        return result

    def davis_id(self, header):
        self.davis_packet_id = 0
        self.battery_low = 0
        self.unit_id = 0
        bin_header = self.byte_split(header)
        self.unit_id = bin_header['LSB'] & 0b0111
        self.battery_low = bin_header['LSB'] >> 3
        self.davis_packet_id = bin_header['MSB']
        result = {"davis_id": self.unit_id,
                  "packet_id": self.davis_packet_id,
                  "bat_low": self.battery_low}
        return result

    def decode_wind(self, databytes):
        # wind speed in mph, i suppose. Let's convert it
        wind_speed = round(float(databytes['windspeed'] * 1.60934), 1)
        wind_direction_factor = round(float(360)/float(255), 1)
        wind_direction = databytes['winddir']
        wind_direction = float(wind_direction) * wind_direction_factor
        result = {"speed": wind_speed, "direction": wind_direction}
        return result

    def decode_temp(self, temp):
        temp_f = (float(temp)) / float(160) # in Fahrenheit
        temp_c = round((temp_f - 32) * float(5)/float(9), 1)
        result = {"celsius": temp_c, "fahrenheit": temp_f}
        return result

    def decode_humidity(self, hum):
        pass

    def supercap_decode(self, byte2, byte3):
        cap = (byte2 << 2) + (byte3 >> 6)
        result = float(cap / 100.00)
        return result

    def solarvolt_decode(self, byte2, byte3):
        solar = (byte2 << 1) + (byte3 >> 7)
        result = float(solar)
        return result

    def rain_decode(self, rain):
        result = float(rain & 0x7F)
        return result

    def rainrate_decode(self, byte2, byte3):
        # if byte3(b2 here) is 0xFF, or 255, there is no rain
        #print("b2:{} b3:{} = result:{}".format(byte2, byte3, byte2 + (byte3 >> 4 << 8)))
        if byte2 == 255:
            rainstate = 0
            rainrate = 0
        elif byte2 == 254:
            rainstate = 1
            rainrate = 0.2
        else:
            rainstate = 2
            if byte3 > 4:
                rainrate = 720 / ((byte3 >> 4 << 8) + byte2)
            else:
                rainrate = 0
        result = {"state": float(rainstate), "rate": float(rainrate)}
        #print(result)
        return result

    def DecodePacket(self, packet):
        # By default and most of the time, write to weather
        self.write_influx_db = self.weather_influx_db
        # Set all to None
        self.wind = False
        self.measurement = False
        self.name = False
        self.value = False
        self.tags = False
        self.wind = self.decode_wind(
            {"windspeed": packet[1], "winddir": packet[2]})
        if self.davis_packet_id == 2:
            # SuperCap charge 0x2
            if _DEBUG:
                print('SCAP:')
            supercap = self.supercap_decode(
                packet[3], packet[4]
            )
            if _DEBUG:
                print("{}".format(supercap))
            self.write_influx_db = self.stat_influx_db
            self.measurement = 'iss'
            self.name = 'voltage'
            self.tags = {'type': 'capacitor'}
            self.value = supercap
        elif self.davis_packet_id == 3:
            # No fucking idea 0x3
            # {'hop':1,'h':48,'b0':6,'b1':237,'b2':255,'b3':195,'b4':135,'b5':50,'b6':110,'b7':255,'b8':255,'b9':179,'rssi':45,'lqi':0,'nxt':64,'cnt':163}
            self.measurement = None
            self.name = None
            self.tags = None
            self.value = None

        elif self.davis_packet_id == 5:
            # Rainrate 0x5
            rainrate_dict = self.rainrate_decode(
                packet[3],
                packet[4])
            if _DEBUG:
                print("RAINRATE: {}".format(rainrate_dict))
            self.measurement = 'rain'
            self.name = 'value'
            self.tags = {'type': 'rainrate'}
            self.value = rainrate_dict['rate']
        elif self.davis_packet_id == 6:
            # Sun Irradiation 0x6 (NOT ON vantage Vue)
            pass
        elif self.davis_packet_id == 7:
            # Super Cap voltage 0x7
            solarvolt = self.solarvolt_decode(
                packet[3], packet[4]
            )
            if _DEBUG:
                print("SOLV {}".format(solarvolt))
            self.write_influx_db = self.stat_influx_db
            self.measurement = 'iss'
            self.name = 'voltage'
            self.tags = {'type': 'solar'}
            self.value = solarvolt
        elif self.davis_packet_id == 8:
            # Temperature 0x8
            raw_temp = (packet[3] << 8) + packet[4]
            temp_dict = self.decode_temp(raw_temp)
            temp = float(temp_dict['celsius'])
            if _DEBUG:
                print("TEMP: {}".format(temp))
            self.measurement = 'temphumi'
            self.name = 'temperature'
            self.tags = {'type': 'external'}
            self.value = temp
        elif self.davis_packet_id == 9:
            # Wind gusts 0x9
            windgust = packet[3] * 1.60934
            if _DEBUG:
                print("WINDGUST: {}".format(windgust))
            self.measurement = 'wind'
            self.name = 'value'
            self.tags = {'type': 'windgust'}
            self.value = windgust
        elif self.davis_packet_id == 10:
            # Humidity 0xa
            raw_humidity = (((packet[4] >> 4) & 0b0011) << 8) \
                         + packet[3]
            humidity = round(int(raw_humidity) / float(10), 1)
            if _DEBUG:
                print("HUMI: {}".format(humidity))
            self.measurement = 'temphumi'
            self.name = 'humidity'
            self.tags = {'type': 'external'}
            self.value = humidity
        elif self.davis_packet_id == 14:
            # Rain bucket tips 0xe
            raw_rain = (packet[3]) + (packet[4] >> 7 << 8)
            rain = self.rain_decode(raw_rain)
            if _DEBUG:
                print("RAINCOUNT: {}".format(rain))
            self.measurement = 'rain'
            self.name = 'value'
            self.tags = {'type': 'rain_bucket_tips'}
            self.value = rain

