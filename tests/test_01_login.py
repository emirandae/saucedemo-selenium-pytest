"""Casos CP-01 a CP-03: autenticación."""
import pytest

from data.datos_prueba import (
    CATALOGO,
    CONTRASENA,
    LOGIN_INVALIDO,
    MSG_BLOQUEADO,
    USUARIO_BLOQUEADO,
    USUARIO_ESTANDAR,
)
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

pytestmark = pytest.mark.login


@pytest.mark.caso("CP-01")
@pytest.mark.humo
def test_inicio_sesion_exitoso(driver, verificar):
    """Inicio de sesión exitoso con el usuario estándar."""
    # Preparar
    login = LoginPage(driver).abrir()
    # Actuar
    login.iniciar_sesion(USUARIO_ESTANDAR, CONTRASENA)
    inventario = InventoryPage(driver).esperar_carga()
    # Afirmar
    verificar("Ruta después del inicio de sesión", True, inventario.url_actual.endswith("/inventory.html"))
    verificar("Título de la página", "Products", inventario.titulo)
    verificar("Cantidad de productos visibles", len(CATALOGO), inventario.cantidad_productos())


@pytest.mark.caso("CP-02")
@pytest.mark.parametrize(
    "usuario, contrasena, mensaje_esperado",
    [caso[1:] for caso in LOGIN_INVALIDO],
    ids=[caso[0] for caso in LOGIN_INVALIDO],
)
def test_inicio_sesion_invalido(driver, verificar, usuario, contrasena, mensaje_esperado):
    """Rechazo de credenciales inválidas o incompletas."""
    login = LoginPage(driver).abrir()
    login.iniciar_sesion(usuario, contrasena)
    verificar("Mensaje de error", mensaje_esperado, login.mensaje_error)
    verificar("Permanece en la página de inicio de sesión", True, login.esta_visible())


@pytest.mark.caso("CP-03")
def test_usuario_bloqueado(driver, verificar):
    """Bloqueo de acceso para un usuario inhabilitado."""
    login = LoginPage(driver).abrir()
    login.iniciar_sesion(USUARIO_BLOQUEADO, CONTRASENA)
    verificar("Mensaje de error", MSG_BLOQUEADO, login.mensaje_error)
    verificar("No accede al catálogo", False, "inventory.html" in login.url_actual)
