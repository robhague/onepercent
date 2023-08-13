"""Morse Code Translator -- --- .-. ... .

A module to convert morse code into symbols
"""

# Raw Morse Code lookup
morse_table = {
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
}

class MorseNode:
    def __init__(self):
        self.symbol = self.dit = self.dah = None
    
    def insert(self, morse, symbol):
        if len(morse) == 0:
            self.symbol = symbol
        elif morse[0] == ".":
            if self.dit is None: self.dit = MorseNode()
            self.dit.insert(morse[1:], symbol)
        else:
            if self.dah is None: self.dah = MorseNode()
            self.dah.insert(morse[1:], symbol)

# Set up the tree based on the lookup table
# We could do this ahed of time, but as it takes less than 100ms on the
# RP2040 we can do it at runtime for simplicity.
root = MorseNode()
for morse, symbol in morse_table.items():
    root.insert(morse, symbol)


