import network
import utime

_DEBUG = False


class NetSet(object):

    def __init__(self, wifi_type):
        self.sta = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)
        if wifi_type == 'infra':
            if _DEBUG:
                print("Disabling AP")
            self.ap.active(False)
            if _DEBUG:
                print("Activating INFRA")
            self.sta.active(True)
            self.sta.isconnected() # False, it should be # Comments by Yoda
            self._SSID = None
            self._PASS = None
            self._TIMEOUT = None
        elif wifi_type == 'ap':
            if _DEBUG:
                print("Disabling INFRA")
            self.ap.active(True)
            if _DEBUG:
                print("Activating AP")
            self.sta.active(False)
            self.sta.isconnected() # False, it should be # Comments by Yoda
            self._SSID = None
            self._PASS = None
            self._TIMEOUT = None

    def connectInfraGo(self, _timeout):
        if _DEBUG:
            print("Connecting to infra")
        self.sta.connect(self._SSID, self._PASS)
        if _DEBUG:
            print("Let's wait for the network to come up")
        while not (self.sta.isconnected()):
            if _timeout > 0:
                print("Trying... {} more times".format(_timeout))
                utime.sleep_ms(1001)
                _timeout -= 1
            else:
                print("Out of retrys")
                return False
        network_config = self.sta.ifconfig()
        return network_config

    def connectInfra(self, _SSID, _PASS, _TIMEOUT):
        self._SSID = _SSID
        self._PASS = _PASS
        try:
            net_conf_result = self.connectInfraGo(_TIMEOUT)
            utime.sleep_ms(100)
            if net_conf_result:
                return {
                    'ip': net_conf_result[0],
                    'mask': net_conf_result[1],
                    'gw': net_conf_result[2],
                    'dns': net_conf_result[3]                    }
            else:
                return False
        except Exception as e:
            print("ERROR: Network configuration failed with: {}".format(e))
            return False

    def connectAp(self):
        # TBI
        pass

    def readNetworkConfig(self):
        self.config_dict = {}
        try:
            with open('inet.conf', 'r') as conf_handler:
                for item in conf_handler.readlines():
                    option = item.split("=")[0].strip()
                    if len(item.split("=")) == 2 and '#' not in option:
                        value = item.split("=")[1].strip()
                        self.config_dict.update({option: value})
                    else:
                        if _DEBUG:
                            if '#' in option:
                                print(b"COMMENT in config")
                            else:
                                print(b"WARNING: Fucked up option, make it better")
        except Exception as e:
            if _DEBUG:
                print("WARNING: Errors in INFRA config, still going for AP")
            return False
        if _DEBUG:
            print("CONFIG DICT: {}".format(self.config_dict))
        self._SSID = self.config_dict['_SSID']
        self._PASS = self.config_dict['_PASS']
        self._TIMEOUT = int(self.config_dict['_TIMEOUT'])
        self._INFLUX_HOST = self.config_dict['_INFLUX_HOST']
        self._INFLUX_PORT = self.config_dict['_INFLUX_PORT']
        self._INFLUX_USER = self.config_dict['_INFLUX_USER']
        self._INFLUX_PASS = self.config_dict['_INFLUX_PASS']
        self._INF_DB_WEATHER = self.config_dict['_INF_DB_WEATHER']
        self._INF_DB_STATUS = self.config_dict['_INF_DB_STATUS']
        self._INF_DB_RAW = self.config_dict['_INF_DB_RAW']
