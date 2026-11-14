"""Pruebas de escenarios."""

import pytest

from ipo.src.escenarios import ESCENARIOS, obtener_escenario


@pytest.mark.parametrize("nombre", ["optimista", "base", "pesimista"])
def test_escenarios_validos(nombre):
    config = obtener_escenario(nombre)
    assert config["nombre"] == nombre
    assert abs(sum(config["pesos_ventana"]) - 1.0) < 1e-9
    assert -1 < config["crecimiento_demanda"] < 1


def test_tres_escenarios():
    assert set(ESCENARIOS) == {"optimista", "base", "pesimista"}


def test_escenario_invalido():
    with pytest.raises(ValueError, match="Escenario inválido"):
        obtener_escenario("otro")
