from __future__ import annotations
import math
from . import exceptions

letters = [
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "0",
    " ",
    "a",
    "A",
    "b",
    "B",
    "c",
    "C",
    "d",
    "D",
    "e",
    "E",
    "f",
    "F",
    "g",
    "G",
    "h",
    "H",
    "i",
    "I",
    "j",
    "J",
    "k",
    "K",
    "l",
    "L",
    "m",
    "M",
    "n",
    "N",
    "o",
    "O",
    "p",
    "P",
    "q",
    "Q",
    "r",
    "R",
    "s",
    "S",
    "t",
    "T",
    "u",
    "U",
    "v",
    "V",
    "w",
    "W",
    "x",
    "X",
    "y",
    "Y",
    "z",
    "Z",
    "*",
    "/",
    ".",
    ",",
    "!",
    '"',
    "§",
    "$",
    "%",
    "_",
    "-",
    "(",
    "´",
    ")",
    "`",
    "?",
    "new line",
    "@",
    "#",
    "~",
    ";",
    ":",
    "+",
    "&",
    "|",
    "^",
    "'"
]


class Encoding:
    """
    Class that contains tools for encoding / decoding strings. The strings encoded / decoded with these functions can be decoded / encoded with Scratch using this sprite: https://scratch3-assets.1tim.repl.co/Encoder.sprite3
    """
    @staticmethod
    def decode(inp):
        """
        Args:
            inp (str): The encoded input.

        Returns:
            str: The decoded output.
        """
        try:
            inp = str(inp)
        except Exception:
            raise(exceptions.InvalidDecodeInput)
        outp = ""
        for i in range(0, math.floor(len(inp) / 2)):
            letter = letters[int(f"{inp[i*2]}{inp[(i*2)+1]}")]
            outp = f"{outp}{letter}"
        return outp

    @staticmethod
    def encode(inp):
        """
        Args:
            inp (str): The decoded input.
            
        Returns:
            str: The encoded output.
        """
        inp = str(inp)
        outp = ""
        for i in inp:
            if i in letters:
                outp = f"{outp}{letters.index(i)}"
            else:
                outp += str(letters.index(" "))
        return outp

    @staticmethod
    def replace_char(old_char, new_char):
        """
        Replaces a character in the list that the encoder uses to encode / decode values.
        You can access this list using `scratchattach.encoder.letters`
        """
        i = letters.index(old_char)
        letters[i] = new_char
        