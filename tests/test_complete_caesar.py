"""
Suite completa de pruebas para el Cifrado César con Máquina de Turing
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from caesar_cipher_tm import CaesarCipherTM


def test_single_letters():
    """Prueba cifrado de letras individuales"""
    print("\n" + "="*70)
    print("TEST 1: Letras Individuales")
    print("="*70)
    
    cipher = CaesarCipherTM(shift=3, debug=False)
    
    test_cases = [
        ('A', 'D'),
        ('B', 'E'),
        ('X', 'A'),
        ('Y', 'B'),
        ('Z', 'C'),
    ]
    
    results = []
    for original, expected in test_cases:
        encrypted = cipher.encrypt(original)
        success = encrypted == expected
        results.append(success)
        
        status = "✓" if success else "✗"
        print(f"{status} {original} -> {encrypted} (esperado: {expected})")
    
    return all(results)


def test_words():
    """Prueba cifrado de palabras"""
    print("\n" + "="*70)
    print("TEST 2: Palabras")
    print("="*70)
    
    cipher = CaesarCipherTM(shift=3, debug=False)
    
    test_cases = [
        ('HOLA', 'KROD'),
        ('MUNDO', 'PXQGR'),
        ('PYTHON', 'SBWKRQ'),
        ('HELLO', 'KHOOR'),
        ('WORLD', 'ZRUOG'),
    ]
    
    results = []
    for original, expected in test_cases:
        encrypted = cipher.encrypt(original)
        success = encrypted == expected
        results.append(success)
        
        status = "✓" if success else "✗"
        print(f"{status} {original} -> {encrypted} (esperado: {expected})")
    
    return all(results)


def test_phrases():
    """Prueba cifrado de frases con espacios"""
    print("\n" + "="*70)
    print("TEST 3: Frases con Espacios")
    print("="*70)
    
    cipher = CaesarCipherTM(shift=3, debug=False)
    
    test_cases = [
        ('HELLO WORLD', 'KHOOR ZRUOG'),
        ('ABC XYZ', 'DEF ABC'),
        ('THE QUICK BROWN FOX', 'WKH TXLFN EURZQ IRA'),
    ]
    
    results = []
    for original, expected in test_cases:
        encrypted = cipher.encrypt(original)
        success = encrypted == expected
        results.append(success)
        
        status = "✓" if success else "✗"
        print(f"{status} '{original}'")
        print(f"   -> '{encrypted}'")
        print(f"   (esperado: '{expected}')")
    
    return all(results)


def test_roundtrip():
    """Prueba cifrado y descifrado (ida y vuelta)"""
    print("\n" + "="*70)
    print("TEST 4: Cifrado y Descifrado (Roundtrip)")
    print("="*70)
    
    cipher = CaesarCipherTM(shift=3, debug=False)
    
    test_cases = [
        'A',
        'Z',
        'HOLA',
        'HELLO WORLD',
        'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    ]
    
    results = []
    for original in test_cases:
        encrypted = cipher.encrypt(original)
        decrypted = cipher.decrypt(encrypted)
        success = original == decrypted
        results.append(success)
        
        status = "✓" if success else "✗"
        print(f"{status} '{original[:30]}{'...' if len(original) > 30 else ''}'")
        if not success:
            print(f"   Cifrado:    '{encrypted}'")
            print(f"   Descifrado: '{decrypted}'")
    
    return all(results)


def test_different_shifts():
    """Prueba con diferentes valores de shift"""
    print("\n" + "="*70)
    print("TEST 5: Diferentes Claves (Shift)")
    print("="*70)
    
    test_text = 'HELLO'
    expected_results = {
        1: 'IFMMP',
        5: 'MJQQT',
        10: 'ROVVY',
        13: 'URYYB',  # ROT13
        25: 'GDKKN',
    }
    
    results = []
    for shift, expected in expected_results.items():
        cipher = CaesarCipherTM(shift=shift, debug=False)
        encrypted = cipher.encrypt(test_text)
        success = encrypted == expected
        results.append(success)
        
        status = "✓" if success else "✗"
        print(f"{status} Shift {shift:2d}: {test_text} -> {encrypted} (esperado: {expected})")
    
    return all(results)


def test_mixed_case():
    """Prueba con mayúsculas y minúsculas mezcladas"""
    print("\n" + "="*70)
    print("TEST 6: Mayúsculas y Minúsculas")
    print("="*70)
    
    cipher = CaesarCipherTM(shift=3, debug=False)
    
    test_cases = [
        ('Hello', 'Khoor'),
        ('WoRlD', 'ZrUoG'),
        ('PyThOn', 'SbWkRq'),
    ]
    
    results = []
    for original, expected in test_cases:
        encrypted = cipher.encrypt(original)
        success = encrypted == expected
        results.append(success)
        
        status = "✓" if success else "✗"
        print(f"{status} {original} -> {encrypted} (esperado: {expected})")
    
    return all(results)


def test_edge_cases():
    """Prueba casos extremos"""
    print("\n" + "="*70)
    print("TEST 7: Casos Extremos")
    print("="*70)
    
    results = []
    
    # Caso 1: Texto vacío
    cipher = CaesarCipherTM(shift=3, debug=False)
    result = cipher.encrypt('')
    success = result == ''
    results.append(success)
    print(f"{'✓' if success else '✗'} Texto vacío")
    
    # Caso 2: Solo espacios
    result = cipher.encrypt('   ')
    success = result == '   '
    results.append(success)
    print(f"{'✓' if success else '✗'} Solo espacios")
    
    # Caso 3: Una sola letra
    result = cipher.encrypt('A')
    decrypted = cipher.decrypt(result)
    success = decrypted == 'A'
    results.append(success)
    print(f"{'✓' if success else '✗'} Una sola letra")
    
    # Caso 4: Texto largo
    long_text = 'A' * 50
    encrypted = cipher.encrypt(long_text)
    decrypted = cipher.decrypt(encrypted)
    success = decrypted == long_text
    results.append(success)
    print(f"{'✓' if success else '✗'} Texto largo (50 caracteres)")
    
    return all(results)


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "SUITE COMPLETA DE PRUEBAS" + " "*28 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Letras Individuales", test_single_letters),
        ("Palabras", test_words),
        ("Frases con Espacios", test_phrases),
        ("Cifrado y Descifrado", test_roundtrip),
        ("Diferentes Claves", test_different_shifts),
        ("Mayúsculas y Minúsculas", test_mixed_case),
        ("Casos Extremos", test_edge_cases),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error en {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron")
    
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
