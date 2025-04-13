from io import pinoSinal_on,pinoSinal_off
from vars import board,AP,som
if board:
    import network
from time import sleep
from json import load
import Logging




#Logging.basicConfig()
log=Logging.getLogger("rede")
wifi,ap=None,None




def pega_ip(nic):
    rtn=nic.ipconfig("addr4")
    
    #print(rtn)
    
    return rtn



def cria_nic():
    global wifi
    
    if wifi is None:
        wifi=network.WLAN(network.WLAN.IF_STA)
        wifi.active(True)
        
        network.hostname('sensor_fluxo')
        
        return wifi
    else:
        return wifi

def cria_ap():
    nic=network.WLAN(network.WLAN.AP_IF)
    #nic.active(True)
    
    essid='Esp32 AP'
    
    
    nic.config(essid=essid,password='1234')
    
    ip=nic.ipconfig("addr4")
    
    log.info(f'Ligando AP: {essid}')
    
    return nic




#wifi,ap=None,None
#ap=cria_ap()
conectado,situacao=None,'Iniciando'

def _situacao(conectado,status):
    global situacao
    
    if conectado is None:
        situacao='Desconectado'
    elif status:
        pinoSinal_on.on()
        pinoSinal_off.off()
            
        if conectado or conectado is None:
            situacao='Conectado'
        else:
            situacao='Reconectado'
    else:
        pinoSinal_on.off()
        pinoSinal_off.on()
            
        if conectado:
            situacao='Desconectado'
        else:
            situacao='Sem Sinal!'
    return situacao

def ciclo():
    #return
    global wifi,conectado
    
    
    
    if board and wifi:
        #print('is_connected',wifi.isconnected())
        #print('config ssid',wifi.config('ssid'))
        
        
        status=wifi.isconnected()
        
        situacao=_situacao(conectado,status)
        
        if status:
            pinoSinal_on.on()
            pinoSinal_off.off()
            
        else:
            pinoSinal_on.off()
            pinoSinal_off.on()
            
        if conectado!=status:
            log.debug(situacao)
        
        
        
        conectado=status
    return situacao






def cria_config_ip(dicio):
    return (dicio['ip'],
            dicio['subrede'],
            dicio['gateway'],
            dicio['dns'])

def define_ip(nic,dicio=None):
    if dicio is None:
        dicio=puxa_ip()
    
    log.info(f"Configurando IP: {dicio['ip']}")
    
    nic.ifconfig(cria_config_ip(dicio))

def puxa_ip():
    with open('ip.json','r') as f:
        dicio=load(f)
        
        return dicio
def puxa_wifi():
    with open('wifi.json','r') as f:
        dicio=load(f)
        
        return dicio


def lida_status(nic):
    from icones import wifi_senha_48px
    from display import display
    
    status=nic.status()
    
    log.info(f'rede.lida_status.status={status}')
    log.info(nic.scan())
    
    if status==1001:
        with display:
            wifi_senha_48px.blit(40,0)
            display.text(f'Falha!',40,50)

def conecta_wifi(nic):
    dicio=puxa_wifi()
    
    
    log.info(f"Ligando Wifi: {dicio['ssid']}")
    
    rtn=nic.connect(dicio['ssid'],
                    dicio['senha'])
    
    log.info(f'rede.conecta_wifi.rtn={rtn}')
    
    while not nic.isconnected():
        lida_status(nic)
        
        sleep(0.02)
    
    if board and som:
        from beeps import inicio
        from io import buzzer
    
        buzzer.play(inicio)
    
    return nic




def do_connect():
    #if not board:
    #    Logging.info(f'Rodando Stand-alone!')
        
    #    return None,None
    from icones import wifi_done_48px,wifi_sta_48px
    from display import display
    from vars import espera
    global wifi,ap
    
    
    if True:#not AP:
        log.info(f'Rodando Modo STA!')
        
        with display:
            icon=wifi_sta_48px.blit(40,0)
            display.text(f'Modo STA!',30,50)
        
        wifi=cria_nic()
        
        wifi.active(True)
        
        
        if espera:
            sleep(.5)
        
        define_ip(wifi)
        
        if espera:
            sleep(1.5)
        
        conecta_wifi(wifi)
        
        
        ap=None
        
    else:
        Logging.info(f'Rodando Modo AP!')
        
        with display:
            display.text(f'Modo AP!',0,0)
        
        ap.active(True)
        
        if espera:
            sleep(.5)
        
        define_ip(ap)
        
        wifi=None
    
    with display:
        from icones import wifi_done_48px
        
        icon=wifi_done_48px.blit(40,0)
        
        display.text(f'Done!',45,50)
    
    #wifi.active(True)
    
    #await sleep(1.5)
    
    #print(f'IP: {pega_ip(wifi)}')
        
    #return wifi,ap
    
    #from wifi_manager.wifi_manager import WifiManager
    
    #WifiManager.setup_network()



def do_connect2():
    from wifi_manager import WifiManager
    
    rtn=WifiManager.setup_network()
    
    global wifi
    
    wifi=WifiManager.wlan()
    
    return rtn

def manager_cycle():
    from wifi_manager import WifiManager
    
    return WifiManager._manage()


def rede_display_ciclo():
    from display import display
    
    
    ip=pega_ip(wifi)[0]
    ssid=wifi.config("essid")
    
    display.text(f'IP: {ip}',0,0)
    display.text(f'SSID: {ssid}',0,10)
    display.text(f'Wifi: {situacao}',0,20)




if __name__=='__main__':
    from asyncio import run
    from time import sleep_ms
    import Logging
    
    Logging.basicConfig()
    
    #run(do_connect())
    do_connect2()
    
    
    while True:
        sleep_ms(500)
