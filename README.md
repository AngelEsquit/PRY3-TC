# PRY3-TC - Máquina de Turing para Cifrado César

## 📋 Descripción

Proyecto de Teoría de la Computación que implementa máquinas de Turing para encriptar y decriptar mensajes usando el cifrado César.

## 🎯 Objetivos

- Simular máquinas de Turing que respeten las operaciones básicas (cambiar estado, sustituir símbolo, moverse L/R)
- Implementar cifrado César: E(x) = (x + k) mod 26
- Implementar descifrado César: D(x) = (x - k) mod 26
- Realizar todas las operaciones aritméticas usando solo operaciones de MT

## 📥 Entrada

Formato: `k # MENSAJE`
- **k**: llave de cifrado (1-27 o letra A-Z)
- **#**: separador
- **MENSAJE**: texto en mayúsculas

**Ejemplo:** `3 # ROMA NO FUE CONSTRUIDA EN UN DIA.`

## 📤 Salida

- **Encripción:** `URPD QR IXH FRQVWUXLGD HQ XQ GLD.`
- **Decripción:** `ROMA NO FUE CONSTRUIDA EN UN DIA.`

## 📁 Estructura del Proyecto

```
PRY3-TC/
├── README.md               # Este archivo
├── Instrucciones.txt       # Especificaciones del proyecto
├── main.py                 # Programa principal interactivo
├── src/                    # Código fuente
│   ├── turing_machine.py
│   ├── caesar_cipher_tm.py
│   └── arithmetic_utils.py
├── config/                 # Configuración de las MT (JSON)
├── tests/                  # Suite de pruebas
└── tools/                  # Generadores de configuración
```

## 🚀 Estado del Proyecto

### ✅ **PROYECTO COMPLETADO** 

**Sistema funcional - Todas las pruebas pasando**
- ✅ Máquina de Turing base
- ✅ Operaciones aritméticas (suma, resta con marcas)
- ✅ Conversiones letra↔número
- ✅ Cifrado César completo
- ✅ Descifrado César completo
- ✅ 7/7 grupos de pruebas exitosos (40+ casos)

**Fecha:** 30 de octubre de 2025

## 💻 Uso

### Opción 1: Programa Interactivo
```bash
python main.py
```
Menú interactivo con opciones para cifrar, descifrar y configurar.

### Opción 2: Uso Programático
```python
from src.caesar_cipher_tm import CaesarCipherTM

# Crear cifrador con clave 3
cipher = CaesarCipherTM(shift=3)

# Cifrar mensaje
encrypted = cipher.encrypt("HOLA MUNDO")
print(encrypted)  # "KROD PXQGR"

# Descifrar
decrypted = cipher.decrypt(encrypted)
print(decrypted)  # "HOLA MUNDO"
```

## 🧪 Pruebas

```bash
# Suite completa de pruebas
python tests\test_complete_caesar.py

# Pruebas individuales
python tests\test_basic_tm.py
python tests\test_arithmetic.py
python tests\test_conversions.py
```

**Resultados:**
- ✓ Letras Individuales
- ✓ Palabras
- ✓ Frases con Espacios
- ✓ Cifrado y Descifrado
- ✓ Diferentes Claves
- ✓ Mayúsculas y Minúsculas
- ✓ Casos Extremos

**Total: 7/7 grupos exitosos** 🎉

## 🏗️ Arquitectura Modular

La implementación entregable usa un enfoque MODULAR (varias MT separadas) en lugar de una sola MT gigante. Cada operación del cifrado César se realiza por una MT independiente descrita en JSON, y el código Python solo coordina su ejecución (no hace aritmética ni transformaciones internas de símbolos). Esto respeta las restricciones de la especificación.

### Máquinas JSON Core (config/)
- `letter_to_number.json`: letra → marcas (A=0 marcas, B=1, ..., Z=25)
- `number_to_letter.json`: marcas → letra
- `add_simple.json`: suma en marcas (concatena y borra '+')
- `subtract_simple.json`: resta (para obtener desplazamiento inverso en descifrado)
- `mod26_full.json`: cálculo de n mod 26 eliminando bloques de 26
- `number_key_to_letter.json`: clave numérica 1..27 → letra (k % 26)

### Flujo Modular de Encripción
1. Clave w: si numérica → `number_key_to_letter.json` → letra; si letra se usa directamente.
2. Letra clave → marcas: `letter_to_number.json` (shift).
3. Para cada letra del mensaje:
	- Letra → marcas (`letter_to_number.json`)
	- Suma de marcas con shift (`add_simple.json`)
	- Reducción módulo 26 (`mod26_full.json`)
	- Marcas → letra cifrada (`number_to_letter.json`)

### Flujo Modular de Decripción
1. Clave w procesada igual que en cifrado.
2. (26 − k) mediante resta de marcas: construir 26 marcas y aplicar `subtract_simple.json` con k marcas.
3. Cada letra cifrada sigue el mismo pipeline de suma y mod usando el desplazamiento inverso.

### Razones para no usar la MT Unificada
Se intentó generar versiones unificadas (`caesar_encrypt_full.json`, `caesar_decrypt_full.json`) pero se mantienen fuera del entregable porque:
1. Generan cientos de estados/transiciones difíciles de verificar manualmente.
2. La versión prototipo no completó correctamente el cifrado (falla en pruebas).
3. La modular mantiene claridad, reutilización y pruebas unitarias con trazabilidad directa.

### Cumplimiento de Especificaciones
- Operaciones aritméticas y conversión realizadas exclusivamente con MTs.
- Entrada `w = clave#mensaje` procesada sin aritmética Python (la clave pasa por MTs).
- Dos máquinas de alto nivel (encriptar/descifrar) representadas por las clases `CaesarEncryptTM` y `CaesarDecryptTM` que orquestan únicamente MTs.

Para construir una MT unificada funcional en el futuro se puede extender el script prototipo (eliminado en esta versión) agregando transiciones de integración completa.

## 🎞️ Animación Paso a Paso del Cifrado César

La GUI (`python -m src.gui.app`) ahora incluye un panel "Animación Paso a Paso César" que permite visualizar cada transición aplicada dentro de cada máquina modular del pipeline.

### ¿Qué se anima?
Se registran y muestran todas las etapas:
- Procesamiento de la clave (número→letra, letra→marcas, resta 26 - k para descifrado)
- Para cada carácter alfabético del mensaje:
	- letra→marcas
	- suma con desplazamiento (o desplazamiento inverso)
	- reducción módulo 26
	- marcas→letra final

Cada transición de cada sub‑máquina genera un snapshot (cinta, posición del cabezal, estado y transición δ aplicada). Estos snapshots se reproducen en la interfaz.

### Uso Rápido
1. Ejecutar: `python -m src.gui.app`
2. Panel "Animación Paso a Paso César":
	 - Ingresar `w = clave#mensaje` (ej: `3#ABC` o `D#HOLA`)
	 - Seleccionar Encrypt o Decrypt.
	 - Pulsar "Generar pasos".
	 - Usar "Play" para animación continua o "Paso" para avanzar uno.
	 - "Reset" vuelve al primer snapshot.
3. El label de estado muestra: cantidad total de pasos y resultado final del cifrado/descifrado.

Nota: Mensajes largos generan muchos pasos (miles). Para demostraciones rápidas usar ejemplos cortos (`3#ABC`).

## 🖥️ Herramientas de Presentación en la GUI

El panel adicional "Herramientas de Presentación" facilita explicar el funcionamiento interno:

- Filtro de etapa: Permite seleccionar una etapa específica (p.ej. `"[2] suma marcas + shift"`) y reproducir solo esos pasos.
- Estadísticas: Muestra conteo de pasos por etapa para evidenciar complejidad relativa de cada fase (ej. mod26 suele ser la más larga).
- Exportar trazas: Genera un archivo `.txt` con todas las transiciones (estado, símbolo escrito, movimiento, cinta completa) para incluir en el informe técnico.
- Ejemplos rápidos: Botones para precargar `3#ROMA` (cifrado) y `3#URPD` (descifrado) para mostrar ciclo completo en pocos segundos.
- Visualización de δ: En modo animación se muestra la transición aplicada (δ) bajo la cinta junto con el estado y la etiqueta de etapa.
- Modo condensado: opción para mostrar solo inicios/finales de etapa y/o muestrear cada N pasos, reduciendo miles de pasos a decenas.
- Navegación por letra: botón “Siguiente letra” que salta al siguiente bloque de etapas del siguiente carácter del mensaje.

### Flujo Recomendado para la Presentación
1. Mostrar una sub‑MT aislada cargando un JSON (ej. `letter_to_number.json`). Ejecutar unos pasos manuales.
2. Cambiar al panel de Animación y generar pasos para `3#ROMA` (Encrypt). Explicar cada etapa usando el filtro y las estadísticas.
3. Exportar las trazas y comentar brevemente el volumen de pasos vs. simplicidad conceptual del algoritmo.
4. Repetir con `3#URPD` (Decrypt) destacando el uso de la resta `26 - k`.
5. Resaltar modularidad y cómo cada sub‑MT respeta el modelo clásico (solo estado, símbolo, movimiento).


