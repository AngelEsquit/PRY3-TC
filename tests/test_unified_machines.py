"""Pruebas básicas sobre las MT unificadas generadas.
Estas pruebas verificarán si la máquina unificada produce el resultado esperado
para el ejemplo del enunciado. Se espera que inicialmente falle en algunos
casos (especialmente clave numérica), lo cual servirá para iterar.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from turing_machine import TuringMachine

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')

EXAMPLE_PLAIN = "ROMA NO FUE CONSTRUIDA EN UN DIA."
EXAMPLE_ENCRYPTED = "URPD QR IXH FRQVWUXLGD HQ XQ GLD."


def run_unified_encrypt(w: str):
    tm = TuringMachine()
    assert tm.load_config(os.path.join(CONFIG_DIR, 'caesar_encrypt_full.json'))
    return tm.run(w, max_steps=20000)


def run_unified_decrypt(w: str):
    tm = TuringMachine()
    assert tm.load_config(os.path.join(CONFIG_DIR, 'caesar_decrypt_full.json'))
    return tm.run(w, max_steps=20000)


def test_unified_encrypt_letter_key():
    # Clave letra D (shift 3)
    result = run_unified_encrypt("D#" + EXAMPLE_PLAIN)
    # Se espera contenga el texto cifrado; si no, se registrará diferencia.
    assert EXAMPLE_ENCRYPTED in result, f"Salida no contiene cifrado esperado.\nSalida:\n{result}"  # leniency: searching substring


def test_unified_encrypt_numeric_key():
    result = run_unified_encrypt("3#" + EXAMPLE_PLAIN)
    assert EXAMPLE_ENCRYPTED in result, f"(num) No contiene cifrado esperado.\nSalida:\n{result}"


def test_unified_decrypt_letter_key():
    result = run_unified_decrypt("D#" + EXAMPLE_ENCRYPTED)
    assert EXAMPLE_PLAIN in result, f"Decripción letra falló.\nSalida:\n{result}"


def test_unified_decrypt_numeric_key():
    result = run_unified_decrypt("3#" + EXAMPLE_ENCRYPTED)
    assert EXAMPLE_PLAIN in result, f"Decripción numérica falló.\nSalida:\n{result}"