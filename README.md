![Action Shot](/images/Dolphin.jpg)

[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

# Palamino: A high definition ePaper 'Now Playing' viewer For Volumio
Code for an easy-on-the-eye ePaper display that talks to a kind-to-the-ear, bit-perfect music player. All of the musical heavy lifting is done by [Volumio](https://github.com/volumio/Volumio2). The code sets up a socket connection, listens for changes and updates the display when needed. The code is currently reflecting what is going on on the server, but adding control via the api is very straightforward.

## Hardware
Volumio server:
- Pi 4 and speakers with built in DAC (eg KEF LS50) **or**
- Pi 4 and DAC (Hifiberry, IQAudio etc) and Sound System

Track Viewer:
- Pi Zero WH
- E Paper Display (a Waveshare 6" HD screen)

The viewer in the YouTube video is running on one [of these](https://www.veeb.ch/store/p/tickerxl), which is a Raspberry Pi Zero WH and a High Definition E-Paper Display in a custom frame.

## Prerequisites
- A Working Volumio server on your LAN
- A Pi Zero running Raspbian, with a Waveshare 6inch HD ePaper attached
- The Python module for [IT8951](https://github.com/GregDMeyer/IT8951) installed on the Pi Zero

## Installation 

All of this takes place on the Pi-Zero. From your home directory, clone the repository 

```
git clone git@github.com:llvllch/palamino.git
cd palamino
```

then install the required modules using `python3 -m pip install -r requirements.txt` then 
move to the directory and copy the example config file and tailor to your needs:
```
cp config_example.yaml config.yaml
```
You can then edit `config.yaml` file to set the name of your server.
Once that's done, you can run the code using the command:
```
python3 palamino.py
```
After a few seconds, the screen will show the trach currently playing on you Volumio server.

## Add Autostart

You can use systemd to start the code as a service on boot.

```
cat <<EOF | sudo tee /etc/systemd/system/palamino.service
[Unit]
Description=palamino
After=network.target

[Service]
ExecStart=/usr/bin/python3 -u /home/pi/palamino/palamino.py
WorkingDirectory=/home/pi/palamino/
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF
```
Now, simply enable the service you just made and reboot
```  
sudo systemctl enable palamino.service
sudo systemctl start palamino.service

sudo reboot
```
## Licence

GNU GENERAL PUBLIC LICENSE Version 3.0
 
