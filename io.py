from vars import board,som,buzzer_pin,sinal_on_pin,sinal_off_pin
if board:
    from machine import Pin,PWM,reset
    from buzzer import Buzzer
    from beeps import zera
import Logging



if board:
    pwm=Pin(buzzer_pin)
    #pwm.off()
    
    
    
    buzzer=Buzzer(pwm)
    
    #if som:
    buzzer.play(zera)
    #pwm.off()
    
    
    led1=PWM(18)
    led2=PWM(19)
    #led3=PWM(21)
    #led4=PWM(22)
    

    led1.duty(0)
    led2.duty(0)
    #led3.duty(0)
    #led4.duty(0)
    
    
    pinoSinal_on=Pin(sinal_on_pin,Pin.OUT)
    pinoSinal_off=Pin(sinal_off_pin,Pin.OUT)
