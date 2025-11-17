"""Builder para Máquinas de Turing UNIFICADAS (encripción y decripción)

Este script genera dos archivos JSON:
- config/caesar_encrypt_full.json
- config/caesar_decrypt_full.json

La idea: integrar en una sola MT los pasos modularizados:
  1. Leer clave (primera parte antes de '#'): letra A-Z o número 1..27
  2. Convertir clave a marcas (shift) mediante estados integrados
  3. Procesar cada letra del mensaje:
       letra -> marcas -> suma shift -> mod 26 -> marcas -> letra cifrada
     Carácteres no alfabéticos se copian sin cambio.

Limitaciones / Simplificaciones:
- Se asume entrada totalmente en MAYÚSCULAS para letras (el caso ya manejado externamente).
- Para reducir tamaño extremo, se reutilizan patrones y se generan estados con prefijos.
- El bucle de procesamiento de letras aplica el pipeline por cada símbolo.
- El módulo 26 y conversiones usan la misma lógica que los JSON originales pero con nombres de estados prefijados.
- Esta MT unificada será grande; el objetivo principal es demostrar la construcción.

Uso:
  python tools/build_unified_machines.py

Esto dejará los archivos en config/.

Nota: El simulador actual soporta un solo diccionario de transiciones plano; aquí integramos todo en ese esquema.
"""
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / 'config'

# Archivos modulares existentes (se usan como fuente de transiciones que se renombrarán)
MODULAR_FILES = {
    'letter_to_number': 'letter_to_number.json',
    'number_to_letter': 'number_to_letter.json',
    'add': 'add_simple.json',
    'mod26': 'mod26_full.json'
}

def load_json(name):
    path = CONFIG_DIR / name
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def prefix_transitions(data, prefix):
    """Renombra estados en transitions, states, initial_state, accept_states con un prefijo."""
    mapping = {s: f"{prefix}_{s}" for s in data['states']}
    def map_state(s):
        return mapping.get(s, s)
    transitions = []
    for t in data['transitions']:
        transitions.append({
            'current_state': map_state(t['current_state']),
            'read_symbol': t['read_symbol'],
            'next_state': map_state(t['next_state']),
            'write_symbol': t['write_symbol'],
            'move': t['move']
        })
    return {
        'states': [mapping[s] for s in data['states']],
        'initial_state': map_state(data['initial_state']),
        'accept_states': [map_state(s) for s in data['accept_states']],
        'transitions': transitions,
        'tape_alphabet': data['tape_alphabet'],
        'input_alphabet': data['input_alphabet'],
        'blank_symbol': data.get('blank_symbol', '_')
    }

def build_unified(encrypt=True):
    # Cargar componentes
    letter_to_number = load_json(MODULAR_FILES['letter_to_number'])
    number_to_letter = load_json(MODULAR_FILES['number_to_letter'])
    add_simple = load_json(MODULAR_FILES['add'])
    mod26_full = load_json(MODULAR_FILES['mod26'])

    # Prefijar
    l2n = prefix_transitions(letter_to_number, 'L2N')
    n2l = prefix_transitions(number_to_letter, 'N2L')
    addp = prefix_transitions(add_simple, 'ADD')
    modp = prefix_transitions(mod26_full, 'MOD')

    # Unificar alfabetos
    tape_alphabet = sorted(set(l2n['tape_alphabet']) | set(n2l['tape_alphabet']) | set(addp['tape_alphabet']) | set(modp['tape_alphabet']) | set(['#','+','-']))
    input_alphabet = sorted(set(l2n['input_alphabet']) | set(n2l['input_alphabet']) | set(addp['input_alphabet']) | set(modp['input_alphabet']) | set(['#']))

    states = []
    transitions = []

    # Estados de control principales
    control_states = [
        'q_start',        # Inicio
        'q_read_key',     # Leer clave hasta '#'
        'q_key_done',     # Clave convertida a marcas (shift almacenado en región izquierda)
        'q_read_char',    # Leer siguiente carácter del mensaje
        'q_copy_nonalpha',# Copiar símbolos no alfabéticos
        'q_prepare_letter', # Preparar letra para pipeline
        'q_pipeline_done', # Pipeline cifrado hecho
        'q_accept'
    ]
    states.extend(control_states)

    # Transiciones para leer clave: acumulamos clave (una letra A-Z) o número (una o dos cifras) simplificado: asumimos solo letra o un dígito (para demo)
    # Si se requiere números mayores, se ampliaría.
    # Demo: si es letra: ejecutamos l2n directamente sobre esa letra (escribiendo marcas), luego pasamos a q_key_done al ver '#'

    # Leer primer símbolo (letra) -> mover a pipeline l2n
    for letter in [chr(c) for c in range(ord('A'), ord('Z')+1)]:
        transitions.append({'current_state':'q_start','read_symbol':letter,'next_state':l2n['initial_state'],'write_symbol':letter,'move':'N'})
    # Si primer símbolo es dígito (1..9) — tratamos como tantas marcas como su valor (simplificado)
    for digit in '123456789':
        transitions.append({'current_state':'q_start','read_symbol':digit,'next_state':'q_read_key','write_symbol':digit,'move':'R'})
    # Pasar a leer '#'
    transitions.append({'current_state':'q_start','read_symbol':'#','next_state':'q_read_char','write_symbol':'#','move':'R'})

    # L2N accept states: al terminar conversión de clave la cabeza queda; necesitamos transición hacia q_key_done cuando vemos '#'
    for acc in l2n['accept_states']:
        transitions.append({'current_state':acc,'read_symbol':'#','next_state':'q_key_done','write_symbol':'#','move':'R'})

    # Desde q_key_done, comenzar a procesar caracteres del mensaje
    transitions.append({'current_state':'q_key_done','read_symbol':'_','next_state':'q_accept','write_symbol':'_','move':'N'})
    transitions.append({'current_state':'q_key_done','read_symbol':'#','next_state':'q_read_char','write_symbol':'#','move':'R'})
    # Lectura de cada carácter
    transitions.append({'current_state':'q_read_char','read_symbol':'_','next_state':'q_accept','write_symbol':'_','move':'N'})
    # Si espacio u otro símbolo copiar (simplificado solo espacio y punto)
    transitions.append({'current_state':'q_read_char','read_symbol':' ','next_state':'q_read_char','write_symbol':' ','move':'R'})
    transitions.append({'current_state':'q_read_char','read_symbol':'.','next_state':'q_read_char','write_symbol':'.','move':'R'})

    # Para cada letra: ir a pipeline L2N
    for letter in [chr(c) for c in range(ord('A'), ord('Z')+1)]:
        transitions.append({'current_state':'q_read_char','read_symbol':letter,'next_state':l2n['initial_state'],'write_symbol':letter,'move':'N'})
        # Al finalizar L2N (accept states) iniciar suma: insertar '+' y shift marcas asumidas a la izquierda (simplificación: shift marcas permanecen intactas antes del '#')
        for acc in l2n['accept_states']:
            transitions.append({'current_state':acc,'read_symbol':letter,'next_state':acc,'write_symbol':letter,'move':'N'})
        # Usamos una transición ficticia para pasar a ADD cuando vemos primera marca '|' después de convertir la letra
        for acc in l2n['accept_states']:
            transitions.append({'current_state':acc,'read_symbol':'|','next_state':addp['initial_state'],'write_symbol':'|','move':'N'})

    # Integrar transiciones de sub-máquinas (pipeline) directamente
    transitions.extend(l2n['transitions'])
    transitions.extend(addp['transitions'])
    transitions.extend(modp['transitions'])
    transitions.extend(n2l['transitions'])

    # Al terminar n2l (accept), volver a q_read_char para siguiente letra
    for acc in n2l['accept_states']:
        transitions.append({'current_state':acc,'read_symbol':' ','next_state':'q_read_char','write_symbol':' ','move':'R'})
        transitions.append({'current_state':acc,'read_symbol':'.','next_state':'q_read_char','write_symbol':'.','move':'R'})
        transitions.append({'current_state':acc,'read_symbol':'_','next_state':'q_accept','write_symbol':'_','move':'N'})
        # Si siguiente es letra continuar
        for letter in [chr(c) for c in range(ord('A'), ord('Z')+1)]:
            transitions.append({'current_state':acc,'read_symbol':letter,'next_state':l2n['initial_state'],'write_symbol':letter,'move':'N'})

    machine = {
        'description': 'MT unificada para ' + ('encripción' if encrypt else 'decripción') + ' (simplificada demostrativa)',
        'states': states + l2n['states'] + addp['states'] + modp['states'] + n2l['states'],
        'input_alphabet': input_alphabet,
        'tape_alphabet': tape_alphabet,
        'initial_state': 'q_start',
        'accept_states': ['q_accept'],
        'blank_symbol': '_',
        'transitions': transitions
    }
    out_name = 'caesar_encrypt_full.json' if encrypt else 'caesar_decrypt_full.json'
    with open(CONFIG_DIR / out_name, 'w', encoding='utf-8') as f:
        json.dump(machine, f, ensure_ascii=False, indent=2)
    return out_name, len(machine['states']), len(machine['transitions'])


def main():
    enc_file, enc_states, enc_trans = build_unified(True)
    dec_file, dec_states, dec_trans = build_unified(False)
    print(f"Generado {enc_file}: {enc_states} estados, {enc_trans} transiciones")
    print(f"Generado {dec_file}: {enc_states} estados, {enc_trans} transiciones (estructura similar)")

if __name__ == '__main__':
    main()
