from __future__ import annotations
import os
import sys

# Ensure src on path when run from repo root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from turing_simulator import TuringMachine  # type: ignore


def _cfg(name: str) -> str:
    return os.path.join(ROOT, 'config', name)


def _run_tm(config_name: str, input_str: str) -> str:
    tm = TuringMachine(_cfg(config_name))
    return tm.run(input_str)


def key_letter_to_shift_marks(key_letter: str) -> str:
    """Convert A..Z to unary marks using the letter_to_number MT.
    A->'' (0), B->'|', ..., Z-> '|'*25
    """
    if not key_letter or not key_letter.isalpha() or len(key_letter) != 1:
        raise ValueError("La clave debe ser una sola letra A-Z")
    letter = key_letter.upper()
    return letter_to_marks(letter)


def letter_to_marks(letter: str) -> str:
    out = _run_tm('letter_to_number.json', letter)
    # Quedarnos solo con las marcas unarias
    return ''.join(ch for ch in out if ch == '|')


def marks_to_letter(marks: str) -> str:
    out = _run_tm('number_to_letter.json', marks)
    # Extraer la última letra A-Z que aparezca en la cinta de salida
    for ch in reversed(out):
        if 'A' <= ch <= 'Z':
            return ch
    # Fallback: si no hay letra explícita, asumir 'A' para 0 marcas
    return 'A'


def add_unary(a: str, b: str) -> str:
    out = _run_tm('add_simple.json', f"{a}+{b}")
    # Sanear: quedarnos solo con marcas unarias
    return ''.join(ch for ch in out if ch == '|')


def subtract_unary(a: str, b: str) -> str:
    out = _run_tm('subtract_simple.json', f"{a}-{b}")
    # Sanear: quedarnos solo con marcas unarias
    return ''.join(ch for ch in out if ch == '|')


def mod26(marks: str) -> str:
    """Reduce unary marks modulo 26 using only JSON-defined MTs.

    Implemented by repeatedly subtracting 26 (||||||||||||||||||||||||||)
    via the subtract machine until result length < 26.
    """
    twenty_six = '|' * 26
    # Guard simple cases
    if not marks:
        return ''
    # Loop using subtract_unary MT; control flow stays in Python (no arithmetic).
    # Hard stop to avoid runaway on malformed configs
    for _ in range(2000):
        # Sanear por si vienen restos
        marks = ''.join(ch for ch in marks if ch == '|')
        if len(marks) < 26:
            return marks
        marks = subtract_unary(marks, twenty_six)
    # If we ever hit the guard, return current best effort
    return marks


def encrypt_text(key_letter: str, text: str) -> str:
    shift_marks = key_letter_to_shift_marks(key_letter)
    out_chars = []
    for ch in text:
        u = ch.upper()
        if 'A' <= u <= 'Z':
            n_marks = letter_to_marks(u)
            s_marks = add_unary(n_marks, shift_marks)
            r_marks = mod26(s_marks)
            out_chars.append(marks_to_letter(r_marks))
        else:
            out_chars.append(ch)
    return ''.join(out_chars)


def decrypt_text(key_letter: str, text: str) -> str:
    shift_marks = key_letter_to_shift_marks(key_letter)
    # Compute (26 - shift) in unary using subtract machine
    const26 = '|' * 26
    inv_marks = subtract_unary(const26, shift_marks)
    out_chars = []
    for ch in text:
        u = ch.upper()
        if 'A' <= u <= 'Z':
            n_marks = letter_to_marks(u)
            s_marks = add_unary(n_marks, inv_marks)
            r_marks = mod26(s_marks)
            out_chars.append(marks_to_letter(r_marks))
        else:
            out_chars.append(ch)
    return ''.join(out_chars)
