import pytest
from astronaut import Astronaut


def fresh() -> Astronaut:
    """Return a baseline astronaut ready for each test."""
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
def test_eva_rest_drift_1min():
    a = fresh()
    # run one minute of rest
    a.eva_rest_drift_1min()

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
def test_eva_work_normal_1min():
    a = fresh()
    a.eva_work_normal_1min()

    assert a.mission_elapsed_time == 1
    assert a.heart_rate       == 74     # +4
    assert a.respiration_rate == 13      # +1
    assert a.metabolic_rate   == 95     # 80 + 15
    assert a.blood_co2_pa     == pytest.approx(41.0)
    assert a.oxygen_saturation == pytest.approx(0.977)
    assert a.core_temp        == pytest.approx(37.01)
    assert a.skin_temp        == pytest.approx(33.02)
    assert a.glucose_level    == pytest.approx(89.8)
    assert a.muscle_fatigue   == pytest.approx(0.004)


# ------------------------------------------------------------------
# eva_work_hard_1min
# ------------------------------------------------------------------
def test_eva_work_hard_1min():
    a = fresh()
    a.eva_work_hard_1min()

    assert a.mission_elapsed_time == 1
    assert a.heart_rate       == 88      # +18
    assert a.respiration_rate == 17      # 12 + 5
    assert a.metabolic_rate   == 130     # 80 + 50
    assert a.blood_co2_pa     == pytest.approx(43.5)
    assert a.oxygen_saturation == pytest.approx(0.972)
    assert a.core_temp        == pytest.approx(37.03)
    assert a.skin_temp        == pytest.approx(33.06)
    assert a.glucose_level    == pytest.approx(89.9)
    assert a.muscle_fatigue   == pytest.approx(0.01)


def test_eva_work_low_1min():
    a = Astronaut()
    a.eva_work_low_1min()
    assert a.heart_rate == 72
    assert a.glucose_level < Astronaut._BASELINE["glucose_level"]

def test_eva_task_cognitive_1min():
    a = Astronaut()
    a.eva_task_cognitive_1min()
    assert a.cognitive_load > Astronaut._BASELINE["cognitive_load"]
    assert a.metabolic_rate > Astronaut._BASELINE["metabolic_rate"]

