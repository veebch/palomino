[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

# Dolphin
The code for an easy-on-the-eye, kind-to-the-ear music player display - all the heavy lifting is done by Volumio.

## Hardware
Volumio is running on a Pi4 on the same LAN as the viewer.
The viewer is running one [of these](https://www.veeb.ch/store/p/tickerxl), which is essentially a Raspberry Pi Zero WH and an EPD in a custom frame.

## Prerequisites

- A working Pi with waveshare 6inch HD ePaper attached
- The Python module for [IT8951](https://github.com/GregDMeyer/IT8951) installed

## Installation 

Clone the repository then install the required modules using `python3 -m pip install -r requirements.txt` then 
move to the directory and copy the example config file and tailor to your needs:
```
cd dolphin
cp config_example.yaml config.yaml
```
Then you can run using
```
python3 dolphin.py
```

## Add Autostart

```
cat <<EOF | sudo tee /etc/systemd/system/dolphin.service
[Unit]
Description=dolphin
After=network.target

[Service]
ExecStart=/usr/bin/python3 -u /home/pi/dolphin/dolphin.py
WorkingDirectory=/home/pi/dolphin/
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
sudo systemctl enable dolphin.service
sudo systemctl start dolphin.service

sudo reboot
```
## Licence

GNU GENERAL PUBLIC LICENSE Version 3.0
 
