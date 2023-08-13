import board

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