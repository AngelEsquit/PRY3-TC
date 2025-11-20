"""Visualizador de Máquina de Turing (desde cero, centrado en cinta, cabezal y estado).

Permite:
- Cargar configuración JSON de MT
- Inicializar con cadena de entrada
- Ejecutar paso a paso o en modo automático con control de velocidad
- Visualizar cinta, cabezal, estado actual y transición aplicada
- Ver registro/trace de los pasos

Esta GUI se centra en la visualización de la MT, no en el cifrado César.
"""
from __future__ import annotations
import os
import sys
import re
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Asegurar que src esté en el path si se ejecuta desde el root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from turing_machine import TuringMachine  # type: ignore

# Eliminado soporte específico de Cifrado César en Python.
# La GUI ahora es puramente universal: cualquier JSON cargado se simula.
PipelineStep = None  # Mantener referencias opcionales inertes


class TMVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Máquina de Turing — PRY3-TC")
        self.geometry("1200x780")
        self.minsize(1000, 680)

        # MT y estado de simulación
        self.tm: TuringMachine | None = None
        self.loaded_config: str | None = None
        self.running = False
        self.step_delay_ms = tk.IntVar(value=300)
        self.max_steps = tk.IntVar(value=100000)
        self.step_count = 0
        self.cfg_input_alphabet: set[str] = set()
        self.cfg_blank: str = '_'
        self.cfg_example: str | None = None
        self._example_suggestion: str | None = None
        # Variables de pipeline removidas (modo César específico). Se deja estructura mínima.
        self.pipeline_steps: list = []
        self.pipeline_index = 0
        self.pipeline_playing = False
        self.pipeline_mode = False
        self.pipeline_filtered_steps: list = []
        self.pipeline_stage_counts: dict[str, int] = {}
        self.pipeline_use_filtered = False
        # Condensación
        self.var_condense_boundaries = tk.BooleanVar(value=True)
        self.var_sample_n = tk.IntVar(value=10)

        self._make_style()
        self._build()
        self._wire()

    def _make_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

    def _build(self):
        root = ttk.Frame(self)
        root.pack(fill=tk.BOTH, expand=True)

        # Top controls
        top = ttk.LabelFrame(root, text="Control")
        top.pack(fill=tk.X, padx=6, pady=6)

        self.btn_load = ttk.Button(top, text="Cargar JSON…")
        self.lbl_cfg = ttk.Label(top, text="Sin archivo", foreground="gray")
        ttk.Label(top, text="Entrada w:").pack(side=tk.LEFT, padx=(8, 4))
        self.entry_w = ttk.Entry(top, width=40)
        self.entry_w.insert(0, "AAA")

        self.btn_init = ttk.Button(top, text="Inicializar")
        self.btn_step = ttk.Button(top, text="Paso (δ)")
        self.btn_run = ttk.Button(top, text="▶ Ejecutar")
        self.btn_pause = ttk.Button(top, text="⏸ Pausa")
        self.btn_reset = ttk.Button(top, text="⟲ Reset")

        for w in [self.btn_load, self.lbl_cfg, self.entry_w, self.btn_init, self.btn_step, self.btn_run, self.btn_pause, self.btn_reset]:
            w.pack(side=tk.LEFT, padx=4)

        # Speed and limits
        speed_frame = ttk.Frame(root)
        speed_frame.pack(fill=tk.X, padx=6)
        ttk.Label(speed_frame, text="Velocidad (ms entre pasos):").pack(side=tk.LEFT)
        self.scale_speed = ttk.Scale(speed_frame, from_=50, to=1000, orient=tk.HORIZONTAL,
                                     command=lambda _=None: self._on_speed_change())
        self.scale_speed.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.scale_speed.set(self.step_delay_ms.get())
        ttk.Label(speed_frame, text="Max steps:").pack(side=tk.LEFT, padx=(8, 4))
        self.spin_max = ttk.Spinbox(speed_frame, from_=1, to=1000000, textvariable=self.max_steps, width=8)
        self.spin_max.pack(side=tk.LEFT)

        # Panel César eliminado: se quitó completamente; no se crean controles.

        # Panel de Animación detallada
        anim = ttk.LabelFrame(root, text="Animación Paso a Paso (JSON universal)")
        anim.pack(fill=tk.X, padx=6, pady=(0, 6))
        ttk.Label(anim, text="Entrada inicial:").pack(side=tk.LEFT, padx=(6, 4))
        self.entry_anim_w = ttk.Entry(anim, width=40)
        self.entry_anim_w.insert(0, "AAA")
        self.entry_anim_w.pack(side=tk.LEFT, padx=4)
        self.btn_anim_step = ttk.Button(anim, text="Paso ▶")
        self.btn_anim_play = ttk.Button(anim, text="Play ▷")
        self.btn_anim_pause = ttk.Button(anim, text="Pausa ⏸")
        self.btn_anim_reset = ttk.Button(anim, text="Reset ⟲")
        self.btn_anim_step.pack(side=tk.LEFT, padx=2)
        self.btn_anim_play.pack(side=tk.LEFT, padx=2)
        self.btn_anim_pause.pack(side=tk.LEFT, padx=2)
        self.btn_anim_reset.pack(side=tk.LEFT, padx=2)
        self.lbl_anim_info = ttk.Label(anim, text="Listo", foreground="gray")
        self.lbl_anim_info.pack(side=tk.LEFT, padx=12)

        # Filtros y acciones extra para presentación
        present = ttk.LabelFrame(root, text="Herramientas de Presentación")
        present.pack(fill=tk.X, padx=6, pady=(0, 6))
        ttk.Label(present, text="Filtrar etapa:").pack(side=tk.LEFT, padx=(6, 4))
        self.combo_stage = ttk.Combobox(present, values=["(todas)"], state="readonly", width=28)
        self.combo_stage.current(0)
        self.combo_stage.pack(side=tk.LEFT, padx=4)
        self.btn_stage_apply = ttk.Button(present, text="Aplicar filtro")
        self.btn_stage_clear = ttk.Button(present, text="Limpiar filtro")
        self.btn_export = ttk.Button(present, text="Exportar trazas")
        self.btn_example_enc = ttk.Button(present, text="Ejemplo Encrypt")
        self.btn_example_dec = ttk.Button(present, text="Ejemplo Decrypt")
        self.btn_stage_apply.pack(side=tk.LEFT, padx=2)
        self.btn_stage_clear.pack(side=tk.LEFT, padx=2)
        self.btn_export.pack(side=tk.LEFT, padx=8)
        self.btn_example_enc.pack(side=tk.LEFT, padx=2)
        self.btn_example_dec.pack(side=tk.LEFT, padx=2)
        self.lbl_stage_stats = ttk.Label(present, text="Stats: -", foreground="gray")
        self.lbl_stage_stats.pack(side=tk.LEFT, padx=12)

        # Línea de condensación
        cond = ttk.Frame(root)
        cond.pack(fill=tk.X, padx=6, pady=(0, 6))
        ttk.Checkbutton(cond, text="Mostrar solo inicios/finales de etapa", variable=self.var_condense_boundaries).pack(side=tk.LEFT, padx=(4, 8))
        ttk.Label(cond, text="Muestrear cada N pasos:").pack(side=tk.LEFT)
        self.spin_sample = ttk.Spinbox(cond, from_=1, to=500, textvariable=self.var_sample_n, width=5)
        self.spin_sample.pack(side=tk.LEFT, padx=4)
        self.btn_condense_apply = ttk.Button(cond, text="Aplicar condensación")
        self.btn_condense_clear = ttk.Button(cond, text="Quitar condensación")
        self.btn_next_letter = ttk.Button(cond, text="Siguiente letra ▶|")
        self.btn_condense_apply.pack(side=tk.LEFT, padx=4)
        self.btn_condense_clear.pack(side=tk.LEFT, padx=2)
        self.btn_next_letter.pack(side=tk.LEFT, padx=8)

        # Main area with canvas and side info
        main_pane = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Canvas area
        canvas_frame = ttk.LabelFrame(main_pane, text="Cinta y Cabezal")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)

        # Right info panel
        info = ttk.LabelFrame(main_pane, text="Estado y Transición")
        info.columnconfigure(0, weight=1)
        ttk.Label(info, text="Estado actual:").grid(row=0, column=0, sticky=tk.W, padx=6, pady=(8, 2))
        self.lbl_state = ttk.Label(info, text="-", font=("Segoe UI", 12, "bold"))
        self.lbl_state.grid(row=1, column=0, sticky=tk.W, padx=6)

        ttk.Label(info, text="Símbolo bajo el cabezal:").grid(row=2, column=0, sticky=tk.W, padx=6, pady=(10, 2))
        self.lbl_symbol = ttk.Label(info, text="-")
        self.lbl_symbol.grid(row=3, column=0, sticky=tk.W, padx=6)

        ttk.Label(info, text="Transición aplicada δ(q, s):").grid(row=4, column=0, sticky=tk.W, padx=6, pady=(10, 2))
        self.lbl_delta = ttk.Label(info, text="-")
        self.lbl_delta.grid(row=5, column=0, sticky=tk.W, padx=6)

        ttk.Label(info, text="Pasos ejecutados:").grid(row=6, column=0, sticky=tk.W, padx=6, pady=(10, 2))
        self.lbl_steps = ttk.Label(info, text="0")
        self.lbl_steps.grid(row=7, column=0, sticky=tk.W, padx=6)

        ttk.Label(info, text="Σ (alfabeto de entrada):").grid(row=8, column=0, sticky=tk.W, padx=6, pady=(10, 2))
        self.lbl_sigma = ttk.Label(info, text="-")
        self.lbl_sigma.grid(row=9, column=0, sticky=tk.W, padx=6)

        ttk.Label(info, text="Símbolo blanco:").grid(row=10, column=0, sticky=tk.W, padx=6, pady=(10, 2))
        self.lbl_blank = ttk.Label(info, text="_")
        self.lbl_blank.grid(row=11, column=0, sticky=tk.W, padx=6)

        main_pane.add(canvas_frame, weight=3)
        main_pane.add(info, weight=1)

        # Bottom log
        bottom = ttk.LabelFrame(root, text="Log / Trazas")
        bottom.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        bottom.columnconfigure(0, weight=1)
        bottom.rowconfigure(0, weight=1)
        self.txt_log = scrolledtext.ScrolledText(bottom, wrap=tk.WORD, font=("Consolas", 9))
        self.txt_log.grid(row=0, column=0, sticky=tk.NSEW)


    def _wire(self):
        self.btn_load.configure(command=self._on_load)
        self.btn_init.configure(command=self._on_init)
        self.btn_step.configure(command=self._on_step)
        self.btn_run.configure(command=self._on_run)
        self.btn_pause.configure(command=self._on_pause)
        self.btn_reset.configure(command=self._on_reset)
        self.btn_cesar_encrypt.configure(command=self._on_cesar_encrypt)
        self.btn_cesar_decrypt.configure(command=self._on_cesar_decrypt)
        self.btn_anim_generate.configure(command=self._on_anim_generate)
        self.btn_anim_step.configure(command=self._on_anim_step)
        self.btn_anim_play.configure(command=self._on_anim_play)
        self.btn_anim_pause.configure(command=self._on_anim_pause)
        self.btn_anim_reset.configure(command=self._on_anim_reset)
        self.btn_stage_apply.configure(command=self._on_stage_apply)
        self.btn_stage_clear.configure(command=self._on_stage_clear)
        self.btn_export.configure(command=self._on_export_pipeline)
        self.btn_example_enc.configure(command=lambda: self._fill_example('encrypt'))
        self.btn_example_dec.configure(command=lambda: self._fill_example('decrypt'))
        self.btn_condense_apply.configure(command=self._on_condense_apply)
        self.btn_condense_clear.configure(command=self._on_condense_clear)
        self.btn_next_letter.configure(command=self._on_next_letter)

    # ---- Actions ----
    def _on_speed_change(self):
        try:
            self.step_delay_ms.set(int(float(self.scale_speed.get())))
        except Exception:
            pass

    def _on_load(self):
        fn = filedialog.askopenfilename(
            title="Seleccionar configuración JSON",
            initialdir=os.path.join(ROOT_DIR, 'config'),
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
        )
        if not fn:
            return
        tm = TuringMachine()
        if not tm.load_config(fn):
            messagebox.showerror("Error", "No se pudo cargar la configuración")
            return
        self.tm = tm
        self.loaded_config = fn
        self.lbl_cfg.configure(text=os.path.basename(fn), foreground="black")
        self._log(f"Cargado: {fn}")

        # Leer metadatos (Σ, blank, example) del JSON para validar entrada y sugerencias
        try:
            with open(fn, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            sigma = meta.get('input_alphabet') or []
            self.cfg_input_alphabet = set(sigma)
            self.cfg_blank = meta.get('blank_symbol', '_') or '_'
            self.cfg_example = meta.get('example') if isinstance(meta.get('example'), str) else None
            self._example_suggestion = self._extract_example(self.cfg_example, self.cfg_input_alphabet)
            # Mostrar Σ y blank en UI
            if self.cfg_input_alphabet:
                sigma_sorted = ', '.join(self._pretty_symbol(s) for s in sorted(self.cfg_input_alphabet))
                self.lbl_sigma.configure(text=f"{{{sigma_sorted}}}")
            else:
                self.lbl_sigma.configure(text="-")
            self.lbl_blank.configure(text=self._pretty_symbol(self.cfg_blank))
            # Prefijar entrada sugerida si hay ejemplo
            if self._example_suggestion:
                self.entry_w.delete(0, tk.END)
                self.entry_w.insert(0, self._example_suggestion)
        except Exception:
            # Si falla lectura del JSON, continuamos sin sugerencias
            pass

    def _on_init(self):
        if not self.tm:
            messagebox.showwarning("Atención", "Cargue una configuración primero")
            return
        w = self.entry_w.get()
        # Validar que w usa símbolos de Σ o blanco
        invalid = self._find_invalid_symbols(w)
        if invalid:
            msg = "La entrada contiene símbolos fuera de Σ: " + ', '.join(self._pretty_symbol(c) for c in sorted(invalid))
            if self._example_suggestion:
                msg += f"\n\nEjemplo sugerido: {self._example_suggestion}"
            messagebox.showwarning("Entrada inválida", msg)
            return
        self.tm.initialize_tape(w)
        self.step_count = 0
        self.running = False
        self._refresh_view(delta=None)
        self._log(f"Inicializado con w='{w}'")

    def _on_step(self):
        if not self.tm:
            return
        if self.tm.is_accepting_state():
            self._log("Estado de aceptación alcanzado")
            self.running = False
            return
        # Obtener transición antes de ejecutarla
        state = self._get_state()
        sym = self._get_symbol()
        delta = self._find_delta(state, sym)
        progressed = self.tm.step()  # bool
        self.step_count += 1
        self._refresh_view(delta=delta)
        if not progressed:
            self._log("Sin transición definida: ejecución detenida")
            self.running = False

    def _on_run(self):
        if not self.tm:
            return
        if self.running:
            return
        self.running = True
        self._run_loop()

    def _run_loop(self):
        if not self.running or not self.tm:
            return
        if self.step_count >= self.max_steps.get():
            self._log("Se alcanzó el máximo de pasos")
            self.running = False
            return
        if self.tm.is_accepting_state():
            self._log("Estado de aceptación alcanzado")
            self.running = False
            return
        self._on_step()
        delay = self.step_delay_ms.get()
        self.after(delay, self._run_loop)

    def _on_pause(self):
        self.running = False

    def _on_reset(self):
        if not self.tm:
            return
        try:
            # Reinicializar con la misma entrada
            self._on_init()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reiniciar: {e}")

    # ---- Rendering and helpers ----
    def _refresh_view(self, delta):
        # Update info labels
        state = self._get_state()
        sym = self._get_symbol()
        self.lbl_state.configure(text=str(state))
        self.lbl_symbol.configure(text=str(sym))
        if delta:
            qn, wr, mv = delta
            self.lbl_delta.configure(text=f"({state}, {sym}) → ({qn}, {wr}, {mv})")
        else:
            self.lbl_delta.configure(text="-")
        self.lbl_steps.configure(text=str(self.step_count))

        # Draw tape
        self._draw_tape()

    def _draw_tape(self):
        self.canvas.delete("all")
        active_steps = self._get_active_pipeline_steps()
        if self.pipeline_mode and active_steps:
            step = active_steps[self.pipeline_index]
            tape = step.tape
            head = step.head
            blank = '_'
        else:
            tape, head, blank = self._get_tape_snapshot()
        
        # Detectar si es multi-cinta
        if self.tm and hasattr(self.tm, 'num_tapes') and self.tm.num_tapes > 1:
            self._draw_multitape()
            return
        
        # Define visible window around head
        window = 31
        half = window // 2
        start = max(0, head - half)
        end = max(start + window, head + half + 1)
        if end > len(tape):
            end = len(tape)
            start = max(0, end - window)

        cell_w, cell_h = 34, 50
        margin_x, margin_y = 20, 40
        y = margin_y

        for i in range(start, end):
            x = margin_x + (i - start) * cell_w
            is_head = (i == head)
            fill = "#fff6cc" if is_head else "white"
            self.canvas.create_rectangle(x, y, x + cell_w, y + cell_h, fill=fill, outline="#333")
            ch = tape[i]
            disp = ch if ch != '_' else '⊔'
            self.canvas.create_text(x + cell_w/2, y + cell_h/2, text=disp, font=("Courier New", 16, "bold"))
            if is_head:
                self.canvas.create_text(x + cell_w/2, y - 18, text="▼", fill="red", font=("Arial", 20))

        # State label under the tape
        if self.pipeline_mode and active_steps:
            current = active_steps[self.pipeline_index]
            self.canvas.create_text(margin_x + (min(window, len(tape)) * cell_w)/2, y + cell_h + 16,
                                    text=f"Etapa: {current.stage}", fill="purple", font=("Segoe UI", 11, "bold"))
            self.canvas.create_text(margin_x + (min(window, len(tape)) * cell_w)/2, y + cell_h + 36,
                                    text=f"q = {current.state}", fill="blue", font=("Segoe UI", 12, "bold"))
            # Mostrar delta si disponible
            if current.delta:
                d_q, d_w, d_m = current.delta
                self.canvas.create_text(margin_x + (min(window, len(tape)) * cell_w)/2, y + cell_h + 56,
                                        text=f"δ: ({d_q}, {d_w}, {d_m})", fill="darkgreen", font=("Segoe UI", 10))
        else:
            self.canvas.create_text(margin_x + (min(window, len(tape)) * cell_w)/2, y + cell_h + 28,
                                    text=f"q = {self._get_state()}", fill="blue", font=("Segoe UI", 12, "bold"))

    def _draw_multitape(self):
        """Dibuja múltiples cintas para MTs multi-cinta"""
        if not self.tm or not hasattr(self.tm, 'tapes'):
            return
        
        num_tapes = len(self.tm.tapes)
        cell_w, cell_h = 28, 40
        window = 25  # Menos celdas por cinta para caber todas
        margin_x = 10
        tape_spacing = 80  # Espacio vertical entre cintas
        
        for tape_idx in range(num_tapes):
            tape = self.tm.tapes[tape_idx]
            head = self.tm.head_positions[tape_idx]
            blank = self.tm.blank_symbol
            
            # Ventana visible alrededor del cabezal
            half = window // 2
            start = max(0, head - half)
            end = max(start + window, head + half + 1)
            if end > len(tape):
                end = len(tape)
                start = max(0, end - window)
            
            y = 20 + tape_idx * tape_spacing
            
            # Label de cinta
            self.canvas.create_text(margin_x - 5, y + cell_h/2, text=f"T{tape_idx}:", 
                                   anchor="e", font=("Segoe UI", 10, "bold"))
            
            # Dibujar celdas
            for i in range(start, end):
                x = margin_x + (i - start) * cell_w
                is_head = (i == head)
                fill = "#fff6cc" if is_head else "white"
                self.canvas.create_rectangle(x, y, x + cell_w, y + cell_h, fill=fill, outline="#333")
                ch = tape[i] if i < len(tape) else blank
                disp = ch if ch != '_' else '⊔'
                self.canvas.create_text(x + cell_w/2, y + cell_h/2, text=disp, font=("Courier New", 11))
                if is_head:
                    self.canvas.create_text(x + cell_w/2, y - 12, text="▼", fill="red", font=("Arial", 14))
        
        # Estado debajo de todas las cintas
        self.canvas.create_text(margin_x + (window * cell_w)/2, 20 + num_tapes * tape_spacing + 10,
                                text=f"q = {self._get_state()}", fill="blue", font=("Segoe UI", 12, "bold"))

    def _get_state(self):
        if not self.tm:
            return '-'
        # Try common attribute name
        state = getattr(self.tm, 'current_state', None)
        if state is not None:
            return state
        # Fallback: no public accessor; show '-'
        return '-'

    def _get_symbol(self):
        if not self.tm:
            return '-'
        try:
            return self.tm.get_current_symbol()
        except Exception:
            return '-'

    def _find_delta(self, q, s):
        if not self.tm or q in (None, '-'):
            return None
        try:
            return self.tm.find_transition(q, s)
        except Exception:
            return None

    def _get_tape_snapshot(self):
        if not self.tm:
            return ['_'] * 31, 15, '_'
        # Try to access internal representation (common names)
        tape = getattr(self.tm, 'tape', None)
        blank = getattr(self.tm, 'blank_symbol', '_')
        head = getattr(self.tm, 'head_position', 0)
        if isinstance(tape, list):
            # Normalize to at least some blanks to avoid empty rendering
            if not tape:
                tape = [blank]
            return tape, max(0, head), blank
        # Fallback: synthesize from output of run/display (not ideal)
        try:
            # As last resort, show the initialized input centered
            w = self.entry_w.get()
            tape = list(w) if w else [blank]
            return tape, 0, blank
        except Exception:
            return ['_'] * 31, 15, '_'

    def _log(self, msg: str):
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)

    # ---- Caesar Cipher Handlers ----
    def _on_cesar_encrypt(self):
        w = self.entry_cesar_w.get().strip()
        if not w:
            self._log("[César] w vacío")
            return
        if '#' not in w:
            self._log("[César] Formato inválido: falta '#'")
            return
        if CaesarEncryptTM is None:
            self._log("[César] Clases no disponibles")
            return
        try:
            enc = CaesarEncryptTM(debug=False)
            out = enc.encrypt_w(w)
            self._log(f"[César][Encrypt] w='{w}' => '{out}'")
            self.lbl_cesar_status.configure(text="OK", foreground="green")
        except Exception as e:
            self._log(f"[César][Error Encrypt] {e}")
            self.lbl_cesar_status.configure(text="Error", foreground="red")

    def _on_cesar_decrypt(self):
        w = self.entry_cesar_w.get().strip()
        if not w:
            self._log("[César] w vacío")
            return
        if '#' not in w:
            self._log("[César] Formato inválido: falta '#'")
            return
        if CaesarDecryptTM is None:
            self._log("[César] Clases no disponibles")
            return
        try:
            dec = CaesarDecryptTM(debug=False)
            out = dec.decrypt_w(w)
            self._log(f"[César][Decrypt] w='{w}' => '{out}'")
            self.lbl_cesar_status.configure(text="OK", foreground="green")
        except Exception as e:
            self._log(f"[César][Error Decrypt] {e}")
            self.lbl_cesar_status.configure(text="Error", foreground="red")

    # ---- Animación Pipeline César ----
    def _on_anim_generate(self):
        if build_encrypt_pipeline is None or build_decrypt_pipeline is None:
            self._log("[Anim] Pipeline no disponible")
            return
        w = self.entry_anim_w.get().strip()
        if '#' not in w:
            self._log("[Anim] Formato inválido: falta '#'")
            return
        mode = self.var_anim_mode.get()
        try:
            if mode == 'encrypt':
                result = build_encrypt_pipeline(w)
            else:
                result = build_decrypt_pipeline(w)
        except Exception as e:
            self._log(f"[Anim] Error generando pasos: {e}")
            self.lbl_anim_info.configure(text="Error", foreground="red")
            return
        self.pipeline_steps = result.steps
        self.pipeline_index = 0
        self.pipeline_mode = True
        self.pipeline_playing = False
        self._refresh_view(delta=None)
        self.lbl_anim_info.configure(text=f"{len(self.pipeline_steps)} pasos - Resultado: {result.output}", foreground="green")
        self._log(f"[Anim] Generados {len(self.pipeline_steps)} pasos. Resultado final: {result.output}")
        self._update_stage_stats()
        self._populate_stage_combo()

    def _on_anim_step(self):
        active_steps = self._get_active_pipeline_steps()
        if not self.pipeline_mode or not active_steps:
            return
        if self.pipeline_index < len(active_steps) - 1:
            self.pipeline_index += 1
        self._refresh_view(delta=None)

    def _on_anim_play(self):
        if not self.pipeline_mode or not self.pipeline_steps:
            return
        if self.pipeline_playing:
            return
        self.pipeline_playing = True
        self._anim_loop()

    def _anim_loop(self):
        if not self.pipeline_playing:
            return
        active_steps = self._get_active_pipeline_steps()
        if self.pipeline_index < len(active_steps) - 1:
            self.pipeline_index += 1
            self._refresh_view(delta=None)
            self.after(self.step_delay_ms.get(), self._anim_loop)
        else:
            self.pipeline_playing = False
            self._log("[Anim] Fin de animación")

    def _on_anim_pause(self):
        self.pipeline_playing = False

    def _on_anim_reset(self):
        self.pipeline_playing = False
        self.pipeline_index = 0
        if self.pipeline_mode and self._get_active_pipeline_steps():
            self._refresh_view(delta=None)
        self._log("[Anim] Reset índice a 0")

    # ---- Filtros y utilidades de presentación ----
    def _get_active_pipeline_steps(self):
        if self.pipeline_use_filtered and self.pipeline_filtered_steps:
            return self.pipeline_filtered_steps
        return self.pipeline_steps

    def _populate_stage_combo(self):
        if not self.pipeline_steps:
            self.combo_stage.configure(values=["(todas)"])
            self.combo_stage.current(0)
            return
        stages = []
        for s in self.pipeline_steps:
            if s.stage not in stages:
                stages.append(s.stage)
        self.combo_stage.configure(values=["(todas)"] + stages)
        self.combo_stage.current(0)

    def _update_stage_stats(self):
        counts = {}
        for s in self.pipeline_steps:
            counts[s.stage] = counts.get(s.stage, 0) + 1
        self.pipeline_stage_counts = counts
        parts = [f"{k}: {v}" for k, v in counts.items()]
        self.lbl_stage_stats.configure(text="Stats: " + (', '.join(parts) if parts else '-'))

    def _on_stage_apply(self):
        selected = self.combo_stage.get()
        if selected == "(todas)" or not selected:
            self.pipeline_use_filtered = False
            self.pipeline_filtered_steps = []
            self.pipeline_index = 0
            self._refresh_view(delta=None)
            self._log("[Filtro] Mostrando todas las etapas")
            return
        self.pipeline_filtered_steps = [s for s in self.pipeline_steps if s.stage == selected]
        self.pipeline_use_filtered = True
        self.pipeline_index = 0
        self._refresh_view(delta=None)
        self._log(f"[Filtro] Filtrada etapa '{selected}' con {len(self.pipeline_filtered_steps)} pasos")
        self.lbl_anim_info.configure(text=f"Filtro '{selected}' pasos: {len(self.pipeline_filtered_steps)}", foreground="blue")

    def _on_stage_clear(self):
        if not self.pipeline_use_filtered:
            return
        self.pipeline_use_filtered = False
        self.pipeline_filtered_steps = []
        self.pipeline_index = 0
        self._refresh_view(delta=None)
        self._log("[Filtro] Filtro eliminado")
        self.lbl_anim_info.configure(text=f"{len(self.pipeline_steps)} pasos (sin filtro)", foreground="green")

    def _on_export_pipeline(self):
        steps = self._get_active_pipeline_steps()
        if not steps:
            self._log("[Export] No hay pasos para exportar")
            return
        try:
            fn = filedialog.asksaveasfilename(title="Guardar trazas", defaultextension=".txt", filetypes=[("Texto", "*.txt")])
            if not fn:
                return
            with open(fn, 'w', encoding='utf-8') as f:
                for i, s in enumerate(steps):
                    delta_txt = f"delta={s.delta}" if s.delta else "delta=None"
                    f.write(f"#{i}\tstage={s.stage}\tstate={s.state}\thead={s.head}\t{delta_txt}\ttape={''.join(s.tape)}\n")
            self._log(f"[Export] Guardado archivo: {fn}")
        except Exception as e:
            self._log(f"[Export] Error: {e}")

    def _fill_example(self, mode: str):
        if mode == 'encrypt':
            self.entry_anim_w.delete(0, tk.END)
            self.entry_anim_w.insert(0, '3#ROMA')
            self.var_anim_mode.set('encrypt')
            self._log('[Ejemplo] Cargado ejemplo cifrado 3#ROMA')
        else:
            self.entry_anim_w.delete(0, tk.END)
            self.entry_anim_w.insert(0, '3#URPD')
            self.var_anim_mode.set('decrypt')
            self._log('[Ejemplo] Cargado ejemplo descifrado 3#URPD')

    # ---- Condensación y navegación ----
    def _on_condense_apply(self):
        base = self._get_active_pipeline_steps()
        if not base:
            return
        result = base
        if self.var_condense_boundaries.get():
            result = []
            prev_stage = None
            prev_step = None
            for s in base:
                if s.stage != prev_stage:
                    # inicio de etapa
                    result.append(s)
                    if prev_step is not None and prev_step is not result[-1]:
                        # fin de etapa anterior
                        if result[-1] is not prev_step:
                            result.append(prev_step)
                prev_stage = s.stage
                prev_step = s
            # añadir último fin de etapa
            if prev_step is not None and (not result or result[-1] is not prev_step):
                result.append(prev_step)
        # Muestreo cada N
        n = max(1, int(self.var_sample_n.get() or 1))
        if n > 1 and result:
            sampled = [result[i] for i in range(0, len(result), n)]
            if sampled[-1] is not result[-1]:
                sampled.append(result[-1])
            result = sampled
        self.pipeline_filtered_steps = result
        self.pipeline_use_filtered = True
        self.pipeline_index = 0
        self._refresh_view(delta=None)
        self.lbl_anim_info.configure(text=f"Condensado: {len(result)} pasos", foreground="blue")
        self._log(f"[Condensación] Lista reducida a {len(result)} pasos")

    def _on_condense_clear(self):
        if not self.pipeline_use_filtered:
            return
        # Si había un filtro previo de etapa, lo mantenemos: reaplicar filtro de etapa si no está en (todas)
        selected = self.combo_stage.get()
        self.pipeline_use_filtered = False
        self.pipeline_filtered_steps = []
        if selected and selected != "(todas)":
            # re-aplicar filtro de etapa sobre todos los pasos
            self.pipeline_filtered_steps = [s for s in self.pipeline_steps if s.stage == selected]
            self.pipeline_use_filtered = True
        self.pipeline_index = 0
        self._refresh_view(delta=None)
        self.lbl_anim_info.configure(text=f"{len(self._get_active_pipeline_steps())} pasos (sin condensación)", foreground="green")
        self._log("[Condensación] Eliminada")

    def _on_next_letter(self):
        steps = self._get_active_pipeline_steps()
        if not steps:
            return
        cur = steps[self.pipeline_index]
        import re
        m = re.match(r"^\[(\d+)\]", cur.stage)
        cur_idx = m.group(1) if m else None
        for i in range(self.pipeline_index + 1, len(steps)):
            s = steps[i]
            m2 = re.match(r"^\[(\d+)\]", s.stage)
            idx2 = m2.group(1) if m2 else None
            if idx2 is not None and idx2 != cur_idx:
                self.pipeline_index = i
                self._refresh_view(delta=None)
                self._log(f"[Navegación] Saltado a letra índice {idx2}")
                return

    # ---- Utilities for input validation and examples ----
    def _find_invalid_symbols(self, w: str) -> set[str]:
        if not self.cfg_input_alphabet:
            return set()  # si no conocemos Σ, no bloqueamos
        allowed = set(self.cfg_input_alphabet) | {self.cfg_blank or '_'}
        return {c for c in w if c not in allowed}

    def _extract_example(self, example_text: str | None, sigma: set[str]) -> str | None:
        if not example_text or not sigma:
            return None
        # Construir regex con símbolos de Σ y '_'
        # Escapar metacaracteres para clases de char
        esc = ''.join(re.escape(ch) for ch in sigma | {'_'})
        m = re.findall(rf"[{esc}]+", example_text)
        if not m:
            # Heurística rápida: casos típicos
            if '|' in sigma and '+' in sigma:
                return '||+|||'
            if 'A' in sigma:
                return 'AAA'
            return None
        # Elegir el match más largo
        return max(m, key=len)

    def _pretty_symbol(self, s: str) -> str:
        return '⊔' if s == '_' else s


def main():
    app = TMVisualizer()
    app.mainloop()


if __name__ == "__main__":
    main()
