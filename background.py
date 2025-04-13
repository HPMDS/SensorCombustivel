from vars import board,settings
if board:
    from interruptor import Sensor,sensor_fluxo,ciclo_sensores
    from rede import ciclo as rede_ciclo,manager_cycle
#from threading import Thread
from display import ciclo_display,display
from asyncio import sleep
from machine import Timer
import Logging




log=Logging.getLogger("background")



n=0



def ciclo(t):
    global n
    
    log.debug(f'Rodando ciclo: {n}.')
    
    if board:
        if settings['done']:
            ciclo_display()
        
        ciclo_sensores(t)
        
        #display.fill(0)
        
        rede_ciclo()
    
    n+=1
        


async def looping():
    while True:
        if board:
            if settings['done']:
                pass
                #manager_cycle()
        
        await sleep(0.5)



temporizador=Timer(3)
temporizador.init(mode=Timer.PERIODIC,
                  period=1000,
                  callback=ciclo)


# loop_threading=Thread(target=looping,
#                       daemon=True)
