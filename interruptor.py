from time import sleep,ticks_ms,ticks_diff,gmtime,localtime,mktime
from vars import fluxo_int,fluxo_led,fluxo_reset
from collections import deque
import machine



def tempo_utc_iso():
    t=localtime()
    
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(*t[:6])

print(tempo_utc_iso())



fator=6.6



class SensorFluxo:
    sensores=[]
    
    def __init__(self,pin,led=None,reset=None,fator=fator):
        from funcoes.randomiza import gera_random
        
        self.id=gera_random(6)
        
        self.fator=fator
        
        self.historico=deque(list(),65)
        self.reset_historico=list()
        
        self.pulse_count=0
        self.flow_count=0
        
        self.rodada=0
        
        self.litros=0
        self.fluxo=0
        
        self.sensor_pin=machine.Pin(pin,machine.Pin.IN)
        
        if led:
            self.led_pin=machine.Pin(led,machine.Pin.OUT)
        else:
            self.led_pin=None
        
        if reset:
            self.reset_pin=machine.Pin(reset,machine.Pin.IN)
        else:
            self.reset_pin=None
        
        self.sensores.append(self)
    
    def zera_callback(self,p):
        #print('zera_callback')
        
        self.zera_total()
    def zera_total(self):
        if self.pulse_count:
            tupla=(mktime(localtime()),
                       self.pulse_count)
        
            self.reset_historico.append(tupla)
        
            print(self.reset_historico)
        
        self.pulse_count=0
        self.flow_count=0
        
    def display(self):
        #from rede import wifi
        from display import display
        
        #display.fill(0)
        
        #ip=wifi.config('addr4')
        #print('ip',ip)
        
        #display.text(f'IP: {ip}',0,0)
        agora=mktime(localtime())
        
        if len(self.reset_historico)>=1:
            
            val=self.reset_historico[-1]
            fnc=lambda pulse_count:(pulse_count/self.fator)/60
        
            if val[0]>=agora-3:
                display.text(f'Reset: {fnc(val[1]):.02} L',0,30)
            else:
                display.text(f'Sensor: {self.id}',0,30)
        else:
            display.text(f'Sensor: {self.id}',0,30)
        
        display.text(f'Litros: {self.litros:.02} L',0,40)
        display.text(f'Fluxo: {self.fluxo:.02} L/Min',0,50)

        #display.show()
        
    def zera_ciclo(self):
        self.flow_count=0
        
        #self.display()
        
    def pulse_callback(self,p):
        #print('pulse_callback')
        
        self.pulse_count+=1
        self.flow_count+=1
    
    def init(self):
        self.sensor_pin.irq(trigger=machine.Pin.IRQ_FALLING,
                            handler=self.pulse_callback)
        
        if self.reset_pin:
            self.reset_pin.irq(trigger=machine.Pin.IRQ_FALLING,
                                handler=self.zera_callback)
    def calcule(self):
        #print('calcule')
        
        self.litros=(self.pulse_count/self.fator)/60
        self.fluxo=(self.flow_count/self.fator)
        
        return self.litros,self.fluxo
    def ciclo_pessoal(self):
        #print('ciclo_pessoal')
        
        self.calcule()
        
        #print(f'Medição: {litros:.02} L')
        #print(f'Fluxo: {self.fluxo:.02} L/min')
            
        self.rodada+=1
            
        if self.rodada%6==0 or len(self.historico)==0:
            tupla=(mktime(localtime()),
                   self.flow_count)
            
            self.historico.append(tupla)
        
        self.zera_ciclo()
        
        if self.led_pin:
            self.led_pin.value(bool(self.fluxo))
    
    @classmethod
    def ciclo_global(cls):
        #print('ciclo_global')
        
        rtn=[]
        
        for sensor in cls.sensores:
            rtn.append(sensor.ciclo_pessoal())
        
        return rtn
    def self_dict(self):
        from vars import valor_gasolina
        
        
        if self.historico:
            tempos,valores=zip(*self.historico)
        else:
            tempos,valores=[],[]
        
        
        return {
            'id':self.id,
            'tempos':tempos,
            'fluxos':valores,
            'fluxo':self.fluxo,
            'litros':self.litros,
            'valor':self.litros*valor_gasolina,
            'valor_fmt':f'{self.litros*valor_gasolina:.02}',
            'litros_fmt':f'{self.litros:.02}',
            'fluxo_fmt':f'{self.fluxo:.02}'
            }
    
    #dict=self_dict
    
    @classmethod
    def dict(cls):
        return [sensor.self_dict() for sensor in cls.sensores]


class SensorEtanol:
    sensores=[]
    
    def __init__(self,pin,led=None):
        from funcoes.randomiza import gera_random
        
        self.id=gera_random(6)
        
        self.pulse_count=0
        
        self.rodada=0
        
        self.frequencia=0
        
        self.sensor_pin=machine.Pin(pin,machine.Pin.IN)
        
        if led:
            self.led_pin=machine.Pin(led,machine.Pin.OUT)
        else:
            self.led_pin=None
        
        self.sensores.append(self)
    
    def zera_callback(self,p):
        #print('zera_callback')
        
        self.zera_total()
    def zera_total(self):
        self.pulse_count=0
        
    def display(self):
        #from rede import wifi
        from display import display
        
        #display.fill(0)
        
        #ip=wifi.config('addr4')
        #print('ip',ip)
        
        #display.text(f'IP: {ip}',0,0)
        agora=mktime(localtime())
        
        if len(self.reset_historico)>=1:
            
            val=self.reset_historico[-1]
            fnc=lambda pulse_count:(pulse_count/self.fator)/60
        
            if val[0]>=agora-3:
                display.text(f'Reset: {fnc(val[1]):.02} L',0,30)
            else:
                display.text(f'Sensor: {self.id}',0,30)
        else:
            display.text(f'Sensor: {self.id}',0,30)
        
        display.text(f'Litros: {self.litros:.02} L',0,40)
        display.text(f'Fluxo: {self.fluxo:.02} L/Min',0,50)

        #display.show()
        
    def zera_ciclo(self):
        self.pulse_count=0
        
        #self.display()
        
    def pulse_callback(self,p):
        #print('pulse_callback')
        
        self.pulse_count+=1
    
    def init(self):
        self.sensor_pin.irq(trigger=machine.Pin.IRQ_FALLING,
                            handler=self.pulse_callback)
        
    def calcule(self):
        #print('calcule')
        
        self.frequencia=self.pulse_count
        
        return self.frequencia
    def ciclo_pessoal(self):
        #print('ciclo_pessoal')
        
        self.calcule()
            
        self.rodada+=1
            
        self.zera_ciclo()
        
        # todo consertar
        #if self.led_pin:
        #    self.led_pin.value(bool(self.fluxo))
    
    @classmethod
    def ciclo_global(cls):
        #print('ciclo_global')
        
        rtn=[]
        
        for sensor in cls.sensores:
            rtn.append(sensor.ciclo_pessoal())
        
        return rtn
    def self_dict(self):
        dicio={
                'id':self.id,
                'frequencia':self.frequencia
            }
        
        return dicio
    
    #dict=self_dict
    
    @classmethod
    def dict(cls):
        return [sensor.self_dict() for sensor in cls.sensores]




sensor_fluxo=SensorFluxo(fluxo_int,
                         led=fluxo_led,
                         reset=fluxo_reset)
sensor_fluxo.init()




def ciclo_sensores(t):
    sensor_fluxo.ciclo_pessoal()



if __name__=='__main__':
    while True:
        sensor.ciclo_pessoal()
        
        print(sensor.fluxo)
        print(Sensor.sensores)
        
        sleep(1)
