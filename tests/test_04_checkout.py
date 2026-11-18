"""Casos CP-07 y CP-08: proceso de compra."""
import pytest

from data.datos_prueba import CATALOGO, CHECKOUT_INCOMPLETO, CLIENTE, MSG_COMPRA_COMPLETA, TASA_IMPUESTO
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutCompletoPage, CheckoutInformacionPage, CheckoutResumenPage

pytestmark = pytest.mark.checkout

PRODUCTOS = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]


def _ir_al_checkout(inventario, driver, productos):
    for producto in productos:
        inventario.agregar_al_carrito(producto)
    inventario.ir_al_carrito()
    CartPage(driver).esperar_carga().ir_a_pagar()


@pytest.mark.caso("CP-07")
@pytest.mark.humo
def test_compra_completa_con_totales_correctos(sesion_iniciada, verificar, driver):
    """Compra completa con cálculo correcto de subtotal, impuesto y total."""
    # Valores esperados calculados a partir de los precios publicados
    subtotal = round(sum(CATALOGO[p] for p in PRODUCTOS), 2)
    impuesto = round(subtotal * TASA_IMPUESTO, 2)
    total = round(subtotal + impuesto, 2)

    _ir_al_checkout(sesion_iniciada, driver, PRODUCTOS)
    CheckoutInformacionPage(driver).completar(CLIENTE["nombre"], CLIENTE["apellido"], CLIENTE["codigo_postal"])
    resumen = CheckoutResumenPage(driver).esperar_carga()

    verificar("Productos en el resumen", sorted(PRODUCTOS), sorted(resumen.productos()))
    verificar("Subtotal (Item total)", subtotal, resumen.subtotal)
    verificar("Impuesto (8 %)", impuesto, resumen.impuesto)
    verificar("Total a pagar", total, resumen.total)

    resumen.finalizar()
    verificar("Mensaje de confirmación", MSG_COMPRA_COMPLETA, CheckoutCompletoPage(driver).encabezado)


@pytest.mark.caso("CP-08")
@pytest.mark.parametrize(
    "nombre, apellido, codigo_postal, mensaje_esperado",
    [caso[1:] for caso in CHECKOUT_INCOMPLETO],
    ids=[caso[0] for caso in CHECKOUT_INCOMPLETO],
)
def test_datos_de_envio_obligatorios(sesion_iniciada, verificar, driver, nombre, apellido, codigo_postal, mensaje_esperado):
    """Validación de campos obligatorios en los datos del comprador."""
    _ir_al_checkout(sesion_iniciada, driver, PRODUCTOS[:1])
    formulario = CheckoutInformacionPage(driver)
    formulario.completar(nombre, apellido, codigo_postal)
    verificar("Mensaje de error", mensaje_esperado, formulario.mensaje_error)
    verificar("Permanece en el formulario", True, formulario.url_actual.endswith(CheckoutInformacionPage.RUTA))
