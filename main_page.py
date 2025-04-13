from vars import tipo,versao,porta,board,_id
from microdot.utemplate import Template
from configuracoes import configuracao
from microdot import Microdot,Response
from display import display
#from servidor import app
from time import sleep
import Logging




#Logging.basicConfig()






#def cadastra(app):
#    pass


#app=Microdot()
#Response.default_content_type='text/html'

#led=Pin(2,Pin.OUT)

def cria_servidor(app):
    with display:
        display.text('Creating Main!',0,0)
    print(f'Carregando main_page')
    sleep(.5)

    @app.route('/')
    def index(req):
        return Template('index.html').render(name=nome)



    nome="teste"
    STATIC_FOLDER='static'


    def join_paths(*paths):
        return '/'.join(path.strip('/') for path in paths)

    def exists(path):
        import os
        
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



    @app.route('/api_fluxo')
    def api_fluxo(request):
        from interruptor import Sensor
        #from servidor import self_status
       
        return self_status()|{'sensores':Sensor.dict()}



    @app.route('/fluxo')
    def fluxo(request):
        from interruptor import sensor
        from vars import valor_gasolina
        
        return Template('fluxo.html').render(litros=f'{sensor.litros:.02}',
                                             valor=f'{sensor.litros*valor_gasolina:.02}',
                                             fluxo=f'{sensor.fluxo:.02}')


    @app.route('/grafico')
    def grafico(request):
        from interruptor import sensor
        from vars import valor_gasolina
        
        return Template('grafico.html').render(litros=f'{sensor.litros:.02}',
                                               valor=f'{sensor.litros*valor_gasolina:.02}',
                                               fluxo=f'{sensor.fluxo:.02}')



    @app.route('/api_historico')
    def api_fluxo(request):
        #from servidor import self_status
        from interruptor import Sensor
       
       
        return self_status()|{'sensores':Sensor.dict()}

        
        
    @app.route('/zera')
    def zera(request):
        from interruptor import sensor
        
        Logging.info('Zerando medição!')
        
        sensor.zera_total()



    @app.route('/reboot')
    def reboot(request):
        if board:
            Logging.info('Reiniciando!')
            
            reset()
        else:
            return 'Não é possível!'



    #@app.route('/on')
    #def main(req):
    #    led.value(1)

    #@app.route('/off')
    #def main(req):
    #    led.value(0)








    def self_status():
        return {'status':'ok',
                
                'id':_id,
                
                'tipo':tipo,
                'versao':versao}

    def _status():
        if board:
            from network import WLAN
            
            ip,subrede,gateway,dns=WLAN(WLAN.IF_STA).ifconfig()
        else:
            ip,subrede,gateway,dns='10.40.0.1','255.0.0.0','10.0.0.1','10.10.0.1'
        
        endereco={
            'ip':ip,
            'dns':dns,
            'porta':porta,
            'subrede':subrede,
            'gateway':gateway
        }
        
        
        return self_status()|{'endereco':endereco}



    async def som_conectou():
        if board:
            from beeps import conectou
            from io import buzzer
            
            await buzzer.async_play(conectou)






    @app.route('/conectar',methods=['POST'])
    async def conectar(request):
        Logging.warning(f'Conexão Status: {request.json.get("status")}')
            
        print(request.json)
            
        await som_conectou()
            
        return _status()

    @app.route('/status')
    def status(request):
        return _status()


    app.mount(configuracao,
              url_prefix='/configuracao')
    
    return app




if __name__=='__main__':
    from servidor import app
    
    
    app=cria_servidor(app)
    
    
    app.run(debug=True,
            #host='10.100.0.1',
            port=porta)
