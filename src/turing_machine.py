"""
Máquina de Turing - Clase Base
Implementación de un simulador de Máquina de Turing para el proyecto PRY3-TC

Autor: Proyecto de Teoría de la Computación 2025
Fecha: 30 de octubre de 2025

Esta clase implementa una Máquina de Turing que puede:
- Cargar configuración desde archivo JSON
- Ejecutar transiciones paso a paso
- Simular el comportamiento de una MT clásica

IMPORTANTE: Esta clase solo usa operaciones básicas de MT:
- Leer símbolo de la cinta
- Escribir símbolo en la cinta
- Mover cabezal (L o R)
- Cambiar de estado
"""

import json
from typing import List, Dict, Tuple, Optional


class TuringMachine:
    """
    Simulador de Máquina de Turing
    
    Componentes de una MT: (Q, Σ, Γ, δ, q0, F)
    - Q: Conjunto de estados
    - Σ: Alfabeto de entrada
    - Γ: Alfabeto de cinta (Γ ⊇ Σ)
    - δ: Función de transición
    - q0: Estado inicial
    - F: Estados de aceptación
    """
    
    def __init__(self, 
                 states: List[str] = None,
                 input_alphabet: List[str] = None,
                 tape_alphabet: List[str] = None,
                 initial_state: str = None,
                 accept_states: List[str] = None,
                 blank_symbol: str = '_',
                 transitions: List[Dict] = None):
        """
        Inicializa la Máquina de Turing
        
        Args:
            states: Lista de estados posibles
            input_alphabet: Alfabeto de entrada (Σ)
            tape_alphabet: Alfabeto de cinta (Γ)
            initial_state: Estado inicial (q0)
            accept_states: Estados de aceptación (F)
            blank_symbol: Símbolo para espacio en blanco
            transitions: Lista de transiciones (δ)
        """
        # Componentes de la MT
        self.states = states or []
        self.input_alphabet = input_alphabet or []
        self.tape_alphabet = tape_alphabet or []
        self.initial_state = initial_state
        self.accept_states = accept_states or []
        self.blank_symbol = blank_symbol
        
        # Transiciones: diccionario para acceso rápido
        # Clave: (estado_actual, símbolo_leído)
        # Valor: (estado_siguiente, símbolo_escribir, movimiento)
        self.transitions = {}
        if transitions:
            self._load_transitions(transitions)
        
        # Estado de la simulación
        self.tape = []  # Cinta como lista de caracteres
        self.head_position = 0  # Posición del cabezal
        self.current_state = initial_state  # Estado actual
        self.step_count = 0  # Contador de pasos
        self.halted = False  # Bandera de parada
        
        # Modo debug (para imprimir cada paso)
        self.debug_mode = False
    
    def _load_transitions(self, transitions: List[Dict]):
        """
        Carga las transiciones en el diccionario interno
        
        Args:
            transitions: Lista de diccionarios con transiciones
                Formato: {
                    "current_state": "q0",
                    "read_symbol": "A",
                    "next_state": "q1",
                    "write_symbol": "B",
                    "move": "R"
                }
        """
        for trans in transitions:
            key = (trans["current_state"], trans["read_symbol"])
            value = (trans["next_state"], trans["write_symbol"], trans["move"])
            self.transitions[key] = value
    
    def load_config(self, json_file: str):
        """
        Carga la configuración de la MT desde un archivo JSON
        
        Args:
            json_file: Ruta al archivo JSON con la configuración
        
        Returns:
            True si la carga fue exitosa, False en caso contrario
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validar que el JSON tenga todos los campos necesarios
            required_fields = ['states', 'input_alphabet', 'tape_alphabet', 
                             'initial_state', 'accept_states', 'transitions']
            
            for field in required_fields:
                if field not in config:
                    print(f"Error: El archivo JSON no contiene el campo '{field}'")
                    return False
            
            # Asignar valores
            self.states = config['states']
            self.input_alphabet = config['input_alphabet']
            self.tape_alphabet = config['tape_alphabet']
            self.initial_state = config['initial_state']
            self.accept_states = config['accept_states']
            self.blank_symbol = config.get('blank_symbol', '_')
            
            # Cargar transiciones
            self._load_transitions(config['transitions'])
            
            # Resetear estado de simulación
            self.current_state = self.initial_state
            self.step_count = 0
            self.halted = False
            
            return True
            
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo '{json_file}'")
            return False
        except json.JSONDecodeError:
            print(f"Error: El archivo '{json_file}' no es un JSON válido")
            return False
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            return False
    
    def initialize_tape(self, input_string: str):
        """
        Inicializa la cinta con el string de entrada
        
        Args:
            input_string: String de entrada para la MT
        """
        # Convertir string a lista de caracteres
        self.tape = list(input_string)
        
        # Agregar algunos blancos al final para tener espacio
        for _ in range(20):
            self.tape.append(self.blank_symbol)
        
        # Posicionar cabezal al inicio
        self.head_position = 0
        
        # Resetear estado
        self.current_state = self.initial_state
        self.step_count = 0
        self.halted = False
    
    def get_current_symbol(self) -> str:
        """
        Obtiene el símbolo en la posición actual del cabezal
        
        Returns:
            El símbolo en la posición actual
        """
        # Expandir la cinta si el cabezal está fuera de rango
        while self.head_position >= len(self.tape):
            self.tape.append(self.blank_symbol)
        
        # Manejar posiciones negativas (por si acaso)
        if self.head_position < 0:
            return self.blank_symbol
        
        return self.tape[self.head_position]
    
    def write_symbol(self, symbol: str):
        """
        Escribe un símbolo en la posición actual del cabezal
        
        Args:
            symbol: Símbolo a escribir
        """
        # Expandir la cinta si es necesario
        while self.head_position >= len(self.tape):
            self.tape.append(self.blank_symbol)
        
        # Escribir el símbolo
        if self.head_position >= 0:
            self.tape[self.head_position] = symbol
    
    def move_head(self, direction: str):
        """
        Mueve el cabezal en la dirección especificada
        
        Args:
            direction: 'L' para izquierda, 'R' para derecha, 'N' para no mover
        """
        if direction == 'R':
            self.head_position += 1
        elif direction == 'L':
            self.head_position -= 1
            # No permitir posiciones negativas
            if self.head_position < 0:
                self.head_position = 0
        # 'N' no hace nada (no mover)
    
    def find_transition(self, state: str, symbol: str) -> Optional[Tuple[str, str, str]]:
        """
        Busca una transición aplicable para el estado y símbolo dados
        
        Args:
            state: Estado actual
            symbol: Símbolo leído
        
        Returns:
            Tupla (next_state, write_symbol, move) si existe transición,
            None si no hay transición aplicable
        """
        key = (state, symbol)
        return self.transitions.get(key, None)
    
    def step(self) -> bool:
        """
        Ejecuta un paso de la máquina de Turing
        
        Returns:
            True si se ejecutó una transición exitosamente,
            False si no hay transición aplicable (rechazo)
        """
        if self.halted:
            return False
        
        # Leer símbolo actual
        current_symbol = self.get_current_symbol()
        
        # Buscar transición aplicable
        transition = self.find_transition(self.current_state, current_symbol)
        
        if transition is None:
            # No hay transición aplicable
            if self.debug_mode:
                print(f"No hay transición para ({self.current_state}, '{current_symbol}')")
            self.halted = True
            return False
        
        # Desempaquetar transición
        next_state, write_symbol, move = transition
        
        # Mostrar paso en modo debug
        if self.debug_mode:
            print(f"Paso {self.step_count}: ({self.current_state}, '{current_symbol}') → "
                  f"({next_state}, '{write_symbol}', {move})")
        
        # Ejecutar transición
        self.write_symbol(write_symbol)
        self.current_state = next_state
        self.move_head(move)
        
        # Incrementar contador
        self.step_count += 1
        
        return True
    
    def is_accepting_state(self) -> bool:
        """
        Verifica si el estado actual es de aceptación
        
        Returns:
            True si está en estado de aceptación, False en caso contrario
        """
        return self.current_state in self.accept_states
    
    def run(self, input_string: str, max_steps: int = 100000) -> str:
        """
        Ejecuta la máquina de Turing hasta aceptar, rechazar o exceder max_steps
        
        Args:
            input_string: String de entrada
            max_steps: Número máximo de pasos (prevenir bucles infinitos)
        
        Returns:
            La cinta resultante como string
        """
        # Inicializar cinta
        self.initialize_tape(input_string)
        
        if self.debug_mode:
            print(f"\n=== Iniciando ejecución ===")
            print(f"Entrada: {input_string}")
            print(f"Estado inicial: {self.initial_state}")
            self.display_tape()
            print()
        
        # Ejecutar hasta aceptar, rechazar o exceder max_steps
        while not self.halted and self.step_count < max_steps:
            # Ejecutar un paso
            if not self.step():
                # No hay transición aplicable (rechazo)
                break
            
            # Verificar si está en estado de aceptación
            if self.is_accepting_state():
                self.halted = True
                break
            
            # Mostrar estado en debug
            if self.debug_mode and self.step_count % 10 == 0:
                self.display_tape()
        
        # Verificar si excedió el límite
        if self.step_count >= max_steps:
            print(f"ADVERTENCIA: Se excedió el límite de {max_steps} pasos")
        
        if self.debug_mode:
            print(f"\n=== Ejecución finalizada ===")
            print(f"Pasos ejecutados: {self.step_count}")
            print(f"Estado final: {self.current_state}")
            print(f"Aceptado: {self.is_accepting_state()}")
            self.display_tape()
            print()
        
        # Retornar la cinta (eliminar blancos al final)
        result = ''.join(self.tape).rstrip(self.blank_symbol)
        return result
    
    def display_tape(self):
        """
        Muestra el estado actual de la cinta y el cabezal
        """
        # Mostrar la cinta (solo hasta donde hay contenido)
        tape_display = ''.join(self.tape[:max(self.head_position + 10, 20)])
        print(f"Cinta: [{tape_display}]")
        
        # Mostrar posición del cabezal
        spaces = ' ' * (self.head_position + 8)  # +8 por "Cinta: ["
        print(f"{spaces}^")
        print(f"Estado: {self.current_state}, Posición: {self.head_position}")
    
    def display_configuration(self):
        """
        Muestra la configuración completa de la MT
        """
        print("\n=== Configuración de la Máquina de Turing ===")
        print(f"Estados (Q): {self.states}")
        print(f"Alfabeto de entrada (Σ): {self.input_alphabet}")
        print(f"Alfabeto de cinta (Γ): {self.tape_alphabet}")
        print(f"Estado inicial (q0): {self.initial_state}")
        print(f"Estados de aceptación (F): {self.accept_states}")
        print(f"Símbolo blanco: '{self.blank_symbol}'")
        print(f"Número de transiciones: {len(self.transitions)}")
        print("=" * 47)
    
    def enable_debug_mode(self):
        """Activa el modo debug para ver cada paso de la ejecución"""
        self.debug_mode = True
    
    def disable_debug_mode(self):
        """Desactiva el modo debug"""
        self.debug_mode = False


# Ejemplo de uso básico
if __name__ == "__main__":
    print("Simulador de Máquina de Turing")
    print("Clase base implementada correctamente ✓")
    print("\nPara usar esta clase:")
    print("1. Crear una instancia: tm = TuringMachine()")
    print("2. Cargar configuración: tm.load_config('archivo.json')")
    print("3. Ejecutar: resultado = tm.run('entrada')")
