import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from turing_simulator import TuringMachine  # type: ignore


def cfg(name: str) -> str:
    return os.path.join(ROOT, 'config', name)


def test_test_simple_replaces_A_with_B():
    tm = TuringMachine(cfg('test_simple.json'))
    out = tm.run('AAA')
    assert out == 'BBB'
    assert tm.current_state in tm.accept_states


def test_add_simple():
    # Entrada: ||+||| => |||||
    tm = TuringMachine(cfg('add_simple.json'))
    out = tm.run('||+|||')
    # Contar barras resultantes
    assert out.count('|') == 5
    assert '+' not in out


def test_blank_input():
    tm = TuringMachine(cfg('test_simple.json'))
    out = tm.run('')
    # Máquina test_simple al recibir blanco debería inmediatamente aceptar con cinta vacía
    assert out == ''


def test_max_steps_guard():
    tm = TuringMachine(cfg('test_simple.json'))
    out = tm.run('A' * 3, max_steps=2)  # Forzar corte temprano
    # Con solo 2 pasos no habrá procesado toda la cadena
    assert out.startswith('B')  # Al menos primer símbolo cambiado
    assert tm.steps_executed == 2
