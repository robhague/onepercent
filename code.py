import board
import busio
import displayio
import digitalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
import terminalio
import asyncio
import neopixel

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

from supervisor import ticks_ms

# Durations (ms) for various stages
class Durations:
    dit = 150 # Max duration for a dit; longer is a dah
    clear = 1000 # Time to clear the display
    symbol = 300 # Gap that signals the end of a symbol
    space = 700 # Gap that signals a space

# Set up morse table
start = ticks_ms()
import morse
end = ticks_ms()
print(f"Morse setup time: {end-start}ms")

# Identify device-specific pins
if "tiny2040" in board.board_id:
    print("Tiny2040 Config")
    display_sda, display_scl = board.GP2, board.GP3
    neopixel_pin = board.GP28
    key_pin = board.GP27

else:
    print("Default (Pico) Config")
    display_sda, display_scl = board.GP16, board.GP17
    neopixel_pin = board.GP14
    key_pin = board.GP15

# Set up a keyboard device.
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

# Set up display
displayio.release_displays()
display_i2c = busio.I2C(scl=display_scl, sda=display_sda)
if display_i2c.try_lock():
    print("I2C devices:", display_i2c.scan())
    display_i2c.unlock()
display_bus = displayio.I2CDisplay(display_i2c, device_address=0x3c)

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

line1 = label.Label(terminalio.FONT, text="One", x=0, y=8)
line2 = label.Label(terminalio.FONT, text="Percent", x=0, y=24)

label_group = displayio.Group()
label_group.append(line1)
label_group.append(line2)
display.show(label_group)

pixels = neopixel.NeoPixel(neopixel_pin, 1)

key = digitalio.DigitalInOut(key_pin)
key.direction = digitalio.Direction.INPUT
key.pull = digitalio.Pull.UP


class Timer:
    def __enter__(self):
        self.start = ticks_ms()
        self._duration = None
        return self

    @property
    def duration(self):
        return self._duration or (ticks_ms() - self.start)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._duration = self.duration or 1
        return False

async def time_key():
    code = text = ""
    cursor = morse.root

    # Wait until the first keypress
    while key.value: await asyncio.sleep(0)

    while True:
        # Time duration of keypress

        pixels[0] = (128,128,128)
        with Timer() as keydown:
            while not key.value and keydown.duration < Durations.clear:
                await asyncio.sleep(0)

        if keydown.duration < Durations.clear:
            is_dit = keydown.duration < Durations.dit
            code = code[-8:]+('.' if is_dit else '_')
            if cursor:
                cursor = cursor.dit if is_dit else cursor.dah
            line1.text = f"{code} {cursor.symbol if cursor and cursor.symbol else '?'}"
        else:
            pixels[0] = (128,0,0)
            code = line1.text = ""
            text = line2.text = ""
            while not key.value: await asyncio.sleep(0)

        pixels[0] = (0,128,0)
        with Timer() as keyup:
            while key.value and keyup.duration < Durations.symbol: await asyncio.sleep(0)
            if key.value and cursor and cursor.symbol:
                text = text[-15:]+cursor.symbol
                layout.write(cursor.symbol)
                cursor = morse.root
                line2.text = text
                code = line1.text = ""

            pixels[0] = (0,0,128)
            while key.value and keyup.duration < Durations.space: await asyncio.sleep(0)
            if key.value:
                text = text[-15:]+" "
                line2.text = text
                layout.write(" ")
                cursor = morse.root
                code = line1.text = ""
            
            pixels[0] = (0,0,0)
            while key.value: await asyncio.sleep(0)
    

async def main():
    await time_key()

asyncio.run(main())