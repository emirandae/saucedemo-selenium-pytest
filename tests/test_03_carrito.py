"""Caso CP-06: carrito de compras."""
import pytest

from pages.cart_page import CartPage

pytestmark = pytest.mark.carrito

PRODUCTOS = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]


@pytest.mark.caso("CP-06")
@pytest.mark.humo
def test_agregar_y_quitar_productos(sesion_iniciada, verificar, driver):
    """Agregar y quitar productos actualiza el contador y el contenido del carrito."""
    inventario = sesion_iniciada
    verificar("Contador inicial del carrito", 0, inventario.cantidad_en_carrito())

    for producto in PRODUCTOS:
        inventario.agregar_al_carrito(producto)
    verificar("Contador tras agregar 2 productos", 2, inventario.cantidad_en_carrito())

    inventario.ir_al_carrito()
    carrito = CartPage(driver).esperar_carga()
    verificar("Productos en el carrito", sorted(PRODUCTOS), sorted(carrito.productos()))

    carrito.seguir_comprando()
    inventario.esperar_carga()
    inventario.quitar_del_carrito(PRODUCTOS[1])
    verificar("Contador tras quitar 1 producto", 1, inventario.cantidad_en_carrito())

    inventario.ir_al_carrito()
    verificar("Productos restantes en el carrito", [PRODUCTOS[0]], CartPage(driver).esperar_carga().productos())
