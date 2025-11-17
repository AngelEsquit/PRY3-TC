"""Pruebas para las máquinas autónomas CaesarEncryptTM y CaesarDecryptTM"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from caesar_encrypt_tm import CaesarEncryptTM
from caesar_decrypt_tm import CaesarDecryptTM


def test_basic_encrypt_machine():
    enc = CaesarEncryptTM(shift=3)
    assert enc.encrypt("HOLA") == "KROD"


def test_basic_decrypt_machine():
    dec = CaesarDecryptTM(shift=3)
    assert dec.decrypt("KROD") == "HOLA"


def test_roundtrip_separate():
    enc = CaesarEncryptTM(shift=10)
    dec = CaesarDecryptTM(shift=10)
    original = "HELLO WORLD"
    cipher = enc.encrypt(original)
    plain = dec.decrypt(cipher)
    assert plain == original


def test_shift_26_equiv_zero_encrypt():
    enc = CaesarEncryptTM(shift=26)
    assert enc.encrypt("ABC") == "ABC"


def test_shift_27_equiv_one_encrypt():
    enc = CaesarEncryptTM(shift=27)
    assert enc.encrypt("ABC") == "BCD"


def test_non_alpha_preserved():
    enc = CaesarEncryptTM(shift=5)
    dec = CaesarDecryptTM(shift=5)
    txt = "HOLA, MUNDO! 123"
    cipher = enc.encrypt(txt)
    plain = dec.decrypt(cipher)
    assert plain == txt
