from machine import Pin,I2C
from ssd1306 import SSD1306_I2C
from icones import booting_48px
#from teste_display import cria_framebuf
from vars import i2c_scl,i2c_sda



i2c=I2C(0,
        scl=Pin(i2c_scl),
        sda=Pin(i2c_sda))



print('i2c_scan:',i2c.scan())


class NullDisplay:
    def __enter__(self):
        pass
        return self
    def __exit__(self,exc_type,exc_val,exc_tb):
        print('Exibição ao Display não Concluída!')
    def __eq__(self,other):
        return other==None
    def text(self,*args,**kwargs):
        pass



display=NullDisplay()



class Display(SSD1306_I2C):
    @classmethod
    def default(self):
        global display
        
        if display==None:
            try:
                display=Display(128,64,i2c)
                
                print(f'Display Reconectado!')
            except OSError:
                print(f'Display Desconectado!')
            
            return display
        else:
            return display
    def __enter__(self):
        self.fill(0)
        return self
    def __exit__(self,exc_type,exc_val,exc_tb):
        try:
            self.show()
        except OSError:
            global display
            
            display=NullDisplay()
            
            print('Reconectando Display!')
            
            self.default()
            
            #display.show()
    
    #default.__exit__=__exit__


#display=Display.default()
def pega_display():
    return Display.default()


try:
    with pega_display() as display:
        icon=booting_48px.blit(40,0,display)
        display.text('Initializing...',5,50)
except AttributeError:
    print('Ciclo do Display não concluído!')




def ciclo_display():
    from rede import rede_display_ciclo
    from interruptor import sensor
        
    
    #if display is not None:
    try:
        with pega_display():
            sensor.display()
            
            rede_display_ciclo()
    except AttributeError:
        print('Ciclo do Display não concluído!')
