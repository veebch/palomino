
import time
from PIL import ImageFont, Image, ImageDraw, ImageOps
import os
from IT8951 import constants
from socketIO_client import SocketIO, LoggingNamespace
import requests
from io import BytesIO
import logging
import gpiozero
import argparse
import yaml 
import textwrap

def _place_text(img, text, x_offset=0, y_offset=0,fontsize=40,fontstring="Kanit-ExtraLight", fill=0):
    '''
    Put some horizontally centered text at a y location on the image.
    '''

    draw = ImageDraw.Draw(img)

    try:
        filename = os.path.join(dirname, './fonts/'+fontstring+'.ttf')
        font = ImageFont.truetype(filename, fontsize)
    except OSError:
        font = ImageFont.truetype('/usr/share/fonts/TTF/Kanit-ExtraLight.ttf', fontsize)

    img_width, img_height = img.size
    text_width, _ = font.getsize(text)
    text_height = fontsize

    draw_x = (img_width - text_width)//2 + x_offset
    draw_y = (img_height - text_height)//2 + y_offset

    draw.text((draw_x, draw_y), text, font=font,fill=fill )
    return 

def writewrappedlines(img,text,fontsize,y_text=0,height=3, width=15,fontstring="Kanit-ExtraLight"):
    '''
    Split over lines if the text is long
    '''
    lines = textwrap.wrap(text, width)
    numoflines=0
    for line in lines:
        _place_text(img, line,0, y_text, fontsize,fontstring)
        y_text += height
        numoflines+=1
    return img, numoflines


def togglebutton(display):
    '''
    The button on the Waveshare device, turned into a graceful power down
    '''
    dims = (display.width, display.height)
    img = Image.new("RGB", (1448, 1072), color = (255, 255, 255) )
    img.thumbnail(dims)
    paste_coords = [dims[i] - img.size[i] for i in (0,1)]  # align image with bottom of display
    logging.info("Reset Pressed, initiate shudown")
    imlogo = rabbit_icon
    clear_display(display)
    img.paste(imlogo,(100, 760))
    img=img.rotate(180, expand=True)
    display.frame_buf.paste(img, paste_coords)
    display.draw_full(constants.DisplayModes.GC16)
    os.system('sudo halt')

def clear_display(display):
    logging.info('Clearing display...')
    display.clear()

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
    logging.info('connect')
    return 'connected'

def display_image_8bpp(display, img):
    dims = (display.width, display.height)
    img.thumbnail(dims)
    paste_coords = [dims[i] - img.size[i] for i in (0,1)]  # align image with bottom of display
    img=img.rotate(180, expand=True)
    display.frame_buf.paste(img, paste_coords)
    display.draw_full(constants.DisplayModes.GC16)
    return

def on_push_state(*args):
    global lastpass
    # Only run screen update if the key arguments have changed since the last call. Key arguments are:
    # status
    # albumart
    # artist, album, title
    # Volume crosses mute threshold
    print(args[0]['status'])
    wasmuted = bool(lastpass['volume']<mutethresh)
    ismuted = bool(args[0]['volume']<mutethresh)
    if  (args[0]['title']!=lastpass['title'] and args[0]['status']!='stop') or \
        wasmuted!=ismuted or \
        (args[0]['status']!=lastpass['status'] and args[0]['status']!='stop'):
        lastpass = args[0]
        img = Image.new('RGBA', (display.width, display.height), color=(255, 255 , 255, 0))

        # Load cover
        albumart = args[0]['albumart'].encode('ascii', 'ignore')

        if len(albumart) == 0:  # to catch a empty field on start
            albumart = 'http://'+servername+':3000/albumart'
        # Make the album art link into a url & get it & paste it in
        albumart = 'http://'+servername+':3000'+args[0]['albumart']
        try:
            response = requests.get(albumart)
            imgart = Image.open(BytesIO(response.content))
            imgart = imgart.resize((coversize, coversize))
            imgart = imgart.convert("RGBA")
        except:
            imgart = Image.new('RGBA', (coversize, coversize), color=(255, 255, 255,0))
        img.paste(imgart, (int((display.width - coversize)/2),220))

        if args[0]['status'] in ['pause', 'stop'] :
            img.paste(pause_icons, (indent, 300), pause_icons)

        draw = ImageDraw.Draw(img, 'RGBA')
        fontsize = 80
        y_text = -450
        height = 80
        width = 25 
        if 'artist' in args[0]:
            img, numline=writewrappedlines(img,args[0]['artist'],fontsize,y_text,height, width,fontstring)
        y_text = 160
        height = 50
        fontsize = 50
        width = 30
        if 'album' in args[0]:
            if len(args[0]['album'])>30:
                titletext= args[0]['album'][:27]+'...'
            else:
                titletext=args[0]['album']
            img, numline=writewrappedlines(img,args[0]['album'],fontsize,y_text,height, width,fontstring)
        y_text = 280
        fontsize = 120
        height = 120
        width = 18
        if 'title' in args[0]:
            if len(args[0]['title'])>35:
                titletext= args[0]['title'][:30]+'...'
            else:
                titletext=args[0]['title']
            img, numline=writewrappedlines(img,titletext,fontsize,y_text,height, width,fontstring)

        vol_x = int(float(args[0]['volume']))
        if vol_x <= mutethresh: 
            logging.info('muted')
            img.paste(mute_icons, (iconheight , 300),mute_icons)
        display_image_8bpp(display,img)
    return

# get the path of the script

script_path = os.path.dirname(os.path.abspath( __file__ ))
dirname = os.path.dirname(__file__)
configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.yaml')
# set script path as current directory
os.chdir(script_path)

# Read config and Initialise display
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
    display = AutoEPDDisplay(vcom=config['display']['vcom'], rotate=args.rotate, spi_hz=60000000)

else:
    from IT8951.display import VirtualEPDDisplay
    display = VirtualEPDDisplay(dims=(1448, 1072), rotate=args.rotate)

# Set up the button

button = gpiozero.Button(17)
button.when_pressed = lambda: togglebutton(display) # Note missing brackets, it's a label

# Initialise some constants

rabbit_icon = Image.open('images/rabbitsq.png').resize((300, 300)).convert("RGBA")
pause_icons = Image.open('images/pause.png').resize((240, 240)).convert("RGBA")
mute_icons = Image.open('images/mute.png').resize((240, 240)).convert("RGBA")

coversize = config['display']['coversize']
mutethresh = config['sound']['mutethresh']
indent = config['display']['indent']
servername = config['server']['name']
fontstring = config['display']['font']

# Derive some constants

iconheight = display.width-240-indent
socketIO = SocketIO(servername, 3000)
socketIO.on('connect', on_connect)
lastpass = {
  "artist": "none",
  "title": "none",
  "album": "none",
  "albumart": "none",
  "status": "none",
  "volume": 60
}


def main():
    while True:
        # connecting to socket
        socketIO.on('pushState', on_push_state)
        # get initial state
        socketIO.emit('getState', '', on_push_state)
        # now wait
        socketIO.wait()
        logging.info('Reconnection needed')
        time.sleep(1)

if __name__ == '__main__':
        try:
            main()
        except KeyboardInterrupt:
            socketIO.disconnect()
            img = Image.new('RGBA', (1448, 1072), color=(255, 255, 255,0))
            img.paste(rabbit_icon,(100,760), rabbit_icon)
            display_image_8bpp(display,img)
            pass