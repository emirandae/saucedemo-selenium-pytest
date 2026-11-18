from pages.base_page import BasePage, data_test


class LoginPage(BasePage):
    RUTA = "/"
    USUARIO = data_test("username")
    CONTRASENA = data_test("password")
    BOTON_INGRESAR = data_test("login-button")
    MENSAJE_ERROR = data_test("error")

    def iniciar_sesion(self, usuario: str, contrasena: str):
        self.escribir(self.USUARIO, usuario)
        self.escribir(self.CONTRASENA, contrasena)
        self.clic(self.BOTON_INGRESAR)

    @property
    def mensaje_error(self) -> str:
        return self.texto(self.MENSAJE_ERROR)

    def esta_visible(self) -> bool:
        return self.existe(self.BOTON_INGRESAR)
