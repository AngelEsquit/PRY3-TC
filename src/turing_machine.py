"""
Simulador Universal de Máquinas de Turing.

Soporta:
- MT de una cinta (formato clásico) con transiciones: (estado, símbolo) -> (estado', símbolo', movimiento)
- MT multi-cinta (num_tapes > 1) con transiciones: (estado, [símbolos]) -> (estado', [símbolos'], [movimientos])

Formato JSON esperado mínimo (una cinta):
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

Formato JSON multi-cinta (ejemplo 2 cintas):
{
    "num_tapes": 2,
    "states": [...],
    "input_alphabet": [...],
    "tape_alphabet": [...],
    "initial_state": "q0",
    "accept_states": ["q_fin"],
    "blank_symbol": "_",
    "transitions": [
        {"current_state": "q0", "read_symbols": ["A","_"], "next_state": "q1", "write_symbols": ["A","A"], "movements": ["R","R"]}
    ]
}

NOTA: El simulador es agnóstico al propósito de la máquina (cifrado César, aritmética, etc.).
Toda la lógica reside en el JSON.
"""

import json
from typing import List, Dict, Tuple, Optional, Any


class TuringMachine:
    """Simulador Universal de MT (una o múltiples cintas)."""
    
    def __init__(self,
                 states: Optional[List[str]] = None,
                 input_alphabet: Optional[List[str]] = None,
                 tape_alphabet: Optional[List[str]] = None,
                 initial_state: Optional[str] = None,
                 accept_states: Optional[List[str]] = None,
                 blank_symbol: str = '_',
                 transitions: Optional[List[Dict[str, Any]]] = None,
                 num_tapes: int = 1):
        # Definición
        self.states = states or []
        self.input_alphabet = input_alphabet or []
        self.tape_alphabet = tape_alphabet or []
        self.initial_state = initial_state
        self.accept_states = accept_states or []
        self.blank_symbol = blank_symbol
        self.num_tapes = num_tapes
        # Transiciones internas:
        # Una cinta: key = (state, symbol) -> (next_state, write_symbol, move)
        # Multi-cinta: key = (state, tuple(read_symbols)) -> (next_state, tuple(write_symbols), tuple(movements))
        self.transitions: Dict[Any, Any] = {}
        if transitions:
            self._load_transitions(transitions)
        # Estado ejecución
        self.tapes: List[List[str]] = []
        self.head_positions: List[int] = []
        self.current_state: Optional[str] = initial_state
        self.step_count = 0
        self.halted = False
        self.debug_mode = False
    
    def _load_transitions(self, transitions: List[Dict[str, Any]]):
        for trans in transitions:
            state = trans["current_state"]
            # Multi-cinta
            if "read_symbols" in trans:
                read = tuple(trans["read_symbols"])
                write = tuple(trans["write_symbols"])
                moves = tuple(trans["movements"])
                self.transitions[(state, read)] = (trans["next_state"], write, moves)
            else:
                key = (state, trans["read_symbol"])
                self.transitions[key] = (trans["next_state"], trans["write_symbol"], trans["move"])
    
    def load_config(self, json_file: str) -> bool:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            required = ["states", "input_alphabet", "tape_alphabet", "initial_state", "accept_states", "transitions"]
            for field in required:
                if field not in config:
                    print(f"Error: falta campo '{field}' en {json_file}")
                    return False
            self.states = config["states"]
            self.input_alphabet = config["input_alphabet"]
            self.tape_alphabet = config["tape_alphabet"]
            self.initial_state = config["initial_state"]
            self.accept_states = config["accept_states"]
            self.blank_symbol = config.get("blank_symbol", "_")
            self.num_tapes = config.get("num_tapes", 1)
            self.transitions = {}
            self._load_transitions(config["transitions"])
            self.current_state = self.initial_state
            self.step_count = 0
            self.halted = False
            return True
        except Exception as e:
            print(f"Error al cargar configuración '{json_file}': {e}")
            return False
    
    def _init_tapes(self, input_string: str):
        self.tapes = []
        if self.num_tapes == 1:
            primary = list(input_string)
            primary.extend([self.blank_symbol] * 50)
            self.tapes.append(primary)
        else:
            # Primera cinta con entrada, resto en blanco
            first = list(input_string)
            first.extend([self.blank_symbol] * 50)
            self.tapes.append(first)
            for _ in range(self.num_tapes - 1):
                blank_tape = [self.blank_symbol] * (len(first))
                self.tapes.append(blank_tape)
        self.head_positions = [0] * self.num_tapes
        self.current_state = self.initial_state
        self.step_count = 0
        self.halted = False
    
    def _ensure_index(self, tape_idx: int):
        while self.head_positions[tape_idx] >= len(self.tapes[tape_idx]):
            self.tapes[tape_idx].append(self.blank_symbol)

    def _read_symbols(self) -> Tuple[str, ...]:
        symbols = []
        for i in range(self.num_tapes):
            self._ensure_index(i)
            pos = self.head_positions[i]
            if pos < 0:
                symbols.append(self.blank_symbol)
            else:
                symbols.append(self.tapes[i][pos])
        return tuple(symbols)
    
    def _write_symbols(self, write: Tuple[str, ...]):
        for i, sym in enumerate(write):
            self._ensure_index(i)
            if self.head_positions[i] >= 0:
                self.tapes[i][self.head_positions[i]] = sym
    
    def _apply_movements(self, movements: Tuple[str, ...]):
        for i, mv in enumerate(movements):
            if mv == 'R':
                self.head_positions[i] += 1
            elif mv == 'L':
                self.head_positions[i] -= 1
                if self.head_positions[i] < 0:
                    self.head_positions[i] = 0
            # 'N' no mueve
    
    def _find_transition(self, state: str, symbols: Tuple[str, ...]):
        if self.num_tapes == 1:
            key = (state, symbols[0])
            return self.transitions.get(key)
        else:
            key = (state, symbols)
            return self.transitions.get(key)
    
    def step(self) -> bool:
        if self.halted:
            return False
        symbols = self._read_symbols()
        transition = self._find_transition(self.current_state, symbols)
        if transition is None:
            if self.debug_mode:
                print(f"Sin transición para estado={self.current_state} símbolos={symbols}")
            self.halted = True
            return False
        next_state, write, moves = transition
        if self.num_tapes == 1:
            # Normalizar tipos
            write = (write,)
            moves = (moves,)
        if self.debug_mode:
            print(f"Paso {self.step_count}: estado={self.current_state} símbolos={symbols} -> {next_state}, escribir={write}, movimientos={moves}")
        self._write_symbols(write)
        self.current_state = next_state
        self._apply_movements(moves)
        self.step_count += 1
        return True
    
    def is_accepting_state(self) -> bool:
        return self.current_state in self.accept_states
    
    def run(self, input_string: str, max_steps: int = 200000) -> str:
        self._init_tapes(input_string)
        if self.debug_mode:
            print("=== Inicio ejecución MT ===")
            print(f"Cintas: {self.num_tapes}, Entrada: '{input_string}'")
        while not self.halted and self.step_count < max_steps:
            progressed = self.step()
            if not progressed:
                break
            if self.is_accepting_state():
                self.halted = True
                break
            if self.debug_mode and self.step_count % 25 == 0:
                self.display_tape()
        if self.step_count >= max_steps:
            print(f"ADVERTENCIA: límite de pasos {max_steps} alcanzado")
        if self.debug_mode:
            print("=== Fin ejecución ===")
            print(f"Pasos: {self.step_count} | Estado final: {self.current_state} | Aceptado: {self.is_accepting_state()}")
            self.display_tape()
        # Resultado principal (cinta 0)
        principal = ''.join(self.tapes[0]).rstrip(self.blank_symbol)
        return principal
    
    def display_tape(self):
        for i in range(self.num_tapes):
            span = max(self.head_positions[i] + 10, 30)
            snippet = ''.join(self.tapes[i][:span])
            print(f"Cinta {i}: [{snippet}]")
            caret_spaces = ' ' * (self.head_positions[i] + 9)
            print(f"{caret_spaces}^ (pos {self.head_positions[i]})")
        print(f"Estado: {self.current_state} | Paso: {self.step_count}")
    
    def display_configuration(self):
        print("\n=== Configuración MT ===")
        print(f"Estados: {len(self.states)} | Inicial: {self.initial_state} | Aceptación: {self.accept_states}")
        print(f"Alfabeto entrada: {self.input_alphabet}")
        print(f"Alfabeto cinta: {self.tape_alphabet}")
        print(f"Símbolo blanco: {self.blank_symbol} | Cintas: {self.num_tapes}")
        print(f"Transiciones: {len(self.transitions)}")
        print("="*48)
    
    def enable_debug_mode(self):
        """Activa el modo debug para ver cada paso de la ejecución"""
        self.debug_mode = True
    
    def disable_debug_mode(self):
        """Desactiva el modo debug"""
        self.debug_mode = False


# Uso rápido de prueba
if __name__ == "__main__":
    import os
    base = os.path.join(os.path.dirname(__file__), '..', 'config', 'test_simple.json')
    tm = TuringMachine()
    if tm.load_config(base):
        tm.enable_debug_mode()
        out = tm.run('AAA')
        print("Salida:", out)
