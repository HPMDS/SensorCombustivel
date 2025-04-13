from microdot.utemplate import Template
from microdot import Microdot,Response
from configuracoes import configuracao
from background import looping
from asyncio import create_task
from rede import do_connect
from buzzer import Buzzer
from machine import Pin,reset
from vars import board
import Logging
if board:
    from machine import Pin
import os
#import artnet
#import webrepl



#webrepl.start()



app=Microdot()
Response.default_content_type='text/html'
Logging.basicConfig(filename='notificacoes.log')

if board:
    pwm=Pin(5)
    pwm.off()
    buzzer=Buzzer(pwm)


#led=Pin(2,Pin.OUT)


nome="teste"
STATIC_FOLDER='static'


@app.route('/')
def index(req):
    return Template('index.html').render(name=nome)





#@app.route('/on')
#def main(req):
#    led.value(1)

#@app.route('/off')
#def main(req):
#    led.value(0)
def join_paths(*paths):
    return '/'.join(path.strip('/') for path in paths)

def exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False



@app.route('/static/<path:path>')
def static_file(request,path):
    file_path=join_paths(STATIC_FOLDER,path)
    
    if exists(file_path):
        # Define o tipo de conteúdo com base na extensão do arquivo
        if file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            content_type='image/jpeg'
        else:
            content_type=None
        
        return Response.send_file(file_path,
                                  content_type=content_type)
    else:
        Logging.warning(f"Tentativa de acesso a arquivo inexistente: [{path}]")
        
        return Response('Arquivo não encontrado',
                        status_code=404)


async def som_conectou():
    tons=[(1/4,'H5'),
          (1/4,'H6'),
          (1/4,'H5'),
          
          (1/4,'H6'),
          (1/8,'H5'),
          (1/2,'H3'),]
    
    if board:
        await buzzer.async_play(tons)


def _status():
    from vars import tipo,versao,porta

    
    if board:
        from network import WLAN
        
        ip,subrede,gateway,dns=WLAN(WLAN.IF_STA).ifconfig()
    else:
        ip,subrede,gateway,dns='10.40.0.1','255.0.0.0','10.0.0.1','10.10.0.1'
    
    
    return {'status':'ok',
            
            'tipo':tipo,
            'versao':versao,
            
            'ip':ip,
            'dns':dns,
            'porta':porta,
            'subrede':subrede,
            'gateway':gateway}



@app.route('/conectar',methods=['POST'])
async def conectar(request):
    print(f'Conexão Status: {request.json.get("status")}')
    
    print(request.json)
    
    if board:
        await som_conectou()
    
    return _status()

@app.route('/status')
def status(request):
    return _status()

@app.route('/api_fluxo')
def api_fluxo(request):
    from interruptor import litros,fluxo
   
    return {'status':'ok',
            'litros':litros,
            'fluxo':fluxo,
            'litros_fmt':f'{litros:.02}',
            'fluxo_fmt':f'{fluxo:.02}'}

@app.route('/fluxo')
def fluxo(request):
    from interruptor import litros,fluxo
    
    return Template('fluxo.html').render(litros=f'{litros:.02}',
                                         fluxo=f'{fluxo:.02}')


@app.route('/grafico')
def fluxo(request):
    from interruptor import litros,fluxo
    
    return Template('grafico.html').render(litros=f'{litros:.02}',
                                           fluxo=f'{fluxo:.02}')



@app.route('/api_historico')
def api_fluxo(request):
    from interruptor import litros,fluxo,historico
   
    tempos,valores=zip(*historico)
   
    return {'status':'ok',
            'litros':litros,
            'fluxo':fluxo,
            'tempos':tempos,
            'fluxos':valores,
            'litros_fmt':f'{litros:.02}',
            'fluxo_fmt':f'{fluxo:.02}'}

    
    

@app.route('/zera')
def zera(request):
    from interruptor import zera
    
    zera()


@app.route('/reboot')
def reboot(request):
    if board:
        reset()
    else:
        return 'Não é possível!'




app.mount(configuracao,
          url_prefix='/configuracao')



def main():
    from vars import porta
    
    if board:
        inicio=[((1/4),'H1'),
                ((1/4),'3'),
                ((1/4),'H5'),
                ((1/4),'0'),
                ((1/4),'6')
                ]

        buzzer.play(inicio)
    
    wifi,ap=do_connect()
    
    create_task(looping(wifi,ap))
    
    app.run(debug=True,
            port=porta)


if __name__=='__main__':
    main()