"""
Generador de configuraciones JSON para Máquinas de Turing
Este script genera configuraciones complejas automáticamente
"""

import json
import os

def generate_letter_to_number_config():
    """
    Genera la configuración de MT para convertir letras a números (marcas).
    A=0 (sin marcas), B=1 (| marca), C=2 (|| marcas), ..., Z=25
    """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    config = {
        "description": "Máquina de Turing para convertir LETRA a NÚMERO (en marcas)",
        "purpose": "Entrada: letra (A-Z), Salida: posición en marcas (A=0, B=1, ...)",
        "example": "H -> ||||||| (7 marcas)",
        "note": "Generado automáticamente",
        
        "states": ["q0", "q_write", "q_accept"],
        "input_alphabet": list(alphabet),
        "tape_alphabet": list(alphabet) + ["|", "_"],
        "initial_state": "q0",
        "accept_states": ["q_accept"],
        "blank_symbol": "_",
        "transitions": []
    }
    
    # Generar transiciones para cada letra
    for i, letter in enumerate(alphabet):
        if i == 0:  # A = 0, no escribir marcas
            config["transitions"].append({
                "comment": f"{letter}=0: borrar letra, no escribir marcas",
                "current_state": "q0",
                "read_symbol": letter,
                "next_state": "q_accept",
                "write_symbol": "_",
                "move": "N"
            })
        else:  # B=1, C=2, etc.
            # Primer transición: borrar letra y mover a la derecha
            config["transitions"].append({
                "comment": f"{letter}={i}: borrar letra y escribir {i} marca(s)",
                "current_state": "q0",
                "read_symbol": letter,
                "next_state": f"q_write_{letter}_1",
                "write_symbol": "_",
                "move": "R"
            })
            
            # Agregar estados intermedios a la lista de estados
            for j in range(1, i + 1):
                state_name = f"q_write_{letter}_{j}"
                if state_name not in config["states"]:
                    config["states"].append(state_name)
            
            # Escribir marcas
            for j in range(1, i + 1):
                current_state = f"q_write_{letter}_{j}"
                if j < i:  # No es la última marca
                    next_state = f"q_write_{letter}_{j+1}"
                    move = "R"
                else:  # Última marca
                    next_state = "q_accept"
                    move = "N"
                
                config["transitions"].append({
                    "comment": f"{letter}: escribir marca {j}/{i}",
                    "current_state": current_state,
                    "read_symbol": "_",
                    "next_state": next_state,
                    "write_symbol": "|",
                    "move": move
                })
    
    return config


def generate_number_to_letter_config():
    """
    Genera la configuración de MT para convertir números (marcas) a letras.
    0 marcas -> A, 1 marca -> B, 2 marcas -> C, ..., 25 marcas -> Z
    """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    config = {
        "description": "Máquina de Turing para convertir NÚMERO (marcas) a LETRA",
        "purpose": "Entrada: n marcas, Salida: letra correspondiente (0=A, 1=B, ...)",
        "example": "|||||||  (7 marcas) -> H",
        "note": "Generado automáticamente",
        
        "states": ["q0"] + [f"q_{i}" for i in range(1, 27)] + ["q_back", "q_accept"],
        "input_alphabet": ["|"],
        "tape_alphabet": ["|", "_"] + list(alphabet),
        "initial_state": "q0",
        "accept_states": ["q_accept"],
        "blank_symbol": "_",
        "transitions": []
    }
    
    # Estado inicial: si no hay marcas, escribir A
    config["transitions"].append({
        "comment": "0 marcas = A",
        "current_state": "q0",
        "read_symbol": "_",
        "next_state": "q_accept",
        "write_symbol": "A",
        "move": "N"
    })
    
    # Primera marca -> estado q_1
    config["transitions"].append({
        "comment": "Primera marca",
        "current_state": "q0",
        "read_symbol": "|",
        "next_state": "q_1",
        "write_symbol": "_",
        "move": "R"
    })
    
    # Contar marcas del 1 al 25
    for i in range(1, 26):
        # Leer siguiente marca
        config["transitions"].append({
            "comment": f"Marca {i}: leer siguiente",
            "current_state": f"q_{i}",
            "read_symbol": "|",
            "next_state": f"q_{i+1}",
            "write_symbol": "_",
            "move": "R"
        })
        
        # Si encontramos blanco, tenemos i marcas -> letra alphabet[i]
        config["transitions"].append({
            "comment": f"{i} marca(s) = {alphabet[i]}",
            "current_state": f"q_{i}",
            "read_symbol": "_",
            "next_state": "q_back",
            "write_symbol": alphabet[i],
            "move": "L"
        })
    
    # Estado 26: escribir Z
    config["transitions"].append({
        "comment": "25 marcas = Z (continuar si hay más)",
        "current_state": "q_26",
        "read_symbol": "|",
        "next_state": "q_26",
        "write_symbol": "_",
        "move": "R"
    })
    
    config["transitions"].append({
        "comment": "25+ marcas = Z",
        "current_state": "q_26",
        "read_symbol": "_",
        "next_state": "q_back",
        "write_symbol": "Z",
        "move": "L"
    })
    
    # Retroceder al inicio
    config["transitions"].append({
        "comment": "Retroceder sobre blancos",
        "current_state": "q_back",
        "read_symbol": "_",
        "next_state": "q_back",
        "write_symbol": "_",
        "move": "L"
    })
    
    config["transitions"].append({
        "comment": "Llegar al inicio y aceptar",
        "current_state": "q_back",
        "read_symbol": "_",
        "next_state": "q_accept",
        "write_symbol": "_",
        "move": "R"
    })
    
    return config


def save_config(config, filename):
    """Guarda la configuración en un archivo JSON."""
    filepath = os.path.join('config', filename)
    os.makedirs('config', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Generado: {filepath}")
    print(f"  Estados: {len(config['states'])}")
    print(f"  Transiciones: {len(config['transitions'])}")


if __name__ == "__main__":
    print("=" * 60)
    print("Generador de Configuraciones de MT")
    print("=" * 60)
    
    print("\nGenerando configuración: Letra -> Número")
    letter_to_num = generate_letter_to_number_config()
    save_config(letter_to_num, "letter_to_number.json")
    
    print("\nGenerando configuración: Número -> Letra")
    num_to_letter = generate_number_to_letter_config()
    save_config(num_to_letter, "number_to_letter.json")
    
    print("\n" + "=" * 60)
    print("✓ Configuraciones generadas exitosamente")
    print("=" * 60)
