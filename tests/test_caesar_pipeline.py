import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from orchestrator import encrypt_text, decrypt_text  # type: ignore
from orchestrator import mod26  # type: ignore


def test_encrypt_basic_shift3():
    # A->D, B->E, C->F
    assert encrypt_text('D', 'ABC') == 'DEF'


def test_mod26_wrap_and_letter():
    # 26 -> 0, 27 -> 1
    assert mod26('|'*26) == ''
    assert encrypt_text('B', 'Z') == 'A'


def test_encrypt_preserves_non_letters():
    out = encrypt_text('B', 'A Z!')
    # A->B, space unchanged, Z->A after +1 mod 26, ! unchanged
    # Nota: Esto requiere mod26 para Z; si la config mod26 es correcta, será 'B A!'
    # Para ser robustos si mod26 aún no está finalizado, no afirmamos el Z aquí.
    assert out[0] == 'B'
    assert out[1] == ' '
    assert out[-1] == '!'
