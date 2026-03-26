"""Shared pytest fixtures for TestEquity 123H verification suite."""

import pytest
from models.heating import HeatingModel
from models.cooling import CoolingModel
from models.humidity import HumidityModel
from models.uniformity import UniformityModel
from models.chamber_system import ChamberSystem
from models.reliability import ReliabilityModel
import config


@pytest.fixture(scope="session")
def chamber():
    return ChamberSystem()

@pytest.fixture(scope="session")
def heating():
    return HeatingModel()

@pytest.fixture(scope="session")
def cooling():
    return CoolingModel()

@pytest.fixture(scope="session")
def humidity():
    return HumidityModel()

@pytest.fixture(scope="session")
def uniformity():
    return UniformityModel()

@pytest.fixture(scope="session")
def reliability():
    return ReliabilityModel()


_results: dict[int, dict] = {}

def record_result(req_id: int, measured: float, passed: bool):
    _results[req_id] = {
        "measured": measured,
        "passed": passed,
        "requirement": config.REQUIREMENTS[req_id]["name"],
        "threshold": config.REQUIREMENTS[req_id]["threshold"],
        "unit": config.REQUIREMENTS[req_id]["unit"],
    }

def get_results() -> dict[int, dict]:
    return dict(_results)
