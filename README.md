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

## 🏗️ Arquitectura

El sistema está compuesto por múltiples Máquinas de Turing especializadas:

1. **TuringMachine** (clase base): Motor genérico de MT
2. **Suma**: Concatenación de marcas (`||+|||` → `|||||`)
3. **Resta**: Eliminación de marcas (`|||||−||` → `|||`)
4. **Letra→Número**: Convierte letras a marcas (H → `||||||||`)
5. **Número→Letra**: Convierte marcas a letras (`||||||||` → H)
6. **CaesarCipherTM**: Orquesta todas las MTs para cifrado completo

Todas las operaciones respetan las restricciones de MT puras (solo lectura/escritura/movimiento/cambio de estado).

