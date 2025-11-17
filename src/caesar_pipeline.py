"""Pipeline de Cifrado/Descifrado César con trazas paso a paso.
Construye una secuencia de snapshots (tape, head, estado, transición, etapa) para animación GUI.
No altera las clases existentes de cifrado; reutiliza los JSON modulares.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional
import os

# Import dual: funciona tanto si se importa como paquete (src.caesar_pipeline)
# como módulo suelto (caesar_pipeline) añadido a sys.path.
try:
    from turing_machine import TuringMachine  # absolute when 'src' is on sys.path
except ImportError:  # pragma: no cover
    from .turing_machine import TuringMachine  # relative when imported as package

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')

@dataclass
class PipelineStep:
    stage: str
    index: int
    tape: List[str]
    head: int
    state: str
    delta: Optional[Tuple[str, str, str]]  # (next_state, write_symbol, move) aplicado en el paso
    accept: bool

@dataclass
class PipelineResult:
    steps: List[PipelineStep]
    output: str  # Mensaje final cifrado/descifrado

# Utilidades internas -------------------------------------------------

def _collect_machine_steps(config_name: str, input_string: str, stage_prefix: str, max_steps: int = 2000) -> Tuple[List[PipelineStep], str]:
    tm = TuringMachine()
    if not tm.load_config(os.path.join(CONFIG_DIR, config_name)):
        raise RuntimeError(f"No se pudo cargar {config_name}")
    tm.initialize_tape(input_string)
    steps: List[PipelineStep] = []
    local_index = 0
    while not tm.halted and tm.step_count < max_steps:
        # Obtener transición antes de step para mostrar como se aplicará
        current_symbol = tm.get_current_symbol()
        current_state = tm.current_state
        transition = tm.find_transition(current_state, current_symbol)
        progressed = tm.step()
        # Snapshot después del paso
        tape_snapshot = list(tm.tape)
        step = PipelineStep(
            stage=f"{stage_prefix}",
            index=local_index,
            tape=tape_snapshot,
            head=tm.head_position,
            state=tm.current_state,
            delta=transition,
            accept=tm.is_accepting_state(),
        )
        steps.append(step)
        local_index += 1
        if not progressed:
            break
        if tm.is_accepting_state():
            break
    output = ''.join(tm.tape).rstrip(tm.blank_symbol)
    return steps, output

# Conversion clave -> marcas -------------------------------------------------

def _key_letter_to_marks(letter: str) -> Tuple[List[PipelineStep], str]:
    letter = letter.upper()
    return _collect_machine_steps('letter_to_number.json', letter, 'clave: letra->marcas')


def _key_number_to_letter(number: str) -> Tuple[List[PipelineStep], str]:
    return _collect_machine_steps('number_key_to_letter.json', number, 'clave: numero->letra')


def _subtract_26_minus_marks(marks: str) -> Tuple[List[PipelineStep], str]:
    base_26 = '|' * 26
    return _collect_machine_steps('subtract_simple.json', f"{base_26}-{marks}", 'clave: resta 26 - k')

# Public API -----------------------------------------------------------------

def build_encrypt_pipeline(w: str) -> PipelineResult:
    if '#' not in w:
        raise ValueError("Formato inválido: falta '#' en w")
    raw_key, message = w.split('#', 1)
    raw_key = raw_key.strip()
    message = message.strip()

    all_steps: List[PipelineStep] = []

    # Obtener marcas de desplazamiento via etapas de MT
    if len(raw_key) == 1 and raw_key.isalpha():
        key_steps, key_marks_out = _key_letter_to_marks(raw_key)
        all_steps.extend(key_steps)
        shift_marks = ''.join(c for c in key_marks_out if c == '|')
    elif raw_key.isdigit():
        key_letter_steps, key_letter_out = _key_number_to_letter(raw_key)
        all_steps.extend(key_letter_steps)
        key_letter = next((c for c in key_letter_out if c.isalpha()), 'A')
        key_marks_steps, key_marks_out = _key_letter_to_marks(key_letter)
        all_steps.extend(key_marks_steps)
        shift_marks = ''.join(c for c in key_marks_out if c == '|')
    else:
        raise ValueError('Clave inválida: debe ser número (1-27) o letra A-Z')

    encrypted_chars: List[str] = []

    # Procesar cada carácter
    for pos, ch in enumerate(message):
        if not ch.isalpha():
            encrypted_chars.append(ch)
            continue
        upper = ch.upper()
        # letra -> marcas
        lt_steps, lt_out = _collect_machine_steps('letter_to_number.json', upper, f"[{pos}] letra->marcas")
        all_steps.extend(lt_steps)
        letter_marks = ''.join(c for c in lt_out if c == '|')
        # suma
        add_input = f"{letter_marks}+{shift_marks}" if shift_marks else f"{letter_marks}+"
        add_steps, add_out = _collect_machine_steps('add_simple.json', add_input, f"[{pos}] suma marcas + shift")
        all_steps.extend(add_steps)
        sum_marks = ''.join(c for c in add_out if c == '|')
        # mod 26
        mod_input = sum_marks if sum_marks else '_'
        mod_steps, mod_out = _collect_machine_steps('mod26_full.json', mod_input, f"[{pos}] mod26")
        all_steps.extend(mod_steps)
        mod_marks = ''.join(c for c in mod_out if c == '|')
        # marcas -> letra
        back_input = mod_marks if mod_marks else '_'
        back_steps, back_out = _collect_machine_steps('number_to_letter.json', back_input, f"[{pos}] marcas->letra")
        all_steps.extend(back_steps)
        out_letter = next((c for c in back_out if c.isalpha()), upper)
        encrypted_chars.append(out_letter if ch.isupper() else out_letter.lower())

    return PipelineResult(steps=all_steps, output=''.join(encrypted_chars))


def build_decrypt_pipeline(w: str) -> PipelineResult:
    if '#' not in w:
        raise ValueError("Formato inválido: falta '#' en w")
    raw_key, message = w.split('#', 1)
    raw_key = raw_key.strip()
    message = message.strip()

    all_steps: List[PipelineStep] = []

    # Obtener marcas de la clave
    if len(raw_key) == 1 and raw_key.isalpha():
        key_steps, key_marks_out = _key_letter_to_marks(raw_key)
        all_steps.extend(key_steps)
        key_marks = ''.join(c for c in key_marks_out if c == '|')
    elif raw_key.isdigit():
        key_letter_steps, key_letter_out = _key_number_to_letter(raw_key)
        all_steps.extend(key_letter_steps)
        key_letter = next((c for c in key_letter_out if c.isalpha()), 'A')
        key_marks_steps, key_marks_out = _key_letter_to_marks(key_letter)
        all_steps.extend(key_marks_steps)
        key_marks = ''.join(c for c in key_marks_out if c == '|')
    else:
        raise ValueError('Clave inválida: debe ser número (1-27) o letra A-Z')

    # Obtener inverse shift marks mediante resta 26 - k
    if key_marks:
        inv_steps, inv_out = _subtract_26_minus_marks(key_marks)
        all_steps.extend(inv_steps)
        inverse_marks = ''.join(c for c in inv_out if c == '|')
    else:
        inverse_marks = ''

    decrypted_chars: List[str] = []

    for pos, ch in enumerate(message):
        if not ch.isalpha():
            decrypted_chars.append(ch)
            continue
        upper = ch.upper()
        lt_steps, lt_out = _collect_machine_steps('letter_to_number.json', upper, f"[{pos}] letra->marcas")
        all_steps.extend(lt_steps)
        letter_marks = ''.join(c for c in lt_out if c == '|')
        add_input = f"{letter_marks}+{inverse_marks}" if inverse_marks else f"{letter_marks}+"
        add_steps, add_out = _collect_machine_steps('add_simple.json', add_input, f"[{pos}] suma + invShift")
        all_steps.extend(add_steps)
        sum_marks = ''.join(c for c in add_out if c == '|')
        mod_input = sum_marks if sum_marks else '_'
        mod_steps, mod_out = _collect_machine_steps('mod26_full.json', mod_input, f"[{pos}] mod26")
        all_steps.extend(mod_steps)
        mod_marks = ''.join(c for c in mod_out if c == '|')
        back_input = mod_marks if mod_marks else '_'
        back_steps, back_out = _collect_machine_steps('number_to_letter.json', back_input, f"[{pos}] marcas->letra")
        all_steps.extend(back_steps)
        out_letter = next((c for c in back_out if c.isalpha()), upper)
        decrypted_chars.append(out_letter if ch.isupper() else out_letter.lower())

    return PipelineResult(steps=all_steps, output=''.join(decrypted_chars))
