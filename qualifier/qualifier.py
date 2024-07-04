import re
import warnings
from enum import StrEnum, auto

MAX_QUOTE_LENGTH = 50


class VariantMode(StrEnum):
    NORMAL = auto()
    UWU = auto()
    PIGLATIN = auto()


class DuplicateError(Exception):
    """Error raised when there is an attempt to add a duplicate entry to a database"""


# Implement the class and function below
class Quote:
    VOWELS = {"a", "e", "i", "o", "u"}
    STUTTERS = ("u", "U")

    def __init__(self, quote: str, mode: "VariantMode") -> None:
        self.quote = quote.strip('"').strip("“").strip("”")
        self.mode = mode

        if len(self.quote) > 50:
            raise ValueError("Quote is too long")

    def __str__(self) -> str:
        return self._create_variant()

    def _create_variant(self) -> str:
        """
        Transforms the quote to the appropriate variant indicated by `self.mode` and returns the result
        """
        match self.mode:
            case VariantMode.UWU:
                return self._do_uwu(self.quote)
            case VariantMode.PIGLATIN:
                return self._do_piglatin(self.quote)
        return self.quote

    def _do_uwu(self, quote):
        self.initial_quote = quote
        quote = (
            quote.replace("L", "W")
            .replace("R", "W")
            .replace("l", "w")
            .replace("r", "w")
        )

        self.quote_after_replace = quote
        quote = " ".join(
            [
                word[0] + "-" + word[:] if word[0] in Quote.STUTTERS else word
                for word in quote.split(" ")
            ]
        )

        if quote == self.initial_quote:
            raise ValueError("Quote was not modified")
        elif len(quote) > 50:
            quote = self.quote_after_replace
            warnings.warn("Quote too long, only partially transformed")

        return quote

    def _do_piglatin(self, quote):
        pieces = []

        for word in quote.lower().split(" "):
            if word[0] in Quote.VOWELS:
                word = word + "way"
            else:
                for index, char in enumerate(word):
                    if char in Quote.VOWELS:
                        word = word[index:] + word[:index] + "ay"
                        break

            pieces.append(word)

        quote = " ".join(pieces).capitalize()

        if len(quote) > 50:
            raise ValueError("Quote was not modified")

        return quote


def run_command(command: str) -> None:
    """
    Will be given a command from a user. The command will be parsed and executed appropriately.

    Current supported commands:
        - `quote` - creates and adds a new quote
        - `quote uwu` - uwu-ifys the new quote and then adds it
        - `quote piglatin` - piglatin-ifys the new quote and then adds it
        - `quote list` - print a formatted string that lists the current
           quotes to be displayed in discord flavored markdown
    """
    try:
        command = re.search(
            r"^(quote) (list|uwu|piglatin|“.*”|\".*\")?\s?(“.*”|\".*\")?$", command
        )
        if command:
            match command.groups():
                case _, "list" as mode, _:
                    print(f"- {"\n- ".join(Database.get_quotes())}")
                case _, "uwu" | "piglatin" as mode, quote:
                    Database.add_quote(Quote(quote, VariantMode(mode)))
                case _, quote, _:
                    Database.add_quote(Quote(quote, VariantMode.NORMAL))
        else:
            raise ValueError("Invalid command")
    except DuplicateError:
        print("Quote has already been added previously")


class Database:
    quotes: list["Quote"] = []

    @classmethod
    def get_quotes(cls) -> list[str]:
        "Returns current quotes in a list"
        return [str(quote) for quote in cls.quotes]

    @classmethod
    def add_quote(cls, quote: "Quote") -> None:
        "Adds a quote. Will raise a `DuplicateError` if an error occurs."
        if str(quote) in [str(quote) for quote in cls.quotes]:
            raise DuplicateError
        cls.quotes.append(quote)
