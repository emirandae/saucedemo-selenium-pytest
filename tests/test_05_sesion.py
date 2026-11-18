"""Caso CP-09: cierre de sesión y protección de rutas."""
import pytest

from data.datos_prueba import MSG_ACCESO_SIN_SESION
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

pytestmark = pytest.mark.sesion


@pytest.mark.caso("CP-09")
def test_cierre_de_sesion_protege_el_catalogo(sesion_iniciada, verificar, driver):
    """Cierre de sesión y bloqueo del catálogo sin autenticación."""
    sesion_iniciada.cerrar_sesion()
    login = LoginPage(driver)
    login.encontrar(LoginPage.BOTON_INGRESAR)
    verificar("Regresa a la página de inicio de sesión", True, login.esta_visible())

    # Intento de acceso directo a una ruta protegida después de cerrar la sesión
    InventoryPage(driver).abrir()
    verificar("Mensaje al acceder sin sesión", MSG_ACCESO_SIN_SESION, login.mensaje_error)
    verificar("No muestra el catálogo", False, login.existe(InventoryPage.PRODUCTOS))
