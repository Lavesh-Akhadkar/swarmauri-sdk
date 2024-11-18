import pytest
from swarmauri_community.measurements.concrete.MutualInformationMeasurement import (
    MutualInformationMeasurement as Measurement,
)


@pytest.mark.unit
def test_ubc_resource():
    assert Measurement(value=10).resource == "Measurement"


@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement(value=10)
    assert measurement.type == "MutualInformationMeasurement"


@pytest.mark.unit
def test_serialization():
    measurement = Measurement(value=10)
    assert (
        measurement.id
        == Measurement.model_validate_json(measurement.model_dump_json()).id
    )


@pytest.mark.unit
def test_measurement_value():
    assert Measurement(value=10)() == 10


@pytest.mark.unit
def test_measurement_unit():
    assert Measurement(value=10).unit == "bits"