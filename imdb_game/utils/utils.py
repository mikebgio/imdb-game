"""
Shared functions for imdb_game
"""
import unicodedata
import textwrap

IMDB_ROOT: str = 'https://www.imdb.com'


def justify_text(text: str, width: int) -> str:
    """
    Formats long strings for more readable console output
    Returns:
        str
    """
    # Wrap the input text into lines with the specified width
    wrapped_lines = textwrap.wrap(text, width=width)

    # Justify each line except for the last one
    justified_lines = []
    for line in wrapped_lines[:-1]:
        words = line.split()
        word_count = len(words)
        spaces = width - sum(len(word) for word in words)
        spaces_per_gap = spaces // (word_count - 1) if word_count > 1 else 0
        extra_spaces = spaces % (word_count - 1) if word_count > 1 else 0

        justified_line = ""
        for word in words[:-1]:
            justified_line += word + " " * (spaces_per_gap + (extra_spaces > 0))
            extra_spaces -= 1

        justified_line += words[-1]
        justified_lines.append(justified_line)

    # Add the last line without justification
    justified_lines.append(wrapped_lines[-1])

    # Join the lines with newline characters
    justified_text = "\n".join(justified_lines)

    return justified_text
def strip_text(input_text: str) -> str:
    """
    Returns input string in lowercase, with spaces removed, special characters
    removed, and accented characters normalized
    Returns:
        str
    """
    input_text = remove_accents(input_text)
    return ''.join(e for e in input_text if e.isalnum()).lower()


def remove_accents(input_str: str) -> str:
    """
    Takes a string and converts all accented characters to unaccented characters
    and returns the string with unaccented characters
    Returns:
        str
    """
    # Normalize the string to the NFKD form (Compatibility Decomposition)
    normalized_str = unicodedata.normalize("NFKD", input_str)
    # Filter out non-spacing marks and join the characters
    unaccented_str = "".join(
        c for c in normalized_str if unicodedata.category(c) != "Mn")
    return unaccented_str
