from asyncio import sleep,gather,run
from servidor import app as _app
from rede import do_connect,do_connect2
from display import display
import Logging
#import webrepl_setup
#import webrepl
#import artnet



#webrepl.start()

#Logging.basicConfig()
log=Logging.getLogger("Board")
app=None
done=False


async def _run():
    from vars import porta,settings,espera
    from icones import webpage_40px
    global app,done
    
    log.info('Começando Server!')
    
    
    with display:
        webpage_40px.blit(42,0)
        
        
        display.text(f'Setting Up',20,45)
        display.text(f'Web APP...',23,55)
    
    from main_page import cria_servidor
    
    if espera:
        await sleep(1)
    
    app=cria_servidor(_app)
    
    settings['done']=True
    
    await app.start_server(debug=True,
                           #host='10.100.0.1',
                           port=porta)


async def main():
    from icones import servidor_40px,tarefa_40px
    from vars import espera
    
    if espera:
        await sleep(.25)
    
    log.info(f'Iniciando Conectividade!')
    wlan=await do_connect()
    #wlan=do_connect2()
    
    if espera:
        await sleep(.5)
    
    with display:
        tarefa_40px.blit(42,0)
        
        display.text(f'Setting Up',20,45)
        display.text(f'Tasks...',33,55)
    
    log.info(f'Iniciando Tasks!')
    from background import looping
    import interruptor
    #import Teste
    
    if espera:
        await sleep(.5)
    
    with display:
        servidor_40px.blit(42,0)
        display.text(f'Starting',30,45)
        display.text(f'Server!',35,55)
    
    #if espera:
    #    await sleep(.5)
    
    log.info(f'Iniciando Gather!')
    await gather(looping(),
                 _run())
    
    #app.run(#debug=True,
    #        host='10.100.0.1',
    #        port=80)
    
    with display:
        display.text(f'Server Stopped!',0,0)



if __name__=='__main__':
    run(main())