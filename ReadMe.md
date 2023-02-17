# The One Percent

A novelty single-key keyboard by Rob Hague.

## Components

- An RP2040 board that supports CircuitPython
- An AdaFruit NanoKey
- An MX-compatible switch and keycap
- An SSD1306 I2C OLED display (128x32px)

## Software setup

1. Install CircuitPython
2. Download the [CircuitPython Libraries Bundle](https://circuitpython.org/libraries) and copy the following libraries to a `lib/` directory on the CircuitPython device:
  - `adafruit_displayio_ssd1306`
  - `adafruit_display_text`
  - `asyncio`
  - `adafruit_ticks`
  - `neopixel`
  - `adafruit_hid`
