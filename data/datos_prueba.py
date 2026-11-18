"""Datos de prueba y datos de referencia (oráculo) para SauceDemo.

Los usuarios y la contraseña son las credenciales públicas de prueba que
SauceDemo muestra en su propia página de inicio de sesión.
"""
import os

URL_BASE = os.getenv("SAUCE_URL", "https://www.saucedemo.com").rstrip("/")

CONTRASENA = "secret_sauce"
USUARIO_ESTANDAR = "standard_user"
USUARIO_BLOQUEADO = "locked_out_user"
USUARIO_PROBLEMA = "problem_user"

# Catálogo de referencia: nombre y precio (USD) de los 6 productos publicados.
CATALOGO = {
    "Sauce Labs Backpack": 29.99,
    "Sauce Labs Bike Light": 9.99,
    "Sauce Labs Bolt T-Shirt": 15.99,
    "Sauce Labs Fleece Jacket": 49.99,
    "Sauce Labs Onesie": 7.99,
    "Test.allTheThings() T-Shirt (Red)": 15.99,
}

TASA_IMPUESTO = 0.08  # impuesto aplicado en el resumen de compra

# Mensajes esperados
MSG_CREDENCIALES = "Epic sadface: Username and password do not match any user in this service"
MSG_USUARIO_REQUERIDO = "Epic sadface: Username is required"
MSG_CONTRASENA_REQUERIDA = "Epic sadface: Password is required"
MSG_BLOQUEADO = "Epic sadface: Sorry, this user has been locked out."
MSG_ACCESO_SIN_SESION = "Epic sadface: You can only access '/inventory.html' when you are logged in."
MSG_COMPRA_COMPLETA = "Thank you for your order!"

# Clases de equivalencia no válidas para el inicio de sesión (CP-02):
# (identificador, usuario, contraseña, mensaje esperado)
LOGIN_INVALIDO = [
    ("contrasena_incorrecta", USUARIO_ESTANDAR, "clave_incorrecta", MSG_CREDENCIALES),
    ("usuario_inexistente", "usuario_qa", CONTRASENA, MSG_CREDENCIALES),
    ("usuario_vacio", "", CONTRASENA, MSG_USUARIO_REQUERIDO),
    ("contrasena_vacia", USUARIO_ESTANDAR, "", MSG_CONTRASENA_REQUERIDA),
]

# Opciones de ordenamiento (CP-05): valor del selector y criterio esperado
ORDENAMIENTOS = {
    "az": ("nombre", False),
    "za": ("nombre", True),
    "lohi": ("precio", False),
    "hilo": ("precio", True),
}

# Datos del formulario de compra (CP-07 y CP-08)
CLIENTE = {"nombre": "Ana", "apellido": "Pérez", "codigo_postal": "10101"}
CHECKOUT_INCOMPLETO = [
    ("sin_nombre", "", "Pérez", "10101", "Error: First Name is required"),
    ("sin_apellido", "Ana", "", "10101", "Error: Last Name is required"),
    ("sin_codigo_postal", "Ana", "Pérez", "", "Error: Postal Code is required"),
]
