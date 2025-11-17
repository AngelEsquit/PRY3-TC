"""Pruebas del flujo w=clave#mensaje usando solo MTs para la clave.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from caesar_encrypt_tm import CaesarEncryptTM
from caesar_decrypt_tm import CaesarDecryptTM

def test_example_encrypt_numeric():
    enc = CaesarEncryptTM(debug=False)
    out = enc.encrypt_w("3#ROMA NO FUE CONSTRUIDA EN UN DIA.")
    assert out == "URPD QR IXH FRQVWUXLGD HQ XQ GLD."

def test_example_encrypt_letter():
    enc = CaesarEncryptTM(debug=False)
    out = enc.encrypt_w("D#ROMA NO FUE CONSTRUIDA EN UN DIA.")
    assert out == "URPD QR IXH FRQVWUXLGD HQ XQ GLD."

def test_example_decrypt_numeric():
    dec = CaesarDecryptTM(debug=False)
    out = dec.decrypt_w("3#URPD QR IXH FRQVWUXLGD HQ XQ GLD.")
    assert out == "ROMA NO FUE CONSTRUIDA EN UN DIA."

def test_example_decrypt_letter():
    dec = CaesarDecryptTM(debug=False)
    out = dec.decrypt_w("D#URPD QR IXH FRQVWUXLGD HQ XQ GLD.")
    assert out == "ROMA NO FUE CONSTRUIDA EN UN DIA."