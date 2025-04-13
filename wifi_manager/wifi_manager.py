"""Implementation of a controller to connect to preferred wifi network(s) [For ESP8266, micro-python]

Config is loaded from a file kept by default in '/networks.json'

Priority of networks is determined implicitly by order in array, first being the highest.
It will go through the list of preferred networks, connecting to the ones it detects present.

Default behaviour is to always start the webrepl after setup,
and only start the access point if we can't connect to a known access point ourselves.

Future scope is to use BSSID instead of SSID when micropython allows it,
this would allow multiple access points with the same name, and we can select by signal strength.


"""

import json
import time
from asyncio import sleep
import os
from display import display

# Micropython modules
import network

try:
    import webrepl
except ImportError:
    pass


try:
    import uasyncio as asyncio
except ImportError:
    pass



# Micropython libraries (install view uPip)
try:
    import Logging as logging
    log = logging.getLogger("wifi_manager")
except ImportError:
    # Todo: stub logging, this can probably be improved easily, though logging is common to install
    def fake_log(msg, *args):
        print("[?] No logger detected. (log dropped)")
    log = type("", (), {"debug": fake_log, "info": fake_log, "warning": fake_log, "error": fake_log,
                            "critical": fake_log})()



dhcp=False



class WifiManager:
    webrepl_triggered = False
    _ap_start_policy = "never"
    config_file = '/networks.json'
    max_retry=10

    # Starts the managing call as a co-op async activity
    @classmethod
    def start_managing(cls):
        loop = asyncio.get_event_loop()
        loop.create_task(cls.manage()) # Schedule ASAP
        # Make sure you loop.run_forever() (we are a guest here)
    
    @classmethod
    def ip(cls)->str:
        from rede import pega_ip
        
        rtn=pega_ip(cls.wlan())
        
        return rtn
    
    @classmethod
    @property
    def ap_ip(self)->str:
        from rede import pega_ip
        
        return pega_ip(self.accesspoint())
    
    @classmethod
    def _got_ip(cls)->bool:
        status=cls.wlan().status()
        
        #print(f'wifi_manager._got_ip.status={status}')
        
        return ((status == network.STAT_GOT_IP) or \
                (cls.ip != '0.0.0.0'))# temporary till #3967
    
    @classmethod
    def got_ip(cls)->bool:
        return cls.wlan().isconnected() and cls._got_ip()
    
    @classmethod
    def _manage(cls):
        # ESP32 does not currently return
        if not cls.got_ip():  # temporary till #3967
            log.info("Network not connected: managing")
            # Ignore connecting status for now.. ESP32 is a bit strange
            # if status != network.STAT_CONNECTING: <- do not care yet
            cls.connect_station()
    
    # Checks the status and configures if needed
    @classmethod
    def manage(cls):
        while True:
            cls._manage()
            
            sleep_ms(10000)  # Pause 5 seconds
        
        log.error("Network manager stopped!")

    @classmethod
    def wlan(cls):
        return network.WLAN(network.WLAN.IF_STA)
        #try:
        #    return cls._wlan
        #except AttributeError:
        #    cls._wlan=network.WLAN(network.WLAN.IF_STA)
        #    
        #    return cls._wlan

    @classmethod
    def accesspoint(cls):
        try:
            return cls._ap
        except AttributeError:
            cls._ap=network.WLAN(network.WLAN.IF_AP)
            
            return cls._ap

    @classmethod
    def wants_accesspoint(cls)->bool:
        static_policies = {"never": False, "always": True}
        if cls._ap_start_policy in static_policies:
            return static_policies[cls._ap_start_policy]
        # By default, that leaves "Fallback"
        return cls.wlan().status() != network.STAT_GOT_IP  # Discard intermediate states and check for not connected/ok
    
    @classmethod
    def get_networks(cls)->list:
        # scan what’s available
        available_networks=[]
        
        with display:
            display.text('Scanning Wifi',0,10)
        
        scan=cls.wlan().scan()
        
        for network in scan:
            dicio={
                "ssid":network[0].decode("utf-8"),
                "bssid":network[1],
                #"channel":network[2],
                "strength":network[3]
            }
            
            available_networks.append(dicio)
        
        # Sort fields by strongest first in case of multiple SSID access points
        available_networks.sort(key=lambda station:station["strength"],
                                reverse=True)
        
        return available_networks
    
    @classmethod
    def candidates(cls,preferred_networks:list[dict],
                       available_networks:list[dict])->list[dict]:
        # Get the ranked list of BSSIDs to connect to, ranked by preference and strength amongst duplicate SSID
        candidates=[]
        
        
        with display:
            display.text('List Known Wifi',0,10)
        
        for aPreference in preferred_networks:
            for aNetwork in available_networks:
                if aPreference["ssid"]==aNetwork["ssid"]:
                    connection_data={"ssid":aNetwork["ssid"],
                                     "bssid":aNetwork["bssid"],# NB: One day we might allow collection by exact BSSID
                                     "password":aPreference["password"],
                                     "enables_webrepl":aPreference["enables_webrepl"]}
                    
                    candidates.append(connection_data)
        
        return candidates

    @classmethod
    def _setup(cls)->bool:
        # now see our prioritised list of networks and find the first available network
        try:
            with open(cls.config_file, "r") as f:
                config = json.loads(f.read())
                
                cls.preferred_networks = config['known_networks']
                cls.ap_config = config["access_point"]
                
                if config.get("schema", 0) != 2:
                    log.warning("Did not get expected schema [2] in JSON config.")
            
            return True
        except Exception as e:
            log.error("Failed to load config file, no known networks selected")
            cls.preferred_networks = []
            
            return False
    
    @classmethod
    def connection_process(cls,candidates:list[dict])->bool:
        for new_connection in candidates:
            
            # Micropython 1.9.3+ supports BSSID specification so let's use that
            if cls.connect_to(ssid=new_connection["ssid"],
                              password=new_connection["password"],
                              bssid=new_connection["bssid"]):
                cls.webrepl_triggered = new_connection["enables_webrepl"]
                break  # We are connected so don't try more
        
        return cls.wlan().isconnected()
    
    @classmethod
    def activate_accesspoint(cls)->bool:
        # Check if we are to start the access point
        cls._ap_start_policy=cls.ap_config.get("start_policy","never")
        
        AP=cls.accesspoint()
        
        should_start_ap=cls.wants_accesspoint()
        AP.active(should_start_ap)
        
        if should_start_ap or not cls.got_ip():  # Only bother setting the config if it WILL be active
            log.info("Enabling your access point...")
            AP.config(**cls.ap_config["config"])
            
            cls.webrepl_triggered=cls.ap_config["enables_webrepl"]
            
        AP.active(cls.wants_accesspoint())  # It may be DEACTIVATED here
        
        # Define ip
        log.info("Setting AP IP...")
        cls.define_ip(AP)
        
        return AP.active()
    
    @classmethod
    def connect_station(cls)->bool:
        #cls.accesspoint().activate(False)
        
        cls.wlan().active(True)#bool(cls.preferred_networks))
        
        with display:
            from icones import wifi_sta_48px
            
            icon=wifi_sta_48px.blit(40,0)
            display.text(f'Modo STA!',30,50)
        
        time.sleep_ms(500)
        
        # scan what’s available
        
        log.debug("Checking Networks!")
        available_networks=cls.get_networks()
        
        # Get the ranked list of BSSIDs to connect to, ranked by preference and strength amongst duplicate SSID

        log.debug("Listing Candidates...")
        candidates=cls.candidates(cls.preferred_networks,
                                  available_networks)
        
        time.sleep_ms(500)
        
        log.debug("Attempting Connection!")
        connected=cls.connection_process(candidates)
        
        time.sleep_ms(500)
        
        # Set IP Address
        if connected:
            log.debug("Configuring Address...")
            
            if dhcp:
                log.info("Connected to {0}".format(cls.ip))
            else:
                log.info("Setting STA IP...")
                
                cls.define_ip(cls.wlan())
        
            log.info("Station Management: Done!")
        else:
            log.error("Station Management: Failed!")
        
        return connected
    
    @classmethod
    def setup_network(cls)->bool:
        if not cls._setup():
            return False

        # set things up
        cls.webrepl_triggered = False  # Until something wants it
        
        connected=cls.connect_station()
        
        cls.activate_accesspoint()

        # may need to reload the config if access points trigger it

        # start the webrepl according to the rules
        if cls.webrepl_triggered:
            try:
                webrepl.start()
            except NameError:
                # Log error here (not after import) to not log it if webrepl is not configured to start.
                log.error("Failed to start webrepl, module is not available.")

        # return the success status, which is ultimately if we connected to managed and not ad hoc wifi.
        return cls.got_ip()

    @classmethod
    def define_ip(cls,nic)->bool:
        from rede import define_ip,puxa_ip
        
        dicio=puxa_ip()
        rtn=define_ip(nic)
        
        if rtn:
            log.info("Connected on address {0}".format(cls.ip))
        else:
            log.error("Failed to connect on address {0}".format(dicio['ip']))
            log.warning("Connected on address {0} insted".format(cls.ip()[0]))
        
        return rtn

    @classmethod
    def connect_to(cls,*,ssid,password,**kwargs)->bool:
        log.info("Attempting to connect to network {0}...".format(ssid))
        
        with display:
            display.text('Connecting Wifi',0,10)
            display.text(ssid,0,25)
        
        cls.wlan().connect(ssid,password,**kwargs)

        for check in range(0,cls.max_retry):  # Wait a maximum of 10 times (10 * 500ms = 5 seconds) for success
            if cls.wlan().isconnected():
                log.info("Successfully connected {0}".format(ssid))
                
                with display:
                    from icones import wifi_done_48px
                    
                    icon=wifi_done_48px.blit(40,0)
                    display.text(f'Done!',45,50)
                
                return True
            time.sleep_ms(500)
        
        log.warning("Failed to connect to {0}".format(ssid))
        return False
