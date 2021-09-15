
import time
from colorsys import hsv_to_rgb
from PIL import ImageFont, Image, ImageDraw, ImageStat
import os
import os.path
from os import path
from IT8951 import constants
from socketIO_client import SocketIO, LoggingNamespace
import requests
from io import BytesIO
from numpy import mean
import logging
# logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
# logging.basicConfig()

# get the path of the script
script_path = os.path.dirname(os.path.abspath( __file__ ))
# set script path as current directory
os.chdir(script_path)


def on_connect():
    print('connect')
    return 'connected'

def display_image_8bpp(display, img, config):

    dims = (display.width, display.height)
    img.thumbnail(dims)
    paste_coords = [dims[i] - img.size[i] for i in (0,1)]  # align image with bottom of display
    img=img.rotate(180, expand=True)
    if config['display']['inverted']==True:
        img = ImageOps.invert(img)
    display.frame_buf.paste(img, paste_coords)
    display.draw_full(constants.DisplayModes.GC16)
    return

def on_push_state(*args):
    # print('state', args)
    # img = Image.new('RGB', (240, 240), color=(0, 0, 0, 25))
    img = Image.new('RGBA', (240, 240), color=(0, 0, 0, 25))
    status = args[0]['status'].encode('ascii', 'ignore')

    # Load albumcover or radio cover
    albumart = args[0]['albumart'].encode('ascii', 'ignore')
    # print 'Albumart0:',albumart
    # print 'Laenge Albumart0:',len(albumart)

    if len(albumart) == 0:  # to catch a empty field on start
        albumart = 'http://boombox.local:3000/albumart'
        # print 'Albumart1:',albumart
    if 'http:' not in albumart:
        albumart = 'http://boombox.local:3000'+args[0]['albumart']
        # print 'http hinzugefugt:',albumart

    # print 'Albumart2:',albumart
    response = requests.get(albumart)
    img = Image.open(BytesIO(response.content))
    img = img.resize((WIDTH, HEIGHT))

    # Light / Dark Symbols an bars, depending on background
    im_stat = ImageStat.Stat(img)
    im_mean = im_stat.mean
    mn = mean(im_mean)

    txt_col = (255, 255, 255)
    bar_col = (255, 255, 255, 255)
    dark = False
    if mn > 175:
        txt_col = (55, 55, 55)
        dark = True
        bar_col = (100, 100, 100, 225)
    if mn < 80:
        txt_col = (200, 200, 200)

    # print 'Modus dark:',dark

    # paste button symbol overlay in light/dark mode
    if status == 'play':
        if dark is False:
            img.paste(pause_icons, (0, 0), pause_icons)
        else:
            img.paste(pause_icons_dark, (0, 0), pause_icons_dark)
    else:
        if dark is False:
            img.paste(play_icons, (0, 0), play_icons)
        else:
            img.paste(play_icons_dark, (0, 0), play_icons_dark)

    # img
    # img = Image.new('RGB', (240, 240), color=(0, 0, 0, 25))
    # draw
    draw = ImageDraw.Draw(img, 'RGBA')

    top = 7
    if 'artist' in args[0]:
        x1 = 20
        w1, y1 = draw.textsize(args[0]['artist'], font_m)
        x1 = x1-20
        if x1 < (WIDTH - w1 - 20):
            x1 = 0
        if w1 <= WIDTH:
            x1 = (WIDTH - w1)//2
        draw.text((x1, top), args[0]['artist'], font=font_m, fill=txt_col)
        # print 'Artist:',args[0]['artist']

    top = 35

    if 'album' in args[0]:
        # print 'Album:',args[0]['album']
        # if args[0]['album'] != None:
        if args[0]['album'] is not None:
            x2 = 20
            w2, y2 = draw.textsize(args[0]['album'], font_s)
            x2 = x2-20
            if x2 < (WIDTH - w2 - 20):
                x2 = 0
            if w2 <= WIDTH:
                x2 = (WIDTH - w2)//2
            draw.text((x2, top), args[0]['album'], font=font_s, fill=txt_col)

    if 'title' in args[0]:
        x3 = 20
        w3, y3 = draw.textsize(args[0]['title'], font_l)
        x3 = x3-20
        if x3 < (WIDTH - w3 - 20):
            x3 = 0
        if w3 <= WIDTH:
            x3 = (WIDTH - w3)//2
            # thin border
            # shadowcolor = "black"
            # draw.text((x3-1, 105), args[0]['title'], font=font_l, fill=shadowcolor)
            # draw.text((x3+1, 105), args[0]['title'], font=font_l, fill=shadowcolor)
            # draw.text((x3, 105-1), args[0]['title'], font=font_l, fill=shadowcolor)
            # draw.text((x3, 105+1), args[0]['title'], font=font_l, fill=shadowcolor)y
        draw.text((x3, 105), args[0]['title'], font=font_l, fill=txt_col)  # fill by mean

    # volume bar
    # volume = args[0]['volume']
    # vol_x = int((float(volume)/100)*(WIDTH - 33))
    # volume = args[0]['volume']
    vol_x = int((float(args[0]['volume'])/100)*(WIDTH - 33))
    # draw.text((200, 200), str(volume), font=font_m) #volume
    draw.rectangle((5, 184, WIDTH-34, 184+8), (255, 255, 255, 145))
    draw.rectangle((5, 184, vol_x, 184+8), bar_col)

    # time bar
    if 'duration' in args[0]:
        duration = args[0]['duration']  # seconds
        # print 'duration found:',duration
        if duration != 0:
            # print 'duration ungleich 0'
            if 'seek' in args[0]:
                seek = args[0]['seek']  # time elapsed seconds
                # print 'seek found:',seek
                if seek != 0:
                    el_time = int(float(args[0]['seek'])/1000)
                    du_time = int(float(args[0]['duration']))
                    dur_x = int((float(el_time)/float(du_time))*(WIDTH-10))
                    draw.rectangle((5, 222, WIDTH-5, 222 + 12), (255, 255, 255, 145))
                    draw.rectangle((5, 222, dur_x, 222 + 12), bar_col)

    # print status + ',' + title + ',' + albumart + ', Vol:' + str(volume)
    # Draw the image on the display hardware
    (img)

socketIO = SocketIO('boombox.local', 3000)
socketIO.on('connect', on_connect)

#Initialise display

WIDTH = 240
HEIGHT = 240
font_s = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf', 20)
font_m = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf', 24)
font_l = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf', 30)

# img = Image.new('RGB', (240, 240), color=(0, 0, 0, 25))

play_icons = Image.open('images/controls-play.png').resize((240, 240))
play_icons_dark = Image.open('images/controls-play-dark.png').resize((240, 240))
pause_icons = Image.open('images/controls-pause.png').resize((240, 240))
pause_icons_dark = Image.open('images/controls-pause-dark.png').resize((240, 240))

# Set up the button
button = gpiozero.Button(17)
button.when_pressed = lambda: togglebutton(display) # Note missing brackets, it's a label
img = Image.new("RGB", (1448, 1072), color = (255, 255, 255) )
display_image_8bpp(display,img, config)
# draw = ImageDraw.Draw(img, 'RGBA')


def main():
    if not args.virtual:
        from IT8951.display import AutoEPDDisplay

        logging.info('Initializing EPD...')

        # here, spi_hz controls the rate of data transfer to the device, so a higher
        # value means faster display refreshes. the documentation for the IT8951 device
        # says the max is 24 MHz (24000000), but my device seems to still work as high as
        # 80 MHz (80000000)
        display = AutoEPDDisplay(vcom=config['display']['vcom'], rotate=args.rotate, spi_hz=24000000)

        #logging.info('VCOM set to', str(display.epd.get_vcom()))

    else:
        from IT8951.display import VirtualEPDDisplay
        display = VirtualEPDDisplay(dims=(1448, 1072), rotate=args.rotate)

    while True:
        print ('Main looping')
        # connecting to socket
        socketIO.on('pushState', on_push_state)
        # get initial state
        socketIO.emit('getState', '', on_push_state)
        socketIO.wait()
        # socketIO.wait_for_callbacks(seconds=1)
        time.sleep(1)

if __name__ == '__main__':
        try:
            main()
        except KeyboardInterrupt:
            img = Image.new('RGB', (240, 240), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.rectangle((0, 0, 240, 240), (0, 0, 0))
            disp.display(img)
            pass