"""Casos CP-04 y CP-05: catálogo de productos."""
import pytest

from data.datos_prueba import (
    CATALOGO,
    CONTRASENA,
    ORDENAMIENTOS,
    USUARIO_ESTANDAR,
    USUARIO_PROBLEMA,
)
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

pytestmark = pytest.mark.catalogo

# Combinaciones de usuario y criterio de orden. El usuario «problem_user» se incluye
# para comprobar que la prueba detecta un comportamiento defectuoso.
COMBINACIONES = [(USUARIO_ESTANDAR, opcion) for opcion in ORDENAMIENTOS] + [(USUARIO_PROBLEMA, "lohi")]


@pytest.mark.caso("CP-04")
@pytest.mark.humo
def test_catalogo_coincide_con_datos_publicados(sesion_iniciada, verificar):
    """Nombres y precios del catálogo coinciden con los datos de referencia."""
    obtenido = sesion_iniciada.catalogo()
    verificar("Cantidad de productos", len(CATALOGO), len(obtenido))
    for nombre, precio in CATALOGO.items():
        verificar(f"Precio de «{nombre}»", precio, obtenido.get(nombre))


@pytest.mark.caso("CP-05")
@pytest.mark.parametrize("usuario, opcion", COMBINACIONES, ids=[f"{u}-{o}" for u, o in COMBINACIONES])
def test_ordenamiento_de_productos(driver, verificar, usuario, opcion):
    """Ordenamiento del catálogo por nombre y por precio."""
    LoginPage(driver).abrir().iniciar_sesion(usuario, CONTRASENA)
    inventario = InventoryPage(driver).esperar_carga()
    criterio, descendente = ORDENAMIENTOS[opcion]

    inventario.ordenar_por(opcion)

    if criterio == "nombre":
        obtenido = inventario.nombres()
    else:
        obtenido = inventario.precios()
    esperado = sorted(obtenido, reverse=descendente)
    verificar(f"Lista ordenada por {criterio} ({opcion})", esperado, obtenido)
