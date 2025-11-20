## Simulador Universal de Máquinas de Turing (Una Cinta)

Este repositorio contiene una implementación **desde cero** de un simulador universal
para Máquinas de Turing de una sola cinta. Toda la lógica se define exclusivamente
mediante archivos JSON; el código Python NO implementa operaciones de negocio
(cifrado, aritmética, etc.).

## 🎯 Características Principales

### 1. Simulador Universal
- Ejecuta cualquier MT definida en JSON
- Cinta infinita con expansión dinámica
- Sin lógica de negocio en Python (pureza total)

### 2. Cifrado César por Orquestación
- Implementación completa usando **solo** Máquinas de Turing
- Pipeline: `letter→number` → `add/subtract` → `mod26` → `number→letter`
- Sin aritmética en Python, todo mediante MTs

### 3. Interfaz Gráfica (GUI)
- Visualización animada de la cinta y cabezal
- Simulación paso a paso de todo el proceso de cifrado
- Controles de navegación (play, pausa, paso anterior/siguiente)

---

## 📁 Estructura del Proyecto

```
PRY3-TC/
├── src/
│   ├── turing_simulator.py      # Simulador universal de MT
│   ├── orchestrator.py           # Orquestador de cifrado César
│   └── gui/
│       └── caesar_gui.py         # Interfaz gráfica
├── config/
│   ├── test_simple.json          # Ejemplo: A→B
│   ├── add_simple.json           # Suma unaria
│   ├── subtract_simple.json      # Resta unaria
│   ├── letter_to_number.json     # Letra → marcas unarias
│   ├── number_to_letter.json     # Marcas → letra
│   └── mod26_full.json           # Módulo 26
├── tests/                        # Suite de pruebas
├── main.py                       # CLI para ejecutar MTs
└── README.md

```

---

## 🚀 Uso

### Opción 1: Interfaz Gráfica (Recomendado)

Ejecuta la aplicación gráfica para cifrado César con visualización:

```bash
python src/gui/caesar_gui.py
```

#### Características de la GUI:

**Panel de Entrada:**
- Formato: `clave#texto` (ejemplo: `3#ROMA`)
- La clave es un número 0-25 (desplazamiento César)
- Botones: 🔒 Encriptar | 🔓 Desencriptar

**Visualización de la Cinta:**
- Canvas animado mostrando la cinta de la MT
- Cabezal visual (▼ HEAD) indicando posición actual
- Símbolos especiales: ⊔ para blancos

**Controles de Navegación:**
- ⏮ **Inicio**: Primer paso de la simulación
- ◀ **Anterior**: Retrocede un paso
- ▶ **Play**: Reproducción automática
- ⏸ **Pausa**: Detiene la reproducción
- **Siguiente** ▶: Avanza un paso
- ⏭ **Fin**: Último paso
- **Control de velocidad**: Ajusta milisegundos entre pasos

**Información en Tiempo Real:**
- Máquina actual ejecutándose (ej: `letter_to_number.json`)
- Estado de la MT (ej: `q_17`)
- Paso actual / total de pasos

#### Ejemplo de Uso:

1. Ejecuta `python src/gui/caesar_gui.py`
2. Ingresa: `3#ROMA`
3. Haz clic en **🔒 Encriptar**
4. Observa cómo la simulación procesa cada etapa:
   - Convierte 'R' a marcas unarias
   - Suma el desplazamiento (3)
   - Aplica módulo 26
   - Convierte de vuelta a letra ('U')
5. Usa los controles para navegar paso a paso

---

### Opción 2: Línea de Comandos (CLI)

Ejecuta cualquier Máquina de Turing definida en JSON:

```bash
python main.py --config config/test_simple.json --input AAA
```

**Parámetros:**
- `--config`: Ruta al archivo JSON de configuración
- `--input`: Cadena de entrada para la cinta
- `--max-steps`: Máximo de pasos (default: 10000)

**Ejemplos:**

```bash
# Ejemplo 1: Reemplazar A por B
python main.py --config config/test_simple.json --input AAA

# Ejemplo 2: Suma unaria (2+3=5)
python main.py --config config/add_simple.json --input "||+|||"

# Ejemplo 3: Convertir letra a número
python main.py --config config/letter_to_number.json --input "H"
```

---

### Opción 3: Orquestador de César (Programático)

Usa directamente el orquestador en Python:

```python
from src.orchestrator import encrypt_text, decrypt_text

# Encriptar
cifrado = encrypt_text('D', 'HOLA')  # Shift de 3 (D = 3)
print(cifrado)  # KROD

# Desencriptar
descifrado = decrypt_text('D', 'KROD')
print(descifrado)  # HOLA
```

---

## 📋 Estructura JSON de las Máquinas de Turing

```json
{
  "states": ["q0", "q1", "q_accept"],
  "input_alphabet": ["A", "B"],
  "tape_alphabet": ["A", "B", "_"],
  "initial_state": "q0",
  "accept_states": ["q_accept"],
  "blank_symbol": "_",
  "transitions": [
    {
      "current_state": "q0",
      "read_symbol": "A",
      "next_state": "q0",
      "write_symbol": "B",
      "move": "R"
    }
  ]
}
```

**Campos:**
- `states`: Lista de estados
- `input_alphabet`: Símbolos de entrada válidos
- `tape_alphabet`: Todos los símbolos (entrada + trabajo + blanco)
- `initial_state`: Estado inicial
- `accept_states`: Estados de aceptación
- `blank_symbol`: Símbolo que representa espacio vacío
- `transitions`: Lista de transiciones δ(q, s) → (q', s', m)
  - `move`: "L" (izquierda), "R" (derecha), "N" (sin mover)

---

## 🧪 Pruebas

Ejecuta la suite completa de tests:

```bash
pytest
```

O tests específicos:

```bash
# Tests básicos del simulador
pytest tests/test_universal_basic.py -v

# Tests del pipeline César
pytest tests/test_caesar_pipeline.py -v
```

**Tests incluidos:**
- Reemplazo de símbolos (A→B)
- Suma unaria
- Entrada vacía
- Límite de pasos
- Cifrado César básico
- Wrap-around (Z+1→A)
- Preservación de no-letras

---

## 🔐 Cifrado César: Pipeline de Máquinas de Turing

El cifrado César se implementa orquestando múltiples MTs:

### Encriptación: `encrypt_text(key, text)`

Para cada letra:
1. **letter_to_number.json**: Convierte letra a marcas unarias
   - Ejemplo: 'R' → `|||||||||||||||||` (17 marcas)
2. **letter_to_number.json**: Convierte clave a marcas
   - Ejemplo: 'D' (shift 3) → `|||` (3 marcas)
3. **add_simple.json**: Suma las marcas
   - `|||||||||||||||||` + `|||` = `||||||||||||||||||||` (20 marcas)
4. **subtract_simple.json**: Aplica módulo 26 (si ≥26)
   - Resta 26 iterativamente hasta <26
5. **number_to_letter.json**: Convierte marcas a letra
   - 20 marcas → 'U'

### Desencriptación: `decrypt_text(key, text)`

Similar, pero usando shift inverso (26 - key):
1. Convierte letra cifrada a marcas
2. Calcula shift inverso: 26 - shift usando `subtract_simple.json`
3. Suma letra + shift_inverso
4. Aplica mod26
5. Convierte a letra original

---

## 🎓 Principios de Diseño

### 1. Pureza Computacional
- **Zero lógica de negocio en Python**
- Todo el cifrado/aritmética definido en JSONs
- Python solo orquesta la ejecución

### 2. Simulador Universal
- Lee cualquier MT válida en JSON
- No interpreta semántica
- Ejecuta transiciones mecánicamente

### 3. Búsqueda de Transiciones
- Orden estricto: primera coincidencia se aplica
- Sin optimizaciones ni atajos
- Implementación fiel al modelo teórico

### 4. Cinta Infinita
- Expansión dinámica en ambas direcciones
- Sin límites artificiales
- Blancos automáticos al expandir

---

## 📦 Configuraciones Incluidas

| Archivo | Descripción | Ejemplo |
|---------|-------------|---------|
| `test_simple.json` | Reemplaza A→B hasta blanco | `AAA` → `BBB` |
| `add_simple.json` | Suma unaria | `\|\|+\|\|\|` → `\|\|\|\|\|` |
| `subtract_simple.json` | Resta unaria | `\|\|\|\|\|-\|\|` → `\|\|\|` |
| `letter_to_number.json` | Letra → marcas (A=0, B=1...) | `H` → `\|\|\|\|\|\|\|` |
| `number_to_letter.json` | Marcas → letra | `\|\|\|\|\|\|\|` → `H` |
| `mod26_full.json` | Módulo 26 (batch-erase) | 30 marcas → 4 marcas |

---

## 🛠️ Requisitos

- Python 3.8+
- pytest (para tests)
- tkinter (para GUI, incluido en Python estándar)

Instalación:
```bash
pip install -r requirements.txt
```

---

## 📸 Capturas de la GUI

La interfaz muestra:
- **Cinta visual** con celdas coloreadas
- **Cabezal animado** en rojo
- **Indicadores de estado** (máquina, estado, paso)
- **Controles intuitivos** de navegación
- **Log detallado** de cada etapa
- **Resultado final** del cifrado/descifrado

---

## 🤝 Contribuciones

Este es un proyecto académico. Las configuraciones JSON pueden mejorarse o
extenderse siguiendo el mismo principio: **lógica solo en transiciones**.

---

## 📝 Licencia

Proyecto educativo - Teoría de la Computación (2025)

---

## 👨‍💻 Autor

Proyecto desarrollado como demostración de Máquinas de Turing universales
y cifrado César mediante orquestación pura de MTs.
