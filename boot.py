# Disable the USB drive unless the key is held down
import digitalio
import storage

import conf

key = digitalio.DigitalInOut(conf.key_pin)
key.direction = digitalio.Direction.INPUT
key.pull = digitalio.Pull.UP

if key.value: # Key is not depressed
    storage.disable_usb_drive()