"""Pruebas básicas sobre las MT unificadas generadas.
Estas pruebas verificarán si la máquina unificada produce el resultado esperado
para el ejemplo del enunciado. Se espera que inicialmente falle en algunos
casos (especialmente clave numérica), lo cual servirá para iterar.
"""
import os, sys, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Unified machine JSONs fueron retirados del entregable modular.
# Estas pruebas se marcan como skip para no afectar la suite.
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
    pytest.skip("Máquina unificada retirada; prueba desactivada.")


def test_unified_encrypt_numeric_key():
    pytest.skip("Máquina unificada retirada; prueba desactivada.")


def test_unified_decrypt_letter_key():
    pytest.skip("Máquina unificada retirada; prueba desactivada.")


def test_unified_decrypt_numeric_key():
    pytest.skip("Máquina unificada retirada; prueba desactivada.")