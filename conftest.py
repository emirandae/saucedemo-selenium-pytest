"""Configuración compartida de pytest.

- Fixture ``driver``: crea un navegador nuevo por prueba (aislamiento) y lo cierra al final.
- Fixture ``sesion_iniciada``: deja la aplicación en el catálogo con el usuario estándar.
- Fixture ``verificar``: compara el resultado esperado con el obtenido, lo registra y lo afirma.
- Ganchos de reporte: captura de pantalla por prueba, columna «Caso» en el reporte HTML
  y exportación de resultados a JSON y CSV para el informe de pruebas.
"""
import csv
import json
import platform
import re
import sys
from datetime import datetime
from pathlib import Path

import pytest
import selenium

from data.datos_prueba import CONTRASENA, URL_BASE, USUARIO_ESTANDAR
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.driver_factory import crear_driver

RAIZ = Path(__file__).parent
REPORTES = RAIZ / "reports"
CAPTURAS = REPORTES / "capturas"

ESTADOS = {"passed": "Aprobada", "failed": "Fallida", "skipped": "Omitida"}


# --------------------------------------------------------------------------- opciones
def pytest_addoption(parser):
    parser.addoption("--browser", default="chrome", help="chrome | edge | firefox")
    parser.addoption("--headless", action="store_true", help="ejecutar sin interfaz gráfica")


def pytest_configure(config):
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    config._resultados = []
    config._entorno = {
        "inicio": datetime.now().isoformat(timespec="seconds"),
        "url_base": URL_BASE,
        "navegador": config.getoption("--browser"),
        "modo": "headless" if config.getoption("--headless") else "con interfaz",
        "selenium": selenium.__version__,
        "pytest": pytest.__version__,
        "python": platform.python_version(),
        "sistema_operativo": f"{platform.system()} {platform.release()}",
    }
    # Datos del entorno que se muestran en la sección «Environment» del reporte HTML
    try:
        from pytest_metadata.plugin import metadata_key

        metadatos = config.stash[metadata_key]
        metadatos.pop("JAVA_HOME", None)
        metadatos["Sitio bajo prueba"] = URL_BASE
        metadatos["Navegador"] = config._entorno["navegador"] + f" ({config._entorno['modo']})"
        metadatos["Selenium"] = selenium.__version__
    except (ImportError, KeyError):
        pass


# --------------------------------------------------------------------------- fixtures
@pytest.fixture
def driver(request):
    navegador = request.config.getoption("--browser")
    driver = crear_driver(navegador, request.config.getoption("--headless"))
    request.config._entorno.setdefault(
        "version_navegador", driver.capabilities.get("browserVersion", "")
    )
    yield driver
    driver.quit()


@pytest.fixture
def sesion_iniciada(driver):
    """Precondición común: usuario estándar autenticado en el catálogo."""
    LoginPage(driver).abrir().iniciar_sesion(USUARIO_ESTANDAR, CONTRASENA)
    return InventoryPage(driver).esperar_carga()


def _formato(valor):
    if isinstance(valor, float):
        return f"{valor:.2f}"
    if isinstance(valor, (list, tuple)):
        return " | ".join(_formato(v) for v in valor)
    if isinstance(valor, dict):
        return " | ".join(f"{k}: {_formato(v)}" for k, v in valor.items())
    return str(valor)


@pytest.fixture
def verificar(request):
    """Compara esperado contra obtenido, deja el registro en el reporte y afirma la igualdad."""

    def _verificar(descripcion, esperado, obtenido):
        cumple = esperado == obtenido
        request.node.user_properties.append(
            (
                "verificacion",
                {
                    "descripcion": descripcion,
                    "esperado": _formato(esperado),
                    "obtenido": _formato(obtenido),
                    "cumple": cumple,
                },
            )
        )
        assert cumple, f"{descripcion}: se esperaba «{_formato(esperado)}» y se obtuvo «{_formato(obtenido)}»"

    return _verificar


# --------------------------------------------------------------------------- reporte
def _caso(item):
    marca = item.get_closest_marker("caso")
    return marca.args[0] if marca else ""


def _titulo(item):
    doc = (item.function.__doc__ or "").strip().splitlines()
    return doc[0].strip() if doc else item.name


def _nombre_archivo(item):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{_caso(item)}_{item.name}").strip("_")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    resultado = yield
    reporte = resultado.get_result()
    reporte.caso = _caso(item)
    if reporte.when == "setup":
        item._duracion_preparacion = reporte.duration  # incluye abrir el navegador e iniciar sesión

    fase_principal = reporte.when == "call" or (reporte.when == "setup" and not reporte.passed)
    if not fase_principal:
        return

    plugin_html = item.config.pluginmanager.getplugin("html")
    extras = getattr(reporte, "extras", [])
    captura = ""

    driver = item.funcargs.get("driver") if hasattr(item, "funcargs") else None
    if driver is not None:
        try:
            ruta = CAPTURAS / f"{_nombre_archivo(item)}.png"
            driver.save_screenshot(str(ruta))
            captura = ruta.relative_to(REPORTES).as_posix()
            if plugin_html:
                extras.append(plugin_html.extras.png(driver.get_screenshot_as_base64(), "Captura"))
        except Exception:  # la captura nunca debe ocultar el resultado real
            pass

    verificaciones = [v for k, v in item.user_properties if k == "verificacion"]
    if plugin_html and verificaciones:
        filas = "".join(
            f"<tr><td>{v['descripcion']}</td><td>{v['esperado']}</td><td>{v['obtenido']}</td>"
            f"<td>{'Cumple' if v['cumple'] else 'No cumple'}</td></tr>"
            for v in verificaciones
        )
        extras.append(
            plugin_html.extras.html(
                "<table border='1' cellpadding='4'><tr><th>Verificación</th><th>Esperado</th>"
                f"<th>Obtenido</th><th>Resultado</th></tr>{filas}</table>"
            )
        )
    reporte.extras = extras

    duracion = reporte.duration
    if reporte.when == "call":
        duracion += getattr(item, "_duracion_preparacion", 0)

    mensaje = ""
    if reporte.failed and call.excinfo is not None:
        mensaje = str(call.excinfo.value).splitlines()[0][:300]

    item.config._resultados.append(
        {
            "caso": reporte.caso,
            "titulo": _titulo(item),
            "prueba": item.name,
            "resultado": ESTADOS.get(reporte.outcome, reporte.outcome),
            "duracion_s": round(duracion, 2),
            "verificaciones": verificaciones,
            "captura": captura,
            "mensaje": mensaje,
        }
    )


def pytest_html_report_title(report):
    report.title = "Reporte de ejecución de pruebas automatizadas – SauceDemo"


def pytest_html_results_table_header(cells):
    cells.insert(1, "<th>Caso</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(1, f"<td>{getattr(report, 'caso', '')}</td>")


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    if not hasattr(config, "_resultados"):
        return
    config._entorno["fin"] = datetime.now().isoformat(timespec="seconds")
    resultados = config._resultados
    resumen = {estado: sum(r["resultado"] == estado for r in resultados) for estado in ESTADOS.values()}
    resumen["total"] = len(resultados)

    REPORTES.mkdir(exist_ok=True)
    with open(REPORTES / "resultados.json", "w", encoding="utf-8") as archivo:
        json.dump(
            {"entorno": config._entorno, "resumen": resumen, "resultados": resultados},
            archivo,
            ensure_ascii=False,
            indent=2,
        )

    with open(REPORTES / "resultados.csv", "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        escritor.writerow(["Caso", "Prueba", "Resultado", "Duración (s)", "Verificación", "Esperado", "Obtenido", "Cumple"])
        for r in resultados:
            for v in r["verificaciones"] or [{"descripcion": r["mensaje"], "esperado": "", "obtenido": "", "cumple": ""}]:
                escritor.writerow(
                    [r["caso"], r["prueba"], r["resultado"], r["duracion_s"], v["descripcion"], v["esperado"], v["obtenido"],
                     {True: "Sí", False: "No"}.get(v["cumple"], "")]
                )
