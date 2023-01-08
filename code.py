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

start = ticks_ms()
import morse
end = ticks_ms()
print(f"Morse setup time: {end-start}ms")

# Set up a keyboard device.
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

displayio.release_displays()
i2c = busio.I2C(scl=board.GP17, sda=board.GP16)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

line1 = label.Label(terminalio.FONT, text="One", x=0, y=8)
line2 = label.Label(terminalio.FONT, text="Percent", x=0, y=24)

label_group = displayio.Group()
label_group.append(line1)
label_group.append(line2)
display.show(label_group)

pixels = neopixel.NeoPixel(board.GP14, 1)

key = digitalio.DigitalInOut(board.GP15)
key.direction = digitalio.Direction.INPUT
key.pull = digitalio.Pull.UP

async def update_count():
    n = 0
    while True:
        n += 1
        if not key.value:
            pixels[0] = (100 * (n & 1), 50 * (n & 2), 100 * (n & 4))
        else:
            pixels[0] = (0,0,0)
        await asyncio.sleep(0.01)

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
            while not key.value and keydown.duration < 1000:
                await asyncio.sleep(0)

        if keydown.duration < 1000:
            is_dit = keydown.duration < 150
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
            while key.value and keyup.duration < 300: await asyncio.sleep(0)
            if key.value and cursor and cursor.symbol:
                text = text[-15:]+cursor.symbol
                layout.write(cursor.symbol)
                cursor = morse.root
                line2.text = text
                code = line1.text = ""

            pixels[0] = (0,0,128)
            while key.value and keyup.duration < 700: await asyncio.sleep(0)
            if key.value:
                text = text[-15:]+" "
                line2.text = text
                layout.write(" ")
                cursor = morse.root
                code = line1.text = ""
            
            pixels[0] = (0,0,0)
            while key.value: await asyncio.sleep(0)
    

async def main():
    #counter_task = asyncio.create_task(update_count())
    #key_task = asyncio.create_task(time_key())
    #await asyncio.gather(counter_task, key_task)
    await time_key()

asyncio.run(main())