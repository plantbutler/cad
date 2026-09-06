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
    "The pump never touches a 5 V rail: 12 V through relay contacts, its return straight to the star "
    "(DECISIONS #7). The servo does run off the board's 5 V, which the R4's buck can carry — see Power.",
    "The pump is OFF unless the MCU actively asserts D6: an MCU in reset, a floating pin, a boot, an "
    "unpowered relay coil, a pulled jumper and a lost 12 V all mean pump off, in hardware.",
    "The float is a sense pin only (D5). There is no hardware interlock on this bench: read THE GAP "
    "under Pump driver before trusting the tank to a sketch.",
    "Failure direction is dry: NAS or WiFi down, unknown manifold position, float says empty -> no "
    "watering (DECISIONS #5). The backend decides when to water; the firmware only enforces caps.",
    "Firmware side of the bench: hall pulse counting on the lead screw plus a home hall (polled), flow "
    "sanity from the meter, sensors reported raw as (controller, channel) counts.",
    "12 V loop on a soldered perfboard with screw terminals and >= 0.5 mm2 wire; breadboard and "
    "Dupont only for 5 V logic.",
]

# What to look for on each drawing, one line each.
DRAWINGS: dict[str, str] = {
    "overview": "every used UNO pin labelled; one orange 5 V rail, and the pump's purple leg is 12 V out "
                "of the relay, never a GND; the screw hall and the flow meter land on interrupt pins while "
                "the home hall goes through the expander; the hydraulic strip along the bottom has the "
                "reservoir above the pump inlet.",
    "pump-driver": "follow the 12 V loop brick -> F1 -> COM -> NO -> pump + -> pump - -> star, and note "
                   "that it crosses no board pin; D6 reaches only the relay's IN, with R1 holding the OFF "
                   "level; the float hall goes straight to D5 with R2, through no gate.",
    "sensor-bus": "P0-P3 -> S0-S3, EN to GND, C0-C4 moisture and C5 light, SIG -> A0; the I2C pull-ups "
                  "sit on the expander module; 100 nF at each chip; MUX2 and its select lines dashed "
                  "(later). The two screens share this SDA/SCL pair: they are in the address table, not "
                  "drawn as blocks.",
    "power": "one 5 V rail out of the board's buck, with the servo on its own pair and C1 at its plug; F1 "
             "and F2 in the + legs only; the pump's return reaching the star without passing a board pin; "
             "a current next to every consumer and the 1.05 A ceiling stated.",
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
    return [{"command": f"`{c['command']}`", "binary": c["binary"], "does": c["does"]}
            for c in nets.BENCH_COMMANDS]


def modules_rows() -> list[dict[str, str]]:
    return [{"id": mid, "module": name, "status": status} for mid, (name, status) in nets.MODULES.items()]


def read_the_label() -> list[str]:
    """The parts whose label or a meter decides the wiring, from PARTS."""
    return [f"**{p['part']}** — {p['verify']}" for p in nets.PARTS
            if "READ THE" in p["verify"] or "on-board pull-up" in p["verify"]]


def render() -> str:
    bench = [w for w in nets.WIRES if not w.later]
    later = [w for w in nets.WIRES if w.later]
    parts = []
    add = parts.append

    add(f"<!-- generated by gen_readme.py from nets.py ({nets.DATE}); edit those, not this file -->")
    add(f"# Bench wiring: one manifold, five pots — {nets.DATE}\n")
    add("Wiring drawings and pin map to bench ONE manifold (5 outlets) with 5 soil-moisture sensors, the "
        "Sensor Kit temperature and light modules, two I2C screens (OLED 0x3C, LCD1602 backpack 0x27), an "
        "analog mux and an I2C expander (so more manifolds "
        "bolt on without rewiring), the pump with its relay, the inline flow meter, the float hall, the "
        "manifold's servo and its screw and home halls. No PCB, no enclosure; KiCad comes once the "
        "bench has fixed the part choices. Source of truth: [`nets.py`](nets.py) (every wire, every "
        "table); the drawings and this file are generated from it.\n")
    add("## Binding rules\n")
    add("From the umbrella [DECISIONS.md](../../DECISIONS.md) #5 and #7 and the pitches \"Bench rig\" and "
        "\"Don't flood the flat\":\n")
    add(md_list(RULES) + "\n")
    add(image("overview") + "\n")

    # -- pin map
    add("## Pin map\n")
    add("Pins are inputs with pull-ups off at reset; D0/D1 stay free for serial; D6 gets its direction "
        "and the relay's OFF level in one PFS register write, because `pinMode(D6, OUTPUT)` on this "
        "core drives the pin LOW and would discard a level set before it (see the relay notes). "
        "`Wire` (A4/A5) is 5 V with no on-board pull-ups and carries the expander and both screens; "
        "the Qwiic connector is `Wire1` at 3.3 V and is not used.\n")
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
    add("## Pump driver and interlock\n")
    add("A bought relay module switches the 12 V + leg: COM comes from the brick through F1, NO goes to "
        "the pump, and the pump's return goes straight to the star. D6 drives the module's IN through "
        "nothing but a wire and R1, which holds the OFF level whenever D6 is not an asserted output. The "
        "float hall reaches D5 directly, with R2 lifting an open line to the \"not OK\" level.\n")
    add(image("pump-driver") + "\n")
    add("### Power board terminals\n")
    add(md_table(nets.PERFBOARD_TERMINALS, [("terminal", "terminal"), ("wire", "wire"), ("net", "net"), ("gauge", "gauge")]) + "\n")
    add("### Relay module terminals\n")
    add(md_table(nets.RELAY_TERMINALS, [("terminal", "terminal"), ("wire", "wire"), ("net", "net"), ("gauge", "gauge")]) + "\n")
    add(md_list(nets.RELAY_NOTES) + "\n")
    add("### Parts\n")
    add(md_table(nets.INTERLOCK_PARTS, [("ref", "ref"), ("value", "value"), ("role", "role")]) + "\n")
    add("### What stops the pump, and what holds it there\n")
    add("Read the last column. Rows marked *hardware* hold whatever the sketch does; rows marked "
        "*FIRMWARE* are only as good as the code, which is the price of building this from parts in hand.\n")
    add(md_table(nets.TRUTH_TABLE, [
        ("case", "case"), ("d6", "D6"), ("float", "float"), ("pump", "pump"), ("held_by", "held by"),
    ]) + "\n")
    add(md_list(nets.INTERLOCK_NOTES) + "\n")
    add("### Where the float sits, and why it decides the failure direction\n")
    add("The mechanics choose the sense, and the sense chooses whether a dead sensor reads as permission. "
        "The wiring is identical either way; what differs is whether the float's travel is capped by a "
        "stop at the trip level.\n")
    add("```\n" + "\n".join(nets.FLOAT_SKETCH) + "\n```\n")
    add(md_table(nets.FLOAT_MOUNTING) + "\n")
    add(md_list(nets.FLOAT_NOTES) + "\n")

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
    add("One 5 V rail: **5V_BOARD** (orange), the UNO's own 5 V pin, an output and never fed from "
        "outside. It carries the sensors, the relay coil and the servo, because the R4's ISL854102 buck "
        "gives 1.2 A total from VIN where the R3's linear regulator could not - so the board must be fed "
        "from the barrel jack, not a USB port, once the servo moves. The servo takes its own pair from "
        "the rail's feed point with C1 (470-1000 uF) at its plug, and returns to the star rather than to "
        "the sensor ground. One GND star on the power board; the pump's 12 V return reaches it without "
        "passing a board pin. Fuses sit in the + leg only, never in a return.\n")
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
        "which the bring-up below uses. The commands that can move the cart or start the pump live only "
        "in the bring-up binary; the one left running unattended has no console path to D6:\n")
    add(md_table(command_rows(), [("command", "command"), ("binary", "binary"), ("does", "does")]) + "\n")

    # -- bring-up
    add("## Bring-up order\n")
    add("In this order, each step proving one thing. Steps 4a-4c exercise the relay dry, with no 12 V on "
        "COM and nothing plumbed, because that is the cheapest moment to discover the module's input "
        "polarity. Step 7c proves the watchdog, which on this bench is the only thing between a hung "
        "sketch and a running pump. Step 7e swaps the bring-up binary for the unattended one before the "
        "48-hour run, and checks that the pump commands went with it.\n")
    add(nets.BRINGUP_NOTE + "\n")
    add(md_table(nets.BRINGUP, [("step", "step"), ("do", "do"), ("proves", "proves")]) + "\n")

    # -- running
    add("## Running the bench\n")
    add("Three things to know during the 48-hour run that `status` cannot tell you. They are "
        "requirements of the firmware spec (2.7, 2.9, 15.2), not advice, and the firmware's "
        "`AGENTS.md` carries the same three rules:\n")
    add(md_list(nets.RUNNING_NOTES) + "\n")

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
