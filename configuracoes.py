from microdot.utemplate import Template
from microdot import Microdot
from rede import puxa_ip,wifi
from vars import board
from json import dump
if board:
    import network



configuracao=Microdot()

if board:
    #wlan=network.WLAN(network.WLAN.IF_STA)
    
    #wlan.activate(True)

    def pega_redes():
        return [str(rede[0].decode('utf-8')) for rede in wlan.scan() if rede[0]]


    @configuracao.route('/')
    def cfg_ip(req):
        return Template('configuracao.html').render()


    @configuracao.route('/ip')
    def cfg_ip(req):
        ip=wifi.ipconfig('addr4')[0]
        
        configs=puxa_ip()
        
        return Template('ip.html').render(ip_atual=ip,
                                          configs=configs)
    @configuracao.route('/ip',methods=['POST'])
    def cfg_ip_set(req):
        
        ip=req.form['ip']
        subrede=req.form['subrede']
        gateway=req.form['gateway']
        dns=req.form['dns']
        
        print('Salvando ip',ip)
        
        with open('ip.json','w') as f:
            dicio={
                'ip':ip,
                'subrede':subrede,
                'gateway':gateway,
                'dns':dns}
            
            dump(dicio,f)
        
        return Template('ip.html').render(ip_atual=ip,
                                          configs=dicio)



    @configuracao.route('/wifi')
    def cfg_wifi(req):
        return Template('wifi.html').render(ssid_atual=wlan.config('ssid'),
                                            #redes_disponiveis=pega_redes(),
                                            )
    @configuracao.route('/wifi',methods=['POST'])
    def cfg_wifi_set(req):
        
        ssid=req.form['ssid']
        senha=req.form['senha']
        
        print('salvando wifi',ip)
        
        with open('wifi.json','w') as f:
            dicio={
                'ssid':ssid,
                'senha':senha}
            
            dump(dicio,f)
        
        return Template('wifi.html').render(ssid_atual=ssid,
                                            redes_disponiveis=pega_redes())
