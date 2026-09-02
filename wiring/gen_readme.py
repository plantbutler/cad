"""Render README.md from nets.py.

    uv run --with schemdraw --with matplotlib python gen_readme.py   (or: make readme)

Every table comes from nets.py; the prose here is the glue. Change a pin in
nets.py and both the drawings and this README follow. The drawings are the
PNGs draw.py writes next to this file.
"""

from __future__ import annotations

from pathlib import Path

import nets
from nets import md_list, md_table

HERE = Path(__file__).resolve().parent
OUT = HERE / "README.md"

RULES = [
    "Actuators (pump, servo) on their own supply with a common ground; neither ever draws from the "
    "board's 5 V pin (DECISIONS #7).",
    "The pump is OFF unless the MCU actively asserts PUMP_EN: an MCU in reset, a floating pin, a boot, "
    "an unpowered logic chip, the I2C expander's power-on state, an unplugged or dead float sensor and "
    "a lifted tank all mean pump off.",
    "The float is both in the driver circuit (74HC00 gate) and on a sense pin (D5).",
    "Failure direction is dry: NAS or WiFi down, unknown manifold position, float says empty -> no "
    "watering (DECISIONS #5). The backend decides when to water; the firmware only enforces caps.",
    "Firmware side of the bench: hall pulse counting on the lead screw plus a home hall (polled), flow "
    "sanity from the meter, sensors reported raw as (controller, channel) counts.",
    "12 V loop on a soldered perfboard with screw terminals and >= 0.5 mm2 wire; breadboard and "
    "Dupont only for 5 V logic.",
]

# What to look for on each drawing, one line each.
DRAWINGS: dict[str, str] = {
    "overview": "every used UNO pin labelled; orange (5V_BOARD) and brown (5V_SERVO) never meet and the "
                "UBEC output ends at the servo; the pump's purple return goes to the perfboard, not to a "
                "GND pin; the hydraulic strip along the bottom has the reservoir above the pump inlet.",
    "pump-driver": "follow the 12 V loop F1 -> PUMP+ -> pump -> PUMP- -> Q1 drain -> source -> star; "
                   "the only path to the gate is G3 through R1; R2 and R3 pull to GND, R4 pulls FLT_S "
                   "up; FLOAT_OK leaves G1 for both G2 and D5.",
    "sensor-bus": "P0-P3 -> S0-S3, EN to GND, C0-C4 moisture and C5 light, SIG -> A0; the I2C pull-ups "
                  "sit on the expander module; 100 nF at each chip; MUX2 and its select lines dashed "
                  "(later).",
    "power": "the two 5 V rails visibly apart; F1 and F2 in the + legs only; the pump return through the "
             "MOSFET to the star, never through the board's GND pin; a current next to every consumer.",
}


def image(stem: str) -> str:
    return f"![{stem}]({stem}.png)\n\n*{stem}.png* — {DRAWINGS[stem]}"


# ---------------------------------------------------------------- sections
def pin_map_rows() -> list[dict[str, str]]:
    rows = []
    for w in nets.pin_map():
        mid, mpin = w.other_end("UNO")
        rows.append({
            "pin": w.board_pin + (" (later)" if w.later else ""),
            "signal": w.signal,
            "module": nets.module_name(mid),
            "module_pin": mpin,
            "via": w.via,
            "connector": w.connector,
            "colour": w.colour,
            "cable": w.cable,
        })
    return rows


PIN_MAP_COLUMNS = [
    ("pin", "board pin"), ("signal", "signal"), ("module", "module"), ("module_pin", "module pin"),
    ("via", "series / pull"), ("connector", "connector"), ("colour", "wire colour"), ("cable", "cable / note"),
]


def all_wire_rows() -> list[dict[str, str]]:
    return [{
        "frm": w.frm, "frm_pin": w.frm_pin, "to": w.to, "to_pin": w.to_pin,
        "net": w.net, "colour": w.colour, "via": w.via, "connector": w.connector,
        "cable": w.cable, "when": "later" if w.later else "bench",
    } for w in nets.WIRES]


ALL_WIRE_COLUMNS = [
    ("frm", "from"), ("frm_pin", "pin"), ("to", "to"), ("to_pin", "pin"), ("net", "net"),
    ("colour", "colour"), ("via", "series / pull"), ("connector", "connector"),
    ("cable", "cable / note"), ("when", "when"),
]


def command_rows() -> list[dict[str, str]]:
    """Commands in code spans: `<ms>` outside one is an HTML tag to GitHub and vanishes."""
    return [{"command": f"`{c['command']}`", "does": c["does"]} for c in nets.BENCH_COMMANDS]


def modules_rows() -> list[dict[str, str]]:
    return [{"id": mid, "module": name, "status": status} for mid, (name, status) in nets.MODULES.items()]


def read_the_label() -> list[str]:
    """The parts whose label or a meter decides the wiring, from PARTS."""
    return [f"**{p['part']}** — {p['verify']}" for p in nets.PARTS
            if "READ THE" in p["verify"] or "on-board pull-up" in p["verify"]]


def gate_rows() -> list[dict[str, str]]:
    return [{"gate": g["gate"], "inputs": f"{g['a']}, {g['b']}", "output": g["y"],
             "pins": "A {}, B {}, Y {}".format(*g["pins"]), "role": g["role"]} for g in nets.GATES]


def render() -> str:
    bench = [w for w in nets.WIRES if not w.later]
    later = [w for w in nets.WIRES if w.later]
    parts = []
    add = parts.append

    add(f"<!-- generated by gen_readme.py from nets.py ({nets.DATE}); edit those, not this file -->")
    add(f"# Bench wiring: one manifold, five pots — {nets.DATE}\n")
    add("Wiring drawings and pin map to bench ONE manifold (5 outlets) with 5 soil-moisture sensors, the "
        "Sensor Kit temperature and light modules, an analog mux and an I2C expander (so more manifolds "
        "bolt on without rewiring), the pump with its driver and interlock, the inline flow meter, the "
        "float hall, the manifold's servo and its two halls. No PCB, no enclosure; KiCad comes once the "
        "bench has fixed the part choices. Source of truth: [`nets.py`](nets.py) (every wire, every "
        "table); the drawings and this file are generated from it.\n")
    add("## Binding rules\n")
    add("From the umbrella [DECISIONS.md](../../DECISIONS.md) #5 and #7 and the pitches \"Bench rig\" and "
        "\"Don't flood the flat\":\n")
    add(md_list(RULES) + "\n")
    add(image("overview") + "\n")

    # -- pin map
    add("## Pin map\n")
    add("Pins are inputs with pull-ups off at reset; D0/D1 stay free for serial; D6 is set LOW before it "
        "becomes an OUTPUT. `Wire` (A4/A5) is 5 V with no on-board pull-ups; the Qwiic connector is "
        "`Wire1` at 3.3 V and is not used.\n")
    add(md_table(pin_map_rows(), PIN_MAP_COLUMNS) + "\n")
    add("Free pins and what they are earmarked for:\n")
    add(md_table([{"pin": p, "use": u} for p, u in nets.BOARD_PINS_FREE], [("pin", "pin"), ("use", "use")]) + "\n")
    add("Per manifold (manifold 1 is the bench):\n")
    add(md_table(nets.MANIFOLD_PINS, [("manifold", "manifold"), ("servo", "servo PWM"), ("hall_screw", "screw hall"),
                                      ("hall_home", "home hall"), ("mux_sig", "mux SIG")]) + "\n")
    add(nets.MANIFOLD_NOTE + "\n")
    add(f"<details>\n<summary>Every wire: {len(nets.WIRES)} rows, {len(bench)} on the bench, "
        f"{len(later)} later (dashed on the drawings)</summary>\n")
    add("Module ids used below:\n")
    add(md_table(modules_rows(), [("id", "id"), ("module", "module"), ("status", "status")]) + "\n")
    add(md_table(all_wire_rows(), ALL_WIRE_COLUMNS) + "\n")
    add("</details>\n")

    # -- mux, expander, I2C
    add("## Mux, expander, I2C\n")
    add(image("sensor-bus") + "\n")
    add("### CD74HC4067 MUX1 channels (SIG -> A0, 14-bit)\n")
    add(md_table(nets.MUX_CHANNELS, [("channel", "channel"), ("source", "source"), ("signal", "signal"), ("note", "note")]) + "\n")
    add(md_list(nets.MUX_NOTES) + "\n")
    add("### PCF8575 pins (0x20)\n")
    add(md_table(nets.EXPANDER_PINS, [("pin", "pin"), ("use", "use"), ("note", "note")]) + "\n")
    add(md_list(nets.EXPANDER_NOTES) + "\n")
    add("### I2C addresses\n")
    add(md_table(nets.I2C_ADDRESSES, [("address", "address"), ("device", "device"), ("note", "note")]) + "\n")
    add(md_list(nets.I2C_NOTES) + "\n")

    # -- interlock
    add("## Pump driver and interlock (perfboard)\n")
    add("G1 inverts the float hall (LOW = magnet = water OK) into FLOAT_OK, which goes to D5 and to G2; "
        "G2 = NAND(PUMP_EN, FLOAT_OK); G3 inverts that into the MOSFET gate through R1. Every pull "
        "resistor pulls toward \"off\": R3 holds PUMP_EN low, R2 holds the gate low, R4 lifts an open "
        "float line to \"block\".\n")
    add(image("pump-driver") + "\n")
    add("### Terminals\n")
    add(md_table(nets.PERFBOARD_TERMINALS, [("terminal", "terminal"), ("wire", "wire"), ("net", "net"), ("gauge", "gauge")]) + "\n")
    add("### Parts on the perfboard\n")
    add(md_table(nets.INTERLOCK_PARTS, [("ref", "ref"), ("value", "value"), ("role", "role")]) + "\n")
    add("### 74HC00 gates (U1, DIP-14: VCC pin 14, GND pin 7)\n")
    add(md_table(gate_rows(), [("gate", "gate"), ("inputs", "inputs"), ("output", "output"), ("pins", "DIP pins"), ("role", "role")]) + "\n")
    add("### Truth table\n")
    add("Only the first row runs the pump.\n")
    add(md_table(nets.TRUTH_TABLE, [
        ("case", "case"), ("pump_en", "PUMP_EN (D6)"), ("magnet", "magnet"), ("float_module", "float module"),
        ("logic_5v", "5V_BOARD"), ("flt_s", "FLT_S"), ("float_ok", "FLOAT_OK (D5)"), ("gate", "gate"), ("pump", "pump"),
    ]) + "\n")
    add(md_list(nets.INTERLOCK_NOTES) + "\n")

    # -- parts
    add("## Parts list\n")
    add("ASSUME = ordered, exact model unknown until it arrives; VERIFY / READ THE LABEL = check before "
        "wiring; the drawings show these as labelled blocks.\n")
    add(md_table(nets.PARTS, [("part", "part"), ("qty", "qty"), ("status", "status"), ("verify", "verify")]) + "\n")
    add("### Read the label first\n")
    add("These decide a wire, a fuse or a library call, so they come before anything is plugged in:\n")
    add(md_list(read_the_label()) + "\n")

    # -- hydraulics
    add("## Hydraulic chain\n")
    add("The reservoir sits ABOVE the pump inlet so any pump type is gravity-primed; the flow meter is "
        "vertical with the flow upward. Tubing is the teal strip on the overview drawing.\n")
    add(md_table(nets.HYDRAULIC_CHAIN, [("stage", "stage"), ("detail", "detail")]) + "\n")

    # -- power
    add("## Power\n")
    add("Two 5 V rails, named and coloured apart: **5V_BOARD** (orange) is the UNO's 5 V pin, an output, "
        "feeding sensors and logic; **5V_SERVO** (brown) is the UBEC output and has exactly one "
        "destination, the servo's red lead. One GND star on the perfboard; the pump return reaches it "
        "through the MOSFET, never through the board's GND pin. Fuses sit in the + leg only, never in a "
        "return.\n")
    add(image("power") + "\n")
    add("### Budget\n")
    add(md_table(nets.POWER_BUDGET, [("rail", "rail"), ("consumer", "consumer"), ("current", "current"), ("note", "note")]) + "\n")
    add("### Fuses\n")
    add(md_table(nets.FUSES, [("ref", "ref"), ("value", "value"), ("branch", "branch"), ("leg", "leg")]) + "\n")
    add(nets.BENCH_POWER_ALT + "\n")
    add("### Never\n")
    add(md_list(nets.NEVER) + "\n")

    # -- bench commands
    add("## Bench command set\n")
    add("The bench firmware is a separate deliverable under the plan pitches \"Pump on command\" and "
        "\"Bench rig\"; it is not in this directory. This wiring assumes it provides these serial commands, "
        "which the bring-up below uses:\n")
    add(md_table(command_rows(), [("command", "command"), ("does", "does")]) + "\n")

    # -- bring-up
    add("## Bring-up order\n")
    add("In this order, each step proving one thing; the fail-dry proofs are 7a-7e. `pump` is refused "
        "while FLOAT_OK is LOW, so step 4 needs the magnet at the float hall.\n")
    add(md_table(nets.BRINGUP, [("step", "step"), ("do", "do"), ("proves", "proves")]) + "\n")

    # -- regenerate
    add("## Regenerate\n")
    add("```bash\nmake -C cad/wiring            # drawings (SVG + PNG at 150 dpi) and this README\n"
        "make -C cad/wiring drawings   # draw.py -> overview, pump-driver, sensor-bus, power\n"
        "make -C cad/wiring readme     # gen_readme.py -> README.md\n```\n")
    add("Needs `uv`; it fetches schemdraw and matplotlib into an ephemeral environment. Facts live in "
        "`nets.py`, the look in `style.py`, one `draw_*.py` per drawing.\n")

    return "\n".join(parts)


def main() -> None:
    OUT.write_text(render(), encoding="utf-8")
    print(OUT.name)


if __name__ == "__main__":
    main()
