# Requirements

* Python 2.7.x
* Python 2.7.x Dev 
* Pip
* Portaudio: `brew install portaudio`
* Install dependencies: `pip install -r requirements.txt`

# For Pi usage:

* `sudo apt-get install python-dev`
* `sudo apt-get install libportaudio-dev`
* `sudo apt-get install portaudio19-dev`
* `sudo apt-get install python-pip`
* `sudo pip install -r requirements.txt`

Enable usb audio:
https://github.com/alexa/alexa-avs-sample-app/issues/85
After struggling to do this cleanly with ASLA configs in raspbian "jesse", I gave up and solved this issue by brute force by just not loading the bcm2835 kernel driver for the default internal headphone jack. That way, my USB mic/speaker (Jabra SPEAK 510) is the only audio device.
	1.	Edit /boot/config.txt and comment out dtparam=audio=on
	2.	Edit /lib/modprobe.d/aliases.conf and comment out options snd-usb-audio index=-2
	3.	Reboot your pi

# Run

`python sensor.py --db <valueDb> [--ts <threshold_duration_seconds>] [--rs <reset_after_seconds>]`

e.g.

`python sensor.py --db 70`
