# Working on the hardware

Not started as a repository (2026-08-30); the manifold exists physically and nowhere else. Read
the umbrella's [AGENTS.md](https://github.com/plantbutler/plantbutler/blob/main/AGENTS.md) and
[DECISIONS.md](https://github.com/plantbutler/plantbutler/blob/main/DECISIONS.md) first; decision
#7 (safety) is the one this repository has to make physically true.

## What goes here

OpenSCAD sources (and the STLs they came from, if a part was printed from a file you only have as
STL), a KiCad schematic of the wiring, the bill of materials, and bench notes with the numbers
measured. Installed on the Mac: OpenSCAD 2021.01, KiCad, FreeCAD (do not use it here),
BambuStudio and Cura.

The hardware today: one reservoir and pump (never yet driven from software), a
continuous-rotation servo turning a rotary manifold with five outputs, one hose per pot, one
uncoated capacitive soil sensor per pot on the board's analog pins. Expect it to evolve; the
solenoid-valve alternative is a note in the plan.

## Pitches, in order (titles in the plan)

1. **Bench rig** — pump, a driver that is off unless the MCU asserts it, the pump's own supply
   with a common ground, a one-litre reservoir and a float switch, driven from a serial command.
   Deliverables: ml/s per output; verdicts on whether the manifold seals, its head, the servo's
   torque and whether the rotor has a hard stop; the KiCad schematic; the BOM. The servo and the
   pump never draw from the board's 5 V pin.
2. **Sensor stakes and sealing** — seal the sensor edges, print stakes that fix each sensor's
   depth, before the NAS starts storing history that matters.
3. **Manifold and mounts in OpenSCAD** — only after "Manifold that knows where it is" (firmware)
   has said whether the mechanism or the indexing is the problem. Parametric only where a
   dimension is known to change.

Not in scope: a PCB, a flow meter, an enclosure, a redesign of the mechanism, positional-servo
or stepper conversions.

## Bench rules

Actuators on their own supply; failure direction is dry; a reservoir small enough that a full
dump is a mop-up; the float switch is both in the driver circuit and on a sense pin. Write every
number you measure into `bench-notes.md` with the date.
