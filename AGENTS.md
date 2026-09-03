# Working on the hardware

Read the umbrella's [AGENTS.md](https://github.com/plantbutler/plantbutler/blob/main/AGENTS.md)
(on this machine: `~/projects/plant-butler/AGENTS.md`) and
[DECISIONS.md](https://github.com/plantbutler/plantbutler/blob/main/DECISIONS.md) first; decision
#7 (safety) is the one this repository has to make physically true, #8 says why everything here
is OpenSCAD.

## What is here (2026-09-02)

- `manifold/` — the watering manifold, parametric OpenSCAD 2021.01: `params.scad` (every
  parameter and every derived number, guarded by asserts), `lib/` (shapes, barb, O-ring,
  involute gear), `parts/` (ten printed parts), `assembly.scad` (everything in place with
  ghosts of the hardware, six section views), `Makefile` (`make stl png check report`),
  `README.md` (the parameters, the gate derivation, what to measure on the bench, assembly and
  sealing, print orientations), `renders/`, `reference/valveV2.{FCStd,step}` (the FreeCAD
  design it reproduces; read-only). Start with the README.
- `wiring/` — the bench wiring: `nets.py` (every wire and every table: the one source of
  truth), `style.py`, four `draw_*.py` (overview, pump switching, sensor bus, power)
  rendered by `draw.py` to SVG and PNG, `gen_readme.py` which writes `README.md` from `nets.py`,
  and a `Makefile` (`make`, `drawings`, `readme`, `clean`). Change a fact in `nets.py`, never in
  the generated README. Needs `uv` (it fetches schemdraw and matplotlib).
- Nothing else yet: the KiCad schematic, the BOM, the sensor stakes and `bench-notes.md` come
  with their pitches. KiCad comes after the bench has fixed the part choices.

Installed on the Mac: OpenSCAD 2021.01 at `/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD`
(the Makefile's default), KiCad, FreeCAD 1.1 (only to read `reference/`; `freecadcmd` scripts
can dump geometry headless), BambuStudio and Cura. The printer is a Bambu Lab P2S, 0.4 nozzle.

## How to work on the CAD

- Every dimension is an expression of `params.scad`; a number typed in a part file is a bug
  unless it is an epsilon or 45°. New behaviour = new parameter with a comment saying why.
- Each part file has `<part>()` in the assembly frame (X across, Y up, Z along, servo end at
  −Z), `<part>_print()` flat on z = 0 for export, `<part>_size()`, and the
  `if (is_undef(ASSEMBLY))` guard. `-D for_print=true` exports it; `-D name=value` overrides a
  parameter on a part file (not on the assembly: it `use`s the parts, `make check` copies the
  tree instead).
- Before saying a change is done: `make check` (defaults and the alternate parameter sets),
  `make stl` (every part one solid: `Simple: yes`, `Volumes: 2`), `make png`, and LOOK at the
  renders, sections included. A part must print with one flat face on the bed and no supports.
- The mechanism is decided (lead screw, magnet cart, 8 mm 440C ball on an O-ring seat, gears
  outboard of the servo plate, bonded lid and caps): re-source it, do not redesign it. What the
  bench must measure before the numbers are trusted is in `manifold/README.md`.

## Pitches, in order (titles in the plan)

1. **Manifold in OpenSCAD with ball gates** — `manifold/`, done.
2. **Bench wiring drawings** — `wiring/`, done: the pin map, what switches the pump, the power
   scheme and the bring-up order that the bench rig follows. Revised 2026-09-03 to the parts
   actually in hand: a relay module instead of a MOSFET and a 74HC00, no UBEC (the R4's buck
   carries the servo), the home hall on the I2C expander.
3. **Bench rig** — pump, a relay that is open unless the MCU asserts it, a one-litre reservoir
   and a float whose travel a stop caps at the trip level, driven from a serial command.
   Deliverables: ml/s per output; verdicts on whether the manifold seals, its head, the servo's
   torque and whether the threadless start of the screw holds as home; the KiCad schematic; the
   BOM. The servo and the pump never draw from the board's 5 V pin.
4. **Sensor stakes and sealing** — seal the sensor edges, print stakes that fix each sensor's
   depth, before the NAS starts storing history that matters.

Not in scope: a PCB, a flow meter, an enclosure, positional-servo or stepper conversions, the
solenoid-valve alternative (a note in the plan).

## Bench rules

The pump never touches a 5 V rail; failure direction is dry; a reservoir small enough that a
full dump is a mop-up. The float is mounted so that ALLOW is the active state - a stop caps the
float's travel at the trip level and the hall sits at that stop, so magnet present means water
above the line and every sensor failure reads as refuse.

There is no hardware interlock on this bench: the relay opens on reset, on lost power and with
the jumper pulled, but nothing in hardware ANDs "firmware says pump" with "the tank has water".
Three firmware things stand in for it and all three are mandatory - the RA4M1 IWDT enabled, a
hard maximum run time in the same code path that asserts D6, and a no-flow abort from the
meter. Pitch 4 ("Don't flood the flat") puts the gate back when the parts arrive.

Write every number you measure into `bench-notes.md` with the date.
