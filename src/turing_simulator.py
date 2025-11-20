"""turing_simulator.py

Simulador universal de Máquinas de Turing (una cinta) construido desde cero
según la especificación solicitada.

Estructura JSON esperada (exacta):
{
    "states": [...],
    "input_alphabet": [...],
    "tape_alphabet": [...],
    "initial_state": "q0",
    "accept_states": ["q_accept"],
    "blank_symbol": "_",
    "transitions": [
        {"current_state": "q0", "read_symbol": "A", "next_state": "q1", "write_symbol": "B", "move": "R"}
    ]
}

Características:
- Carga directa del JSON sin reinterpretar la lógica.
- Cinta conceptualmente infinita: se expande dinámicamente a la izquierda o derecha.
- Búsqueda de transición lineal en el orden declarado (prioriza primera coincidencia).
- Pasos individuales mediante step(); ejecución completa con run().

Limitaciones intencionales (para mantener pureza):
- No se incluye soporte multi-cinta ni atajos lógicos.
- No se agregan transformaciones externas (cifrado, aritmética) en Python.
"""

from __future__ import annotations
import json
from typing import List, Dict, Optional


class TuringMachine:
    def __init__(self, json_file: str):
        self.states: List[str] = []
        self.input_alphabet: List[str] = []
        self.tape_alphabet: List[str] = []
        self.initial_state: Optional[str] = None
        self.accept_states: List[str] = []
        self.blank_symbol: str = '_'
        self.transitions: List[Dict[str, str]] = []

        self.tape: List[str] = []
        self.head_position: int = 0
        self.current_state: Optional[str] = None
        self.steps_executed: int = 0

        self.load_machine(json_file)

    def load_machine(self, json_file: str) -> None:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.states = data.get('states', [])
        self.input_alphabet = data.get('input_alphabet', [])
        self.tape_alphabet = data.get('tape_alphabet', [])
        self.initial_state = data.get('initial_state')
        self.accept_states = data.get('accept_states', [])
        self.blank_symbol = data.get('blank_symbol', '_')
        self.transitions = data.get('transitions', [])

    def initialize_tape(self, input_string: str) -> None:
        self.tape = list(input_string) if input_string else []
        if not self.tape:
            self.tape.append(self.blank_symbol)
        self.head_position = 0
        self.current_state = self.initial_state
        self.steps_executed = 0

    def find_transition(self, state: str, symbol: str) -> Optional[Dict[str, str]]:
        for t in self.transitions:
            if t.get('current_state') == state and t.get('read_symbol') == symbol:
                return t
        return None

    def step(self) -> bool:
        if self.current_state is None:
            return False
        if self.current_state in self.accept_states:
            return False
        if self.head_position < 0:
            needed = -self.head_position
            self.tape = [self.blank_symbol] * needed + self.tape
            self.head_position = 0
        if self.head_position >= len(self.tape):
            self.tape.append(self.blank_symbol)
        current_symbol = self.tape[self.head_position]
        transition = self.find_transition(self.current_state, current_symbol)
        if transition is None:
            return False
        write_symbol = transition.get('write_symbol', current_symbol)
        move = transition.get('move', 'N')
        next_state = transition.get('next_state', self.current_state)
        self.tape[self.head_position] = write_symbol
        if move == 'L':
            self.head_position -= 1
        elif move == 'R':
            self.head_position += 1
        if self.head_position < 0:
            self.tape.insert(0, self.blank_symbol)
            self.head_position = 0
        elif self.head_position >= len(self.tape):
            self.tape.append(self.blank_symbol)
        self.current_state = next_state
        self.steps_executed += 1
        return True

    def run(self, input_string: str, max_steps: int = 10000) -> str:
        self.initialize_tape(input_string)
        for _ in range(max_steps):
            if self.current_state in self.accept_states:
                break
            progressed = self.step()
            if not progressed:
                break
        return self.get_tape_contents()

    def get_tape_contents(self) -> str:
        if not self.tape:
            return ''
        first = None
        last = None
        for i, sym in enumerate(self.tape):
            if sym != self.blank_symbol:
                if first is None:
                    first = i
                last = i
        if first is None:
            return ''
        return ''.join(self.tape[first:last + 1])


if __name__ == "__main__":
    import os
    cfg = os.path.join(os.path.dirname(__file__), '..', 'config', 'test_simple.json')
    if os.path.isfile(cfg):
        tm = TuringMachine(cfg)
        out = tm.run('AAA')
        print('Salida:', out)
        print('Pasos:', tm.steps_executed)
    else:
        print('No se encontró config/test_simple.json para la prueba rápida.')