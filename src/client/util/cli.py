import sys


__all__ = [
    "prompt_ranged_int",
    "prompt_ranged_int_or_none",
    "prompt_int",
    "prompt_int_or_none",
]


def prompt_ranged_int(
    prompt:               str,
    lower_bound:          int,
    upper_bound:          int,
    nan_message:          str = "Input is not an integer!\n",
    out_of_range_message: str = "Value is out of range\n",
) -> int:
    while True:
        number = prompt_ranged_int_or_none(
            prompt,
            lower_bound,
            upper_bound,
            nan_message,
            out_of_range_message,
        )

        if number is None:
            print(nan_message, file = sys.stderr)
            continue

        return number

def prompt_ranged_int_or_none(
    prompt:               str,
    lower_bound:          int,
    upper_bound:          int,
    nan_message:          str = "Input is not an integer!\n",
    out_of_range_message: str = "Value is out of range\n",
) -> int | None:
    if lower_bound > upper_bound:
        raise ValueError("lower_bound > upper_bound")

    while True:
        number = prompt_int_or_none(prompt, nan_message)

        if number is None:
            return None

        if number < lower_bound or number > upper_bound:
            print(out_of_range_message, file = sys.stderr)
            continue

        return number

def prompt_int(
    prompt:       str,
    nan_message:  str = "Input is not an integer!\n",
) -> int:
    while True:
        try:
            return int(input(prompt))
        except:
            print(nan_message, file = sys.stderr)
            continue

def prompt_int_or_none(
    prompt:       str,
    nan_message:  str = "Input is not an integer!\n",
) -> int | None:
    while True:
        text = input(prompt).strip()

        if len(text) == 0:
            return None

        try:
            number = int(text)
        except:
            print(nan_message, file = sys.stderr)
            continue

        return number
