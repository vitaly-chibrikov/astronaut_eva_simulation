# ------------------------------------------------------------------
# > pytest
# ------------------------------------------------------------------

import pytest
from astronaut import Astronaut


def fresh() -> Astronaut:
    """Return a baseline astronaut ready for each test."""
    Astronaut.init() 
    return Astronaut()


# ------------------------------------------------------------------
# reset_to_rest
# ------------------------------------------------------------------
def test_reset_to_rest():
    a = fresh()
    a.heart_rate = 150
    a.core_temp = 38.5
    a.muscle_fatigue = 0.4

    a.reset_to_rest()

    for key, baseline_val in Astronaut._BASELINE.items():
        assert getattr(a, key) == pytest.approx(baseline_val)
    # anthropometrics and mission time unchanged
    assert a.mission_elapsed_time == 0.0


# ------------------------------------------------------------------
# eva_rest_drift_1min
# ------------------------------------------------------------------
def test_eva_rest_drift():
    a = fresh()
    # run one minute of rest
    a.eva_rest_drift(1)

    # Values that should remain at baseline (cannot go lower)
    assert a.heart_rate        == Astronaut._BASELINE["heart_rate"]
    assert a.respiration_rate  == Astronaut._BASELINE["respiration_rate"]
    # Values that recover upward
    assert a.sweat_rate         == Astronaut._BASELINE["sweat_rate"]
    assert a.skin_temp          == Astronaut._BASELINE["skin_temp"]
    # Values that accumulate
    assert a.muscle_fatigue     > Astronaut._BASELINE["muscle_fatigue"]
    # Mission clock advanced
    assert a.mission_elapsed_time == 1


# ------------------------------------------------------------------
# eva_work_normal_1min
# ------------------------------------------------------------------
def test_eva_work_normal():
    a = fresh()
    a.eva_work_normal(1)

    assert a.mission_elapsed_time == 1
    assert a.heart_rate       == 75     
    assert a.respiration_rate == 13.2     
    assert a.metabolic_rate   > 80     
    assert a.blood_co2_pa     == pytest.approx(39.866666667)
    assert a.oxygen_saturation == pytest.approx(97.9)
    assert a.core_temp        == pytest.approx(37.005555556)
    assert a.skin_temp        == pytest.approx(33.033333333)
    assert a.glucose_level    == pytest.approx(89.861111111)
    assert a.muscle_fatigue   == pytest.approx(0.1)


# ------------------------------------------------------------------
# eva_work_hard_1min
# ------------------------------------------------------------------
def test_eva_work_hard():
    a = fresh()
    a.eva_work_hard(1)

    assert a.mission_elapsed_time == 1
    assert a.heart_rate       == 79     
    assert a.respiration_rate == 13.8      
    assert a.metabolic_rate   == 85.333333333    
    assert a.blood_co2_pa     == pytest.approx(40.5)
    assert a.oxygen_saturation == pytest.approx(97.866666667)
    assert a.core_temp        == pytest.approx(37.011111111)
    assert a.skin_temp        == pytest.approx(33.05)
    assert a.glucose_level    == pytest.approx(89.833333333)
    assert a.muscle_fatigue   == pytest.approx(0.5)


def test_eva_work_low():
    a = Astronaut()
    a.eva_work_low(1)
    assert a.heart_rate == 72
    assert a.glucose_level < Astronaut._BASELINE["glucose_level"]

def test_eva_task_cognitive():
    a = Astronaut()
    a.eva_task_cognitive(1)
    assert a.cognitive_load > Astronaut._BASELINE["cognitive_load"]
    assert a.metabolic_rate > Astronaut._BASELINE["metabolic_rate"]

