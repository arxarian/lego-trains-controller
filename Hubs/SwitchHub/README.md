# SwitchHub

Pybricks CityHub firmware for a single turnout actuator.

- Reports role `switch` after `int` (see [`../README.md`](../README.md)).
- Motor on **Port A** (`DCMotor`): short DC pulse for position `A` vs `B`.
- Host command `pos` + `A`/`B`; hub echoes `pos` + letter after the pulse.

Tune `MOTOR_DC` and `PULSE_MS` in `main.py` for your mechanical setup.
