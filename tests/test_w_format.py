"""Pruebas del formato w (clave#mensaje)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from caesar_cipher_tm import CaesarCipherTM
from main import parse_w


def test_parse_numeric_key():
    shift, msg = parse_w("3#HOLA")
    assert shift == 3 and msg == "HOLA"


def test_parse_letter_key():
    shift, msg = parse_w("D#HOLA")
    assert shift == 3 and msg == "HOLA"  # D -> 3


def test_encrypt_with_w_numeric():
    shift, msg = parse_w("3#ROMA")
    cipher = CaesarCipherTM(shift=shift)
    assert cipher.encrypt(msg) == "URPD"


def test_encrypt_with_w_letter():
    shift, msg = parse_w("D#ABC XYZ")
    cipher = CaesarCipherTM(shift=shift)
    assert cipher.encrypt(msg) == "DEF ABC"


def test_decrypt_with_w_numeric():
    shift, msg = parse_w("3#URPD")
    cipher = CaesarCipherTM(shift=shift)
    assert cipher.decrypt(msg) == "ROMA"


def test_decrypt_with_w_letter():
    shift, msg = parse_w("D#KHOOR ZRUOG")
    cipher = CaesarCipherTM(shift=shift)
    assert cipher.decrypt(msg) == "HELLO WORLD"


def test_numeric_26_equiv_shift_0():
    shift, msg = parse_w("26#ABC")
    assert shift == 0 and msg == "ABC"
    cipher = CaesarCipherTM(shift=shift)
    assert cipher.encrypt(msg) == "ABC"  # desplazamiento 0


def test_numeric_27_equiv_shift_1():
    shift, msg = parse_w("27#ABC")
    assert shift == 1 and msg == "ABC"
    cipher = CaesarCipherTM(shift=shift)
    assert cipher.encrypt(msg) == "BCD"
