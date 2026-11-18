# Pruebas automatizadas de SauceDemo con Selenium WebDriver y pytest

Proyecto de automatización de pruebas funcionales del sitio de demostración
[SauceDemo](https://www.saucedemo.com), publicado por Sauce Labs para practicar
pruebas de software. Implementa 9 casos de prueba (18 ejecuciones gracias a la
parametrización) con **Selenium WebDriver 4**, **pytest** y el patrón **Page Object Model**.

## Tecnologías

| Herramienta | Uso |
|---|---|
| Python 3.10+ | Lenguaje de las pruebas |
| Selenium WebDriver 4 | Automatización del navegador (Selenium Manager descarga el driver) |
| pytest | Ejecución, fixtures, parametrización y marcadores |
| pytest-html | Reporte HTML con capturas de pantalla |
| Git | Control de versiones del código |
| openpyxl | Matriz de casos de prueba en Excel |

## Estructura

```
saucedemo-selenium-pytest/
├── conftest.py            # fixtures (driver, sesión, verificar) y ganchos de reporte
├── pytest.ini             # configuración de pytest y marcadores
├── requirements.txt       # dependencias
├── run_tests.bat          # ejecución en Windows con un doble clic
├── data/datos_prueba.py   # datos de prueba y oráculo (catálogo, mensajes, impuesto)
├── pages/                 # Page Objects
│   ├── base_page.py       # esperas explícitas y acciones comunes
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── tests/                 # casos de prueba CP-01 a CP-09
├── utils/
│   ├── driver_factory.py  # fábrica de navegadores (Chrome, Edge, Firefox)
│   └── matriz_casos.py    # genera la matriz de casos con los resultados
└── docs/casos_de_prueba.xlsx  # matriz de gestión de casos de prueba
```

## Patrones de diseño aplicados

- **Page Object Model (POM):** cada página tiene una clase con sus localizadores y acciones;
  las pruebas no contienen selectores.
- **Clase base (BasePage):** centraliza esperas explícitas (`WebDriverWait`) y acciones comunes.
- **Factory:** `crear_driver()` crea Chrome, Edge o Firefox según el parámetro `--browser`.
- **Pruebas guiadas por datos:** `@pytest.mark.parametrize` con datos en `data/datos_prueba.py`.
- **Preparar–Actuar–Afirmar (AAA)** y **fixtures** para precondiciones y limpieza.

## Casos de prueba

| ID | Caso | Ejecuciones |
|---|---|---|
| CP-01 | Inicio de sesión exitoso con el usuario estándar | 1 |
| CP-02 | Rechazo de credenciales inválidas o incompletas | 4 |
| CP-03 | Bloqueo de acceso para un usuario inhabilitado | 1 |
| CP-04 | Nombres y precios del catálogo coinciden con los datos de referencia | 1 |
| CP-05 | Ordenamiento del catálogo por nombre y por precio | 5 |
| CP-06 | Agregar y quitar productos del carrito | 1 |
| CP-07 | Compra completa con cálculo de subtotal, impuesto y total | 1 |
| CP-08 | Validación de campos obligatorios del comprador | 3 |
| CP-09 | Cierre de sesión y bloqueo del catálogo sin autenticación | 1 |

La ejecución `CP-05 [problem_user-lohi]` usa el usuario que SauceDemo publica con fallas
intencionales; se espera que **falle** y así demuestra que la prueba detecta el defecto.

## Ejecución

**Windows (doble clic):** `run_tests.bat`. Crea el entorno virtual, instala dependencias,
ejecuta las pruebas y abre el reporte.

**Manual (cualquier sistema):**

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  |  source .venv/bin/activate  (Linux/macOS)
pip install -r requirements.txt
pytest                           # Chrome con interfaz
pytest --browser edge            # otro navegador
pytest --headless -m humo        # solo pruebas de humo, sin interfaz
```

## Resultados

Cada ejecución genera en `reports/`:

- `reporte.html`: reporte con estado, verificaciones (esperado vs. obtenido) y captura por prueba.
- `resultados.json` y `resultados.csv`: resultados estructurados para el informe.
- `junit.xml`: formato estándar para herramientas de integración continua.
- `capturas/`: evidencia en imagen de cada prueba.

Para actualizar la matriz de casos de prueba con la última ejecución:

```bash
python -m utils.matriz_casos     # genera docs/casos_de_prueba.xlsx
```

## Control de versiones

El historial se lleva con Git usando mensajes de commit con el formato *Conventional Commits*
(`feat:`, `test:`, `docs:`, `chore:`).

```bash
git log --oneline --graph      # ver historial
```

Para registrar el historial con su propio nombre y publicarlo en GitHub:

```bash
git config user.name "Su Nombre"
git config user.email "su_correo@ejemplo.com"
git rebase -r --root --exec "git commit --amend --no-edit --reset-author"
git remote add origin https://github.com/<usuario>/saucedemo-selenium-pytest.git
git push -u origin main
```
