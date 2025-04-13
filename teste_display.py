from icones import wifi_alert_48px
import framebuf






#def cria_framebuf(icon,width,height):
#    icone=framebuf.FrameBuffer(icon,
#                              width,height,
#                              framebuf.MONO_HLSB)
#return icone




if __name__=='__main__':
    from display import display
    
    with display:
        wifi_alert_48px.blit(40,0)
        display.text('WiFi',48,50)
