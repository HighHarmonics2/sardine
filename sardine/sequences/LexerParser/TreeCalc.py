from lark import Transformer, v_args
from typing import Union
from .Qualifiers import qualifiers
from .Utilities import zip_cycle, map_unary_function, map_binary_function
from . import FuncLibrary
from lark.lexer import Token
from typing import Any
from itertools import cycle, takewhile, count
from time import time
import datetime
import random
from rich import print
from rich.panel import Panel


@v_args(inline=True)
class CalculateTree(Transformer):
    def __init__(self, clock, iterators, variables):
        super().__init__()
        self.clock = clock
        self.iterators = iterators
        self.variables = variables
        self.memory = {}

    def number(self, number):
        try:
            return [int(number)]
        except ValueError:
            return [float(number)]

    def return_pattern(self, *args):
        return list(args)

    # ---------------------------------------------------------------------- #
    # Silence: handling silence
    # ---------------------------------------------------------------------- #

    def silence(self, *args):
        """
        Pure silence. The absence of an event. Silence is represented using
        a dot or multiple dots for multiple silences.
        """
        return [None] * len(args)

    # ---------------------------------------------------------------------- #
    # Variables: methods concerning bi-valent variables
    # ---------------------------------------------------------------------- #

    def get_variable(self, letter):
        letter = str(letter)
        return [getattr(self.variables, letter)]

    def reset_variable(self, letter):
        letter = str(letter)
        self.variables.reset(letter)
        return [getattr(self.variables, letter)]

    def set_variable(self, letter, number):
        letter, number = str(letter), int(number)
        setattr(self.variables, letter, number)
        return [getattr(self.variables, letter)]

    # ---------------------------------------------------------------------- #
    # Iterators: methods concerning iterators
    # ---------------------------------------------------------------------- #

    def get_iterator(self, letter):
        letter = str(letter)
        return [getattr(self.iterators, letter)]

    def reset_iterator(self, letter):
        letter = str(letter)
        self.iterators.reset(letter)
        return [getattr(self.iterators, letter)]

    def set_iterator(self, letter, number):
        letter, number = str(letter), int(number)
        setattr(self.iterators, letter, number)
        return [getattr(self.iterators, letter)]

    def set_iterator_step(self, letter, number, step):
        letter, number, step = str(letter), int(number), int(step)
        setattr(self.iterators, letter, [number, step])
        return [getattr(self.iterators, letter)]

    # ---------------------------------------------------------------------- #
    # Notes: methods used by the note-specific parser
    # ---------------------------------------------------------------------- #

    def specify_address(self, name0, name1):
        """Convert underscore into slash for name based addresses"""
        return "".join([name0, "/", name1])

    def random_note_in_range(self, number0, number1):
        """Generates a random MIDI Note in the range number0 - number1.

        Args:
            number0 (int):  low boundary
            number1 (int): high boundary

        Returns:
            int: a random MIDI Note.
        """
        return random.randint(int(number0), int(number1))

    def make_note(self, note):
        """Return a valid MIDI Note (fifth octave)
        from a valid anglo-saxon, french or canadian note name.

        Args:
            note (str): a string representing a valid note ("A" to "G", or "Do" to "Si").

        Returns:
            int: A MIDI Note (fifth octave)
        """
        if note in ["A", "La"]:
            return 0 + 12 * 5
        elif note in ["B", "Si", "Ti"]:
            return 2 + 12 * 5
        elif note in ["C", "Do"]:
            return 3 + 12 * 5
        elif note in ["D", "Re", "Ré"]:
            return 5 + 12 * 5
        elif note in ["E", "Mi"]:
            return 7 + 12 * 5
        elif note in ["F", "Fa"]:
            return 8 + 12 * 5
        elif note in ["G", "Sol"]:
            return 10 + 12 * 5

    def note_flat(self, note):
        """Flatten a note"""
        return note - 1

    def note_sharp(self, note):
        """Sharpen a note"""
        return note + 1

    def note_set_octave(self, note, value):
        """Move a note to a given octave"""
        return (note % 12) + 12 * int(value)

    def note_octave_up(self, note):
        """Move a note one octave up"""
        return note + 12

    def note_octave_down(self, note):
        """Move a note one octave down"""
        return note - 12

    def finish_note(self, note):
        """Finish the note construction"""
        return [note]

    def add_qualifier(self, note, *quali):
        """Adding a qualifier to a note taken from a qualifier list.
        Adding a qualifier is the main method to generate scales and
        chords in a monophonic fashion (each note layed out as a list).

        Qualifiers are applied by taking the first note as a reference,
        and building the collection of notes against it. Eg: c5:major
        the reference note -> [60, added notes from coll -> 67, 72]

        Args:
            note (int): A MIDI Note

        Returns:
            list: A collection of notes built by applying a collection to
            the note given as input.
        """
        quali = list(quali)
        quali = "".join([str(x) for x in quali])
        try:
            return [note + x for x in qualifiers[str(quali)]]
        except KeyError:
            return note

    def make_number(self, *token):
        """Turn a number from string to integer. Used by the parser,
        transform a token matched as a string to a number before
        applying other rules.

        Returns:
            int: an integer
        """
        return int("".join(token))

    def id(self, a):
        """Identity function. Returns first argument."""
        return a

    def make_list(self, *args):
        """Make a list from gathered arguments (alias used by parser)

        Returns:
            list: Gathered arguments in a list
        """
        return sum(args, start=[])

    def get_time(self):
        """Return current clock time (tick) as integer"""
        return [int(self.clock.tick)]

    def get_year(self):
        """Return current clock time (tick) as integer"""
        return [int(datetime.datetime.now().year)]

    def get_month(self):
        """Return current clock time (tick) as integer"""
        return [int(datetime.datetime.now().month)]

    def get_day(self):
        """Return current clock time (tick) as integer"""
        return [int(datetime.datetime.now().day)]

    def get_hour(self):
        """Return current clock time (tick) as integer"""
        return [int(datetime.datetime.now().hour)]

    def get_minute(self):
        """Return current clock time (tick) as integer"""
        return [int(datetime.datetime.now().minute)]

    def get_second(self):
        """Return current clock time (tick) as integer"""
        return [int(datetime.datetime.now().second)]

    def get_microsecond(self):
        """Return current clock time (tick) as integer"""
        return [int(datetime.datetime.now().microsecond)]

    def get_measure(self):
        """Return current measure (bar) as integer"""
        return [int(self.clock.bar)]

    def get_phase(self):
        """Return current phase (phase) as integer"""
        return [int(self.clock.phase)]

    def get_unix_time(self):
        """Return current unix time as integer"""
        return [int(time())]

    def get_random_number(self):
        """Return a random number (alias used by parser)

        Returns:
            float: a random floating point number
        """
        return [random.random()]

    def generate_ramp(self, left, right):
        """Generates a ramp of integers between x included and y
        included (used by parser). Note that this is an extension
        of Python's default range function: descending ranges are
        possible.

        Args:
            left (int): First boundary
            right (int): Second boundary

        Returns:
            list: a ramp of ascending or descending integers
        """
        ramp_from = left[-1]
        ramp_to = right[0]
        between = range(min(ramp_from, ramp_to) + 1, max(ramp_from, ramp_to))
        between_flipped = between if ramp_from <= ramp_to else reversed(between)
        return left + list(between_flipped) + right

    def generate_ramp_with_range(self, left, right, step=1):
        """Generates a ramp of integers between x included and y
        included (used by parser). Variant using a step param.

        Args:
            left (int): First boundary
            right (int): Second boundary
            step (int): Range every x steps

        Returns:
            list: a ramp of ascending or descending integers with step
        """

        epsilon = 0.0000001
        start = min(left, right)
        stop = max(left, right)
        ramp = list(
            takewhile(
                lambda x: x < stop + epsilon, (start + i * abs(step) for i in count())
            )
        )
        if left > right:
            return list(reversed(ramp))
        else:
            return ramp

    def extend(self, left, right):
        """Extend a token: repeat the token x times. Note that this function
        will work for any possible type on its left and right side. A list
        can extend a list, etc.. etc.. See examples for a better understanding
        of the mechanism.

        Examples:
        [1,2,3]![1,2,3] -> [1,2,2,3,3,3]
        1!3 -> [1,1,1]
        [2,1]!4 -> [2,1,2,1,2,1,2,1]
        etc..

        Args:
            left (Union[list, float, int]): A token that will be extended
            right (Union[list, float, int]): A token used as an extension rule

        Returns:
            list: A list of integers after applying the expansion rule.
        """
        return left * sum(int(x) for x in right)

    def extend_repeat(self, left, right):
        """Variation of the preceding rule.
        TODO: document this behavior."""
        return sum(([x] * int(y) for (x, y) in zip_cycle(left, right)), start=[])

    def choice(self, left, right):
        """Choose 50%-50% between the 'left' or 'right' token

        Args:
            left (any): First possible choice
            right (any): Second possible choice

        Returns:
            any: A token chosen between 'left' or 'right'.
        """
        return random.choice([left, right])

    def random_in_range(self, left, right):
        def my_random(low, high):
            if isinstance(low, int) and isinstance(high, int):
                return random.randint(low, high)
            else:
                return random.uniform(low, high)

        return map_binary_function(my_random, left, right)

    def negation(self, value):
        return map_unary_function(lambda x: -x, value)

    def addition(self, left, right):
        return map_binary_function(lambda x, y: x + y, left, right)

    def modulo(self, left, right):
        return map_binary_function(lambda x, y: x % y, left, right)

    def power(self, left, right):
        return map_binary_function(lambda x, y: pow(x, y), left, right)

    def substraction(self, left, right):
        return map_binary_function(lambda x, y: x - y, left, right)

    def multiplication(self, left, right):
        return map_binary_function(lambda x, y: x * y, left, right)

    def division(self, left, right):
        return map_binary_function(lambda x, y: x / y, left, right)

    def floor_division(self, left, right):
        return map_binary_function(lambda x, y: x // y, left, right)

    def name(self, name):
        """Generating a name"""
        return str(name)

    def assoc_sp_number(self, name, value):
        def _simple_association(name, value):
            return name + ":" + str(int(value))

        return map_binary_function(_simple_association, name, value)

    def finish_patname(self, patname):
        """Finish the patname construction"""
        return [patname]

    def function_call(self, func_name, *args):
        modifiers_list = {
            "expand": FuncLibrary.expand,
            "disco": FuncLibrary.disco,
            "palindrome": FuncLibrary.palindrome,
            "reverse": FuncLibrary.reverse,
            "braid": FuncLibrary.braid,
            "shuffle": FuncLibrary.shuffle,
            "drop2": FuncLibrary.drop2,
            "drop3": FuncLibrary.drop3,
            "drop2and4": FuncLibrary.drop2and4,
            "sin": FuncLibrary.sin,
            "cos": FuncLibrary.cos,
            "tan": FuncLibrary.tan,
        }
        try:
            return modifiers_list[func_name](*args)
        except Exception as e:
            # Fail safe
            print(
                Panel.fit(
                    f"[red]/!\\\\[/red] Unknown function: [bold yellow]{func_name}[/bold yellow]\n"
                    + "".join(f"\n- {name}" for name in modifiers_list.keys())
                )
            )
            return args[0]
