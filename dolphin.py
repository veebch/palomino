
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
import gpiozero
import argparse
import yaml 

# logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
# logging.basicConfig()

# get the path of the script
script_path = os.path.dirname(os.path.abspath( __file__ ))
configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.yaml')
# set script path as current directory
os.chdir(script_path)

def togglebutton(display):
    dims = (display.width, display.height)
    img = Image.new("RGB", (1448, 1072), color = (255, 255, 255) )
    img.thumbnail(dims)
    paste_coords = [dims[i] - img.size[i] for i in (0,1)]  # align image with bottom of display
    logging.info("Reset Pressed, initiate shudown")
    filename = os.path.join(dirname, 'images/rabbitsq.png')
    imlogo = Image.open(filename)
    resize = 300,300
    imlogo.thumbnail(resize)
    clear_display(display)
    img.paste(imlogo,(100, 760))
    img=img.rotate(180, expand=True)
    display.frame_buf.paste(img, paste_coords)
    display.draw_full(constants.DisplayModes.GC16)
    os.system('sudo systemctl stop btcticker-start.service')


def parse_args():
    p = argparse.ArgumentParser(description='Test EPD functionality')   
    p.add_argument('-v', '--virtual', action='store_true',
                   help='display using a Tkinter window instead of the '
                        'actual e-paper device (for testing without a '
                        'physical device)')
    p.add_argument('-r', '--rotate', default=None, choices=['CW', 'CCW', 'flip'],
                   help='run the tests with the display rotated by the specified value')
    p.add_argument('-e', '--error', action='store_true',
                   help='Brings up the error screen for formatting')

    return p.parse_args()

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
    img = Image.new('RGBA', (WIDTH, HEIGHT), color=(255, 255 , 255, 0))
    status = args[0]['status'].encode('ascii', 'ignore')

    # Load albumcover or radio cover
    albumart = args[0]['albumart'].encode('ascii', 'ignore')
    # print 'Albumart0:',albumart
    # print 'Laenge Albumart0:',len(albumart)

    if len(albumart) == 0:  # to catch a empty field on start
        albumart = 'http://boombox.local:3000/albumart'
        # print 'Albumart1:',albumart
    # make this conditional
    albumart = 'http://boombox.local:3000'+args[0]['albumart']
        # print 'http hinzugefugt:',albumart

    # print 'Albumart2:',albumart
    response = requests.get(albumart)
    imgart = Image.open(BytesIO(response.content))
    imgart = imgart.convert("RGBA")
    imgart = imgart.resize((400, 400))
    img.paste(imgart, (850,150))

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

    print(status)
    indent = 200
    if status == b'play':
        img.paste(play_icons, (indent, 500))
    else:
        img.paste(pause_icons, (indent, 500))

    # img
    # img = Image.new('RGB', (240, 240), color=(0, 0, 0, 25))
    # draw
    draw = ImageDraw.Draw(img, 'RGBA')



    if 'artist' in args[0]:
        draw.text((indent, 150), args[0]['artist'], font=font_m, fill=txt_col)
        # print 'Artist:',args[0]['artist']

    if 'album' in args[0]:
        draw.text((indent,250),args[0]['album'], font=font_m, fill=txt_col)

    if 'title' in args[0]:
        draw.text((indent, 750), args[0]['title'], font=font_l, fill=txt_col)  # fill by mean

    vol_x = int((float(args[0]['volume'])/100)*(WIDTH - 33))
    draw.rectangle((5, 984, WIDTH-34, 984+8), (255, 255, 255, 145))
    draw.rectangle((5, 984, vol_x, 984+8), bar_col)
    # Only update if the song title has changed
    display_image_8bpp(display,img, config)

socketIO = SocketIO('boombox.local', 3000)
socketIO.on('connect', on_connect)

#Initialise display

WIDTH = 1448
HEIGHT = 1072 
font_s = ImageFont.truetype(script_path + '/fonts/Kanit-ExtraLight.ttf', 70)
font_m = ImageFont.truetype(script_path + '/fonts/Kanit-ExtraLight.ttf', 94)
font_l = ImageFont.truetype(script_path + '/fonts/Kanit-ExtraLight.ttf', 110)

# img = Image.new('RGB', (240, 240), color=(0, 0, 0, 25))

play_icons = Image.open('images/play.png').resize((240, 240)).convert("RGBA")
pause_icons = Image.open('images/pause.png').resize((240, 240)).convert("RGBA")

img = Image.new("RGB", (1448, 1072), color = (255, 255, 255) )
args = parse_args()
with open(configfile) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
logging.info("Read Config File")
logging.info(config)
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
# Set up the button
button = gpiozero.Button(17)
button.when_pressed = lambda: togglebutton(display) # Note missing brackets, it's a label

# draw = ImageDraw.Draw(img, 'RGBA')


def main():
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
            img = Image.new('RGB', (1448, 1072), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            draw.rectangle((0, 0, 240, 240), (0, 0, 0))
            display_image_8bpp(display,img, config)
            pass