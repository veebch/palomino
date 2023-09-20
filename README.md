[![Action Shot](/images/Dolphin.jpg)](https://youtu.be/7x2k6CjCG04)

[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/v_e_e_b/)

# Palomino: A high definition ePaper 'Now Playing' viewer For Volumio
Code for an easy-on-the-eye ePaper display that talks to a kind-to-the-ear, bit-perfect music player. All of the musical heavy lifting is done by [Volumio](https://github.com/volumio/Volumio2). The code sets up a socket connection, listens for changes and updates the display when needed. 

## Hardware

**Palomino Track Viewer**:
- Raspberry Pi Zero WH
- E Paper Display (a Waveshare 6" HD screen)

The viewer in the [YouTube video](https://youtu.be/7x2k6CjCG04) is running a [veeb epaper display](https://www.veeb.ch/notes/a-musical-interlude), which is a Raspberry Pi Zero WH and a High Definition E-Paper Display in a custom frame.

For any of this to work, you'll have to be using a Volumio Server. 

**Volumio server**:
Hardware for this is covered [in detail elsewhere](https://volumio.com/en/), but the **tl;dr** is

- Raspberry Pi 4 
- Speakers with built in DAC (eg KEF LS50) **or** DAC (Hifiberry, IQAudio etc) and Sound System

## Prerequisites
- A Working Volumio server on your LAN
- A Pi Zero running Raspbian, with a Waveshare 6inch HD ePaper attached
- The Python module for [IT8951](https://github.com/GregDMeyer/IT8951) installed on the Pi Zero

## Installation 

All of this takes place on the Pi-Zero - **not on the volumio server** . 

From your home directory, clone the repository 

```
git clone git@github.com:llvllch/palomino.git
cd palomino
```

then install the required modules using `python3 -m pip install -r requirements.txt` then 
move to the directory and copy the example config file and tailor to your needs:
```
cp config_example.yaml config.yaml
```
You can then edit `config.yaml` file to set the name of your server.
Once that's done, you can run the code using the command:
```
python3 palomino.py
```
After a few seconds, the screen will show the track currently playing on you Volumio server.


## Add Autostart

Once you've got a working instance of the code, you will probably want it to start automatically every time you power up. You can use systemd to start the code as a service on boot.

```
cat <<EOF | sudo tee /etc/systemd/system/palomino.service
[Unit]
Description=palomino
After=network.target

[Service]
ExecStart=/usr/bin/python3 -u /home/pi/palomino/palomino.py
WorkingDirectory=/home/pi/palomino/
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF
```
Now, simply enable the service you just made and reboot...
```  
sudo systemctl enable palomino.service
sudo systemctl start palomino.service

sudo reboot
```

## Video

Click/Tap the image at the top of this readme.


## Licence

GNU GENERAL PUBLIC LICENSE Version 3.0
 
