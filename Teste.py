from stupidArtnet import StupidArtnetServer
from vars import board
if board:
    from io import led1,led2,led3,led4
import time



canal=0
delta=6


sinal={}

def registra(addr):
    tempo_atual=time.mktime(time.localtime())
    
    if addr in sinal:
        ultimo_tempo=sinal[addr]
        
        #print(ultimo_te]mpo)
        
        if time.ticks_diff(tempo_atual,ultimo_tempo)>=delta:
            print(f'Voltou a receber sinal Artnet, Endereço: {addr}')
    else:
        print(f'Recebendo sinal Artnet, Endereço: {addr}')
    sinal[addr]=tempo_atual
    

# create a callback to handle data when received
def test_callback(data,addr):
    """Test function to receive callback data."""
    # the received data is an array
    # of the channels value (no headers)
    
    
    aplica=lambda canal:int((data[canal]*2))
    
    #print('Received new data \n',data[:4])
    
    #registra(addr)
    
    c1=aplica(canal)
    
    #print(f'Canal 1: {c1}')
    
    if board:
        led1.duty(c1)
        led2.duty(aplica(canal+1))
        led3.duty(aplica(canal+2))
        led4.duty(aplica(canal+3))


def test_callback2(data,addr):
    registra(addr)



if __name__=='__main__':
    from rede import do_connect
    
    do_connect()



#do_connect()


#from urllib import urlopen
#result=urlopen('http://portainer.local/')


#print(result)


universe=1
a=StupidArtnetServer()

# For every universe we would like to receive,
# add a new listener with a optional callback
# the return is an id for the listener
u1_listener=a.register_listener(
    universe,callback_function=test_callback)

#u2_listener=a.register_listener(
#    8,callback_function=test_callback2)



if __name__=='__main__':
    while True:
        time.sleep(1)