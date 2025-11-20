from __future__ import annotations
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from orchestrator import encrypt_text, decrypt_text  # type: ignore
from turing_simulator import TuringMachine  # type: ignore


class CaesarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cifrado César — Simulador con Máquinas de Turing")
        self.geometry("1200x750")
        self.minsize(1000, 700)
        
        # Estado de simulación visual
        self.current_machine_name = ""
        self.current_machine = None
        self.simulation_steps = []
        self.current_step_index = 0
        self.is_playing = False
        self.step_delay = tk.IntVar(value=500)
        
        self._build()

    def _build(self):
        root = ttk.Frame(self)
        root.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        title = ttk.Label(root, text="Cifrado César", 
                         font=("Segoe UI", 16, "bold"))
        title.pack(pady=(0, 4))
        
        desc = ttk.Label(root, text="Visualiza cómo las MTs procesan cada letra: letter→marks → +shift → mod26 → marks→letter",
                        foreground="gray", font=("Segoe UI", 9))
        desc.pack(pady=(0, 10))

        # Panel de entrada
        input_frame = ttk.LabelFrame(root, text="Entrada", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 8))

        # Panel de entrada
        input_frame = ttk.LabelFrame(root, text="Entrada", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Formato
        format_frame = ttk.Frame(input_frame)
        format_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(format_frame, text="Formato: clave#texto   Ejemplo:", 
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        ttk.Label(format_frame, text="3#ROMA", 
                 font=("Segoe UI", 9, "italic"), foreground="blue").pack(side=tk.LEFT, padx=8)

        # Campo de entrada
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill=tk.X)
        ttk.Label(entry_frame, text="Entrada:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        self.entry_input = ttk.Entry(entry_frame, font=("Consolas", 11))
        self.entry_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry_input.insert(0, '3#ROMA')
        
        # Botones principales
        self.btn_encrypt = ttk.Button(entry_frame, text="🔒 Encriptar", command=self._on_encrypt)
        self.btn_decrypt = ttk.Button(entry_frame, text="🔓 Desencriptar", command=self._on_decrypt)
        self.btn_encrypt.pack(side=tk.LEFT, padx=2)
        self.btn_decrypt.pack(side=tk.LEFT, padx=2)
        
        # Ejemplos rápidos en una segunda fila
        examples = ttk.Frame(input_frame)
        examples.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(examples, text="Ejemplos:", foreground="gray", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=4)
        ttk.Button(examples, text="3#ROMA", width=10, 
                  command=lambda: self._load_example('3#ROMA')).pack(side=tk.LEFT, padx=2)
        ttk.Button(examples, text="5#HOLA", width=10,
                  command=lambda: self._load_example('5#HOLA')).pack(side=tk.LEFT, padx=2)
        ttk.Button(examples, text="1#XYZ", width=10,
                  command=lambda: self._load_example('1#XYZ')).pack(side=tk.LEFT, padx=2)

        # Panel de visualización de la cinta (Canvas)
        visual_frame = ttk.LabelFrame(root, text="Simulación Visual de la Máquina de Turing", padding=8)
        visual_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        # Info superior del canvas
        canvas_info = ttk.Frame(visual_frame)
        canvas_info.pack(fill=tk.X, pady=(0, 4))
        
        self.lbl_machine_name = ttk.Label(canvas_info, text="Máquina: -", 
                                         font=("Segoe UI", 10, "bold"), foreground="purple")
        self.lbl_machine_name.pack(side=tk.LEFT, padx=4)
        
        self.lbl_state_info = ttk.Label(canvas_info, text="Estado: -", font=("Consolas", 9))
        self.lbl_state_info.pack(side=tk.LEFT, padx=12)
        
        self.lbl_step_info = ttk.Label(canvas_info, text="Paso: 0/0", font=("Consolas", 9))
        self.lbl_step_info.pack(side=tk.LEFT, padx=4)
        
        # Canvas para dibujar la cinta
        self.canvas = tk.Canvas(visual_frame, bg="white", height=180, relief=tk.SUNKEN, bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        
        # Controles de navegación
        controls = ttk.Frame(visual_frame)
        controls.pack(fill=tk.X)
        
        ttk.Label(controls, text="Velocidad:").pack(side=tk.LEFT, padx=4)
        self.scale_speed = ttk.Scale(controls, from_=100, to=2000, orient=tk.HORIZONTAL,
                                     variable=self.step_delay, length=150)
        self.scale_speed.pack(side=tk.LEFT, padx=4)
        ttk.Label(controls, textvariable=self.step_delay).pack(side=tk.LEFT, padx=4)
        ttk.Label(controls, text="ms").pack(side=tk.LEFT)
        
        ttk.Separator(controls, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        self.btn_first = ttk.Button(controls, text="⏮ Inicio", command=self._on_first_step, width=10)
        self.btn_prev = ttk.Button(controls, text="◀ Anterior", command=self._on_prev_step, width=10)
        self.btn_play = ttk.Button(controls, text="▶ Play", command=self._on_play, width=10)
        self.btn_pause = ttk.Button(controls, text="⏸ Pausa", command=self._on_pause, width=10)
        self.btn_next = ttk.Button(controls, text="Siguiente ▶", command=self._on_next_step, width=10)
        self.btn_last = ttk.Button(controls, text="Fin ⏭", command=self._on_last_step, width=10)
        
        self.btn_first.pack(side=tk.LEFT, padx=2)
        self.btn_prev.pack(side=tk.LEFT, padx=2)
        self.btn_play.pack(side=tk.LEFT, padx=2)
        self.btn_pause.pack(side=tk.LEFT, padx=2)
        self.btn_next.pack(side=tk.LEFT, padx=2)
        self.btn_last.pack(side=tk.LEFT, padx=2)

        # Panel inferior: Resultado y Log
        bottom_pane = ttk.Frame(root)
        bottom_pane.pack(fill=tk.BOTH, expand=True)
        # Resultado
        result_frame = ttk.LabelFrame(bottom_pane, text="Resultado", padding=8)
        result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        
        self.result_text = tk.Text(result_frame, height=3, font=("Consolas", 12), 
                                   wrap=tk.WORD, bg="#f0f0f0", relief=tk.FLAT)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Log
        log_frame = ttk.LabelFrame(bottom_pane, text="Log de Proceso", padding=8)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=3, font=("Consolas", 9),
                                                  wrap=tk.WORD, bg="#fafafa")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self._log("Sistema listo. Ingrese entrada en formato clave#texto y presione Encriptar o Desencriptar")
        self._draw_empty_canvas()

    def _draw_empty_canvas(self):
        """Dibuja un canvas vacío con mensaje"""
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 180
        self.canvas.create_text(w/2, h/2, 
                               text="Ejecute una operación de cifrado/descifrado para ver la simulación",
                               font=("Segoe UI", 11), fill="gray")

    def _parse_input(self):
        """Parsea la entrada en formato clave#texto"""
        inp = self.entry_input.get().strip()
        if not inp:
            raise ValueError("La entrada no puede estar vacía")
        if '#' not in inp:
            raise ValueError("Formato inválido. Use: clave#texto (ejemplo: 3#HOLA)")
        
        parts = inp.split('#', 1)
        key_str = parts[0].strip()
        text = parts[1] if len(parts) > 1 else ''
        
        try:
            key_num = int(key_str)
        except ValueError:
            raise ValueError(f"La clave debe ser un número (0-25), recibido: '{key_str}'")
        
        if not (0 <= key_num <= 25):
            raise ValueError(f"La clave debe estar entre 0 y 25, recibido: {key_num}")
        
        # Convertir número a letra (0=A, 1=B, ..., 25=Z)
        key_letter = chr(ord('A') + key_num)
        
        return key_letter, text, key_num

    def _on_encrypt(self):
        try:
            key_letter, text, key_num = self._parse_input()
            self._log(f"\n{'='*50}")
            self._log(f"ENCRIPTANDO con clave {key_num} (letra {key_letter})")
            self._log(f"Texto original: '{text}'")
            
            # Generar pasos de simulación para la primera letra (demo)
            if text and text[0].isalpha():
                self._generate_encryption_steps(text[0].upper(), key_letter)
            
            result = encrypt_text(key_letter, text)
            
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert('1.0', result)
            self.result_text.tag_add("result", "1.0", tk.END)
            self.result_text.tag_config("result", foreground="darkgreen", font=("Consolas", 12, "bold"))
            
            self._log(f"✓ Texto cifrado: '{result}'")
            
        except Exception as e:
            self._log(f"✗ ERROR: {str(e)}")
            messagebox.showerror("Error de Encriptación", str(e))

    def _on_decrypt(self):
        try:
            key_letter, text, key_num = self._parse_input()
            self._log(f"\n{'='*50}")
            self._log(f"DESENCRIPTANDO con clave {key_num} (letra {key_letter})")
            self._log(f"Texto cifrado: '{text}'")
            
            # Generar pasos de simulación para la primera letra (demo)
            if text and text[0].isalpha():
                self._generate_decryption_steps(text[0].upper(), key_letter)
            
            result = decrypt_text(key_letter, text)
            
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert('1.0', result)
            self.result_text.tag_add("result", "1.0", tk.END)
            self.result_text.tag_config("result", foreground="darkblue", font=("Consolas", 12, "bold"))
            
            self._log(f"✓ Texto descifrado: '{result}'")
            
        except Exception as e:
            self._log(f"✗ ERROR: {str(e)}")
            messagebox.showerror("Error de Desencriptación", str(e))

    def _generate_encryption_steps(self, letter: str, shift_letter: str):
        """Genera pasos de simulación para encriptar una letra - TODO el pipeline"""
        self.simulation_steps = []
        self.current_step_index = 0
        
        self._log(f"→ Generando simulación completa del cifrado para '{letter}' con shift '{shift_letter}'...")
        
        # ETAPA 1: Convertir letra a marcas
        self._log(f"  Etapa 1/4: letter_to_number.json - Convertir {letter} a marcas")
        tm1 = TuringMachine(os.path.join(ROOT, 'config', 'letter_to_number.json'))
        tm1.initialize_tape(letter)
        self._capture_tm_steps(tm1, 'letter_to_number.json', f'Convertir {letter} → marcas unarias')
        letra_marcas = tm1.get_tape_contents()
        
        # ETAPA 2: Convertir shift a marcas
        self._log(f"  Etapa 2/4: letter_to_number.json - Convertir shift {shift_letter} a marcas")
        tm2 = TuringMachine(os.path.join(ROOT, 'config', 'letter_to_number.json'))
        tm2.initialize_tape(shift_letter)
        self._capture_tm_steps(tm2, 'letter_to_number.json', f'Convertir shift {shift_letter} → marcas')
        shift_marcas = tm2.get_tape_contents()
        
        # Sanear marcas (solo |)
        letra_marcas_clean = ''.join(ch for ch in letra_marcas if ch == '|')
        shift_marcas_clean = ''.join(ch for ch in shift_marcas if ch == '|')
        
        # ETAPA 3: Sumar marcas (add_simple)
        self._log(f"  Etapa 3/4: add_simple.json - Sumar {len(letra_marcas_clean)} + {len(shift_marcas_clean)} marcas")
        input_suma = f"{letra_marcas_clean}+{shift_marcas_clean}"
        tm3 = TuringMachine(os.path.join(ROOT, 'config', 'add_simple.json'))
        tm3.initialize_tape(input_suma)
        self._capture_tm_steps(tm3, 'add_simple.json', f'Sumar marcas: {len(letra_marcas_clean)} + {len(shift_marcas_clean)}')
        suma_result = tm3.get_tape_contents()
        suma_marcas = ''.join(ch for ch in suma_result if ch == '|')
        
        # ETAPA 4: Aplicar mod26 (si es necesario)
        if len(suma_marcas) >= 26:
            self._log(f"  Etapa 4a/4: subtract_simple.json - Aplicar mod26 ({len(suma_marcas)} marcas)")
            twenty_six = '|' * 26
            input_mod = f"{suma_marcas}-{twenty_six}"
            tm4 = TuringMachine(os.path.join(ROOT, 'config', 'subtract_simple.json'))
            tm4.initialize_tape(input_mod)
            self._capture_tm_steps(tm4, 'subtract_simple.json', f'Mod26: {len(suma_marcas)} - 26')
            mod_result = tm4.get_tape_contents()
            marcas_final = ''.join(ch for ch in mod_result if ch == '|')
        else:
            marcas_final = suma_marcas
            self._log(f"  Etapa 4a/4: Sin mod26 necesario ({len(suma_marcas)} < 26)")
        
        # ETAPA 5: Convertir marcas a letra
        self._log(f"  Etapa 4b/4: number_to_letter.json - Convertir {len(marcas_final)} marcas → letra")
        tm5 = TuringMachine(os.path.join(ROOT, 'config', 'number_to_letter.json'))
        tm5.initialize_tape(marcas_final)
        self._capture_tm_steps(tm5, 'number_to_letter.json', f'Convertir {len(marcas_final)} marcas → letra')
        
        self._log(f"✓ Simulación completa: {len(self.simulation_steps)} pasos generados")
        self.current_step_index = 0
        self._update_canvas_from_step()

    def _capture_tm_steps(self, tm, machine_name, description, max_steps=200):
        """Captura todos los pasos de ejecución de una MT"""
        # Estado inicial
        self.simulation_steps.append({
            'machine': machine_name,
            'description': description,
            'tape': list(tm.tape),
            'head': tm.head_position,
            'state': tm.current_state,
            'step': 0
        })
        
        # Ejecutar hasta aceptación o max_steps
        step_count = 0
        while step_count < max_steps:
            if tm.current_state in tm.accept_states:
                break
            
            progressed = tm.step()
            if not progressed:
                break
            
            step_count += 1
            self.simulation_steps.append({
                'machine': machine_name,
                'description': description,
                'tape': list(tm.tape),
                'head': tm.head_position,
                'state': tm.current_state,
                'step': step_count
            })

    def _generate_decryption_steps(self, letter: str, shift_letter: str):
        """Genera pasos de simulación para desencriptar una letra - TODO el pipeline"""
        self.simulation_steps = []
        self.current_step_index = 0
        
        self._log(f"→ Generando simulación completa del descifrado para '{letter}' con shift '{shift_letter}'...")
        
        # ETAPA 1: Convertir letra cifrada a marcas
        self._log(f"  Etapa 1/4: letter_to_number.json - Convertir {letter} a marcas")
        tm1 = TuringMachine(os.path.join(ROOT, 'config', 'letter_to_number.json'))
        tm1.initialize_tape(letter)
        self._capture_tm_steps(tm1, 'letter_to_number.json', f'Convertir {letter} → marcas unarias')
        letra_marcas = tm1.get_tape_contents()
        
        # ETAPA 2: Convertir shift a marcas y calcular inverso (26-shift)
        self._log(f"  Etapa 2/4: Calcular shift inverso (26 - shift)")
        tm2 = TuringMachine(os.path.join(ROOT, 'config', 'letter_to_number.json'))
        tm2.initialize_tape(shift_letter)
        self._capture_tm_steps(tm2, 'letter_to_number.json', f'Convertir shift {shift_letter} → marcas')
        shift_marcas = tm2.get_tape_contents()
        
        # Calcular 26 - shift
        shift_marcas_clean = ''.join(ch for ch in shift_marcas if ch == '|')
        const26 = '|' * 26
        input_inv = f"{const26}-{shift_marcas_clean}"
        tm_inv = TuringMachine(os.path.join(ROOT, 'config', 'subtract_simple.json'))
        tm_inv.initialize_tape(input_inv)
        self._capture_tm_steps(tm_inv, 'subtract_simple.json', f'Calcular 26 - {len(shift_marcas_clean)}')
        inv_result = tm_inv.get_tape_contents()
        inv_marcas = ''.join(ch for ch in inv_result if ch == '|')
        
        # ETAPA 3: Sumar letra + shift_inverso
        letra_marcas_clean = ''.join(ch for ch in letra_marcas if ch == '|')
        self._log(f"  Etapa 3/4: add_simple.json - Sumar {len(letra_marcas_clean)} + {len(inv_marcas)} marcas")
        input_suma = f"{letra_marcas_clean}+{inv_marcas}"
        tm3 = TuringMachine(os.path.join(ROOT, 'config', 'add_simple.json'))
        tm3.initialize_tape(input_suma)
        self._capture_tm_steps(tm3, 'add_simple.json', f'Sumar: {len(letra_marcas_clean)} + {len(inv_marcas)}')
        suma_result = tm3.get_tape_contents()
        suma_marcas = ''.join(ch for ch in suma_result if ch == '|')
        
        # ETAPA 4: Aplicar mod26
        if len(suma_marcas) >= 26:
            self._log(f"  Etapa 4a/4: subtract_simple.json - Aplicar mod26")
            twenty_six = '|' * 26
            input_mod = f"{suma_marcas}-{twenty_six}"
            tm4 = TuringMachine(os.path.join(ROOT, 'config', 'subtract_simple.json'))
            tm4.initialize_tape(input_mod)
            self._capture_tm_steps(tm4, 'subtract_simple.json', f'Mod26: {len(suma_marcas)} - 26')
            mod_result = tm4.get_tape_contents()
            marcas_final = ''.join(ch for ch in mod_result if ch == '|')
        else:
            marcas_final = suma_marcas
            self._log(f"  Etapa 4a/4: Sin mod26 necesario")
        
        # ETAPA 5: Convertir marcas a letra
        self._log(f"  Etapa 4b/4: number_to_letter.json - Convertir {len(marcas_final)} marcas → letra")
        tm5 = TuringMachine(os.path.join(ROOT, 'config', 'number_to_letter.json'))
        tm5.initialize_tape(marcas_final)
        self._capture_tm_steps(tm5, 'number_to_letter.json', f'Convertir {len(marcas_final)} marcas → letra')
        
        self._log(f"✓ Simulación completa: {len(self.simulation_steps)} pasos generados")
        self.current_step_index = 0
        self._update_canvas_from_step()

    def _update_canvas_from_step(self):
        """Actualiza el canvas con el paso actual"""
        if not self.simulation_steps or self.current_step_index >= len(self.simulation_steps):
            self._draw_empty_canvas()
            return
        
        step = self.simulation_steps[self.current_step_index]
        
        self.current_machine_name = step['machine']
        self.lbl_machine_name.configure(text=f"Máquina: {step['machine']}")
        self.lbl_state_info.configure(text=f"Estado: {step['state']}")
        self.lbl_step_info.configure(text=f"Paso: {self.current_step_index + 1}/{len(self.simulation_steps)}")
        
        self._draw_tape_from_step(step)

    def _draw_tape_from_step(self, step):
        """Dibuja la cinta desde un paso capturado"""
        self.canvas.delete("all")
        
        tape = step['tape']
        head = step['head']
        state = step['state']
        blank = '_'
        
        cell_w, cell_h = 40, 60
        window = 20  # Celdas visibles
        
        start = max(0, head - window // 2)
        end = min(len(tape), start + window)
        
        # Asegurar ventana mínima
        if end - start < window:
            end = min(len(tape), start + window)
        
        margin_x = 50
        margin_y = 50
        
        for i in range(start, end):
            x = margin_x + (i - start) * cell_w
            y = margin_y
            
            is_head = (i == head)
            fill_color = "#fff6cc" if is_head else "white"
            
            # Celda
            self.canvas.create_rectangle(x, y, x + cell_w, y + cell_h, 
                                        fill=fill_color, outline="#333", width=2)
            
            # Símbolo
            sym = tape[i] if i < len(tape) else blank
            display_sym = sym if sym != '_' else '⊔'
            self.canvas.create_text(x + cell_w/2, y + cell_h/2, 
                                  text=display_sym, font=("Courier New", 12, "bold"))
            
            # Indicador de cabezal
            if is_head:
                self.canvas.create_text(x + cell_w/2, y - 20, 
                                      text="▼", fill="red", font=("Arial", 16, "bold"))
                self.canvas.create_text(x + cell_w/2, y + cell_h + 16,
                                      text="HEAD", fill="red", font=("Arial", 8, "bold"))
        
        # Estado
        canvas_width = self.canvas.winfo_width() or 800
        self.canvas.create_text(canvas_width/2, margin_y + cell_h + 40,
                              text=f"q = {state}", fill="blue", 
                              font=("Segoe UI", 11, "bold"))

    # Controles de navegación
    def _on_first_step(self):
        self.current_step_index = 0
        self._update_canvas_from_step()
    
    def _on_prev_step(self):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self._update_canvas_from_step()
    
    def _on_next_step(self):
        if self.current_step_index < len(self.simulation_steps) - 1:
            self.current_step_index += 1
            self._update_canvas_from_step()
    
    def _on_last_step(self):
        if self.simulation_steps:
            self.current_step_index = len(self.simulation_steps) - 1
            self._update_canvas_from_step()
    
    def _on_play(self):
        if not self.simulation_steps:
            return
        self.is_playing = True
        self._play_loop()
    
    def _play_loop(self):
        if not self.is_playing:
            return
        if self.current_step_index < len(self.simulation_steps) - 1:
            self.current_step_index += 1
            self._update_canvas_from_step()
            self.after(self.step_delay.get(), self._play_loop)
        else:
            self.is_playing = False
    
    def _on_pause(self):
        self.is_playing = False

    def _load_example(self, example: str):
        self.entry_input.delete(0, tk.END)
        self.entry_input.insert(0, example)
        self._log(f"Ejemplo cargado: {example}")

    def _log(self, msg: str):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)


def main():
    app = CaesarApp()
    app.mainloop()


if __name__ == "__main__":
    main()
