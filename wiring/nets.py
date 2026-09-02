"""One source of truth for the bench wiring: modules, every wire, tables, parts.

The drawings (draw_*.py) and the README (gen_readme.py) are both generated
from this file, so a pin changes here and nowhere else. Facts come from the
wiring brief (2026-09-02) and umbrella DECISIONS.md #5 and #7. Nothing in
here is firmware: the bench command set is a requirement on the bench sketch.

Net names (and their colours, see style.COLOURS): 12V, 5V_BOARD, 5V_SERVO,
GND, SIGNAL, I2C, PUMP_SW (the pump's switched return: NOT ground).
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Iterable, Sequence

DATE = "2026-09-02"

# Physical wire colour per net: what to reach for on the bench.
COLOUR_NAMES: dict[str, str] = {
    "12V": "red",
    "5V_BOARD": "orange",
    "5V_SERVO": "brown",
    "GND": "black",
    "SIGNAL": "blue",
    "I2C": "green",
    "PUMP_SW": "purple",  # or black with red tape: 12 V switched return, not GND
}

# ---------------------------------------------------------------- modules
# id -> (name on the drawings, status). Status: in hand | ASSUME (ordered,
# exact model unknown) | bench (rail, star point, perfboard we build).
MODULES: dict[str, tuple[str, str]] = {
    "UNO": ("Arduino UNO R4 WiFi", "in hand"),
    "PCF8575": ("PCF8575 I2C expander 0x20", "in hand"),
    "MUX1": ("CD74HC4067 mux MUX1", "in hand"),
    "MUX2": ("CD74HC4067 mux MUX2 (later)", "later"),
    "MOIST1": ("moisture 1 (capacitive)", "in hand"),
    "MOIST2": ("moisture 2 (capacitive)", "in hand"),
    "MOIST3": ("moisture 3 (capacitive)", "in hand"),
    "MOIST4": ("moisture 4 (capacitive)", "in hand"),
    "MOIST5": ("moisture 5 (capacitive)", "in hand"),
    "LDR": ("Sensor Kit light (LDR)", "in hand"),
    "DHT": ("Sensor Kit temp/humidity (DHT11)", "in hand"),
    "SERVO": ("SG90 continuous servo", "in hand"),
    "HALL_SCREW": ("WPSE313 hall: screw pulse", "in hand"),
    "HALL_HOME": ("WPSE313 hall: home", "in hand"),
    "HALL_FLOAT": ("WPSE313 hall: float (tank)", "in hand"),
    "FLOW": ("YF-S401 flow meter", "ASSUME"),
    "PERFBOARD": ("pump driver + interlock perfboard", "bench"),
    "PUMP": ("12 V diaphragm pump", "ASSUME"),
    "BRICK": ("12 V >= 3 A brick", "ASSUME"),
    "UBEC": ("5 V >= 3 A UBEC", "ASSUME"),
    "RAIL5V": ("5V_BOARD rail (breadboard)", "bench"),
    "RAILGND": ("GND rail (breadboard)", "bench"),
    "STAR": ("GND star (perfboard)", "bench"),
}


def module_name(mid: str) -> str:
    return MODULES[mid][0]


# ---------------------------------------------------------------- wires
@dataclass(frozen=True)
class Wire:
    frm: str  # module id
    frm_pin: str  # silkscreen / lead name at that end
    to: str
    to_pin: str
    net: str  # key of COLOUR_NAMES
    signal: str = ""  # name printed on the wire in the drawings
    via: str = ""  # series or pull part on the way ("1 k series", "10 k pull-up")
    connector: str = ""
    cable: str = ""  # length / routing note
    later: bool = False  # expansion, drawn dashed, not on the bench

    @property
    def board_pin(self) -> str:
        """The UNO pin this wire lands on, or ''."""
        if self.frm == "UNO":
            return self.frm_pin
        if self.to == "UNO":
            return self.to_pin
        return ""

    @property
    def colour(self) -> str:
        return COLOUR_NAMES[self.net]

    def other_end(self, mid: str) -> tuple[str, str]:
        """(module id, pin) at the end that is not `mid`."""
        return (self.to, self.to_pin) if self.frm == mid else (self.frm, self.frm_pin)


_I2C_PULL = "10 k pull-up on the module (VERIFY; else 4.7 k to 5V_BOARD)"
_HALL_CONN = "3-pin S / + (middle) / -"
_HALL_PULL = "10 k pull-up to 5V_BOARD at the breadboard"
_PH = "JST-PH 2.0 3-pin (VCC, GND, AOUT)"
_GROVE = "Grove 4-pin (VCC, GND, SIG, NC)"

WIRES: list[Wire] = [
    # -- UNO pins ------------------------------------------------------------
    Wire("UNO", "D2", "FLOW", "yellow (pulse)", "SIGNAL", "FLOW",
         via="1 k series at the board", connector="3-wire lead red / black / yellow",
         cable="<= 1 m; away from the servo lead"),
    Wire("UNO", "D3", "HALL_SCREW", "S", "SIGNAL", "HALL_SCREW",
         via=_HALL_PULL, connector=_HALL_CONN, cable="<= 50 cm; hall fixed, magnet on the cart"),
    Wire("UNO", "D4", "HALL_HOME", "S", "SIGNAL", "HALL_HOME",
         via=_HALL_PULL, connector=_HALL_CONN, cable="<= 50 cm"),
    Wire("UNO", "D5", "PERFBOARD", "FLOAT_OK", "SIGNAL", "FLOAT_OK",
         connector="screw terminal", cable="<= 30 cm; input, HIGH = allow"),
    Wire("UNO", "D6", "PERFBOARD", "PUMP_EN", "SIGNAL", "PUMP_EN",
         via="10 k pull-down on the perfboard", connector="screw terminal",
         cable="<= 30 cm; the jumper pulled in bring-up 7e"),
    Wire("UNO", "D7", "DHT", "SIG", "SIGNAL", "DHT_DATA",
         connector=_GROVE, cable="Grove 20-50 cm; free if the kit has the DHT20"),
    Wire("UNO", "D9", "SERVO", "orange (signal)", "SIGNAL", "SERVO_PWM",
         connector="JR 3-pin brown / red / orange", cable="servo lead ~25 cm; extension fine"),
    Wire("UNO", "A0", "MUX1", "SIG", "SIGNAL", "MUX1_SIG",
         connector="header / Dupont", cable="<= 20 cm; analog, 14-bit"),
    Wire("UNO", "A4", "PCF8575", "SDA", "I2C", "SDA", via=_I2C_PULL,
         connector="header / Dupont", cable="<= 20 cm"),
    Wire("UNO", "A5", "PCF8575", "SCL", "I2C", "SCL", via=_I2C_PULL,
         connector="header / Dupont", cable="<= 20 cm"),
    Wire("UNO", "5V", "RAIL5V", "+", "5V_BOARD", "5V_BOARD",
         connector="header / Dupont", cable="<= 20 cm; OUTPUT only, ~120 mA, never fed"),
    Wire("UNO", "GND", "STAR", "GND", "GND", "GND",
         connector="screw terminal", cable="<= 30 cm; the pump return never passes here"),
    Wire("BRICK", "12V+", "UNO", "VIN (barrel)", "12V", "12V",
         via="1 A fuse F2 (shared with the UBEC input)", connector="barrel 5.5/2.1 mm, centre +",
         cable="or USB-C on the bench"),
    # -- 5V_BOARD rail -> modules -------------------------------------------
    Wire("RAIL5V", "+", "MUX1", "VCC", "5V_BOARD", "5V_BOARD", via="100 nF at the module"),
    Wire("RAIL5V", "+", "PCF8575", "VCC", "5V_BOARD", "5V_BOARD", via="100 nF at the module"),
    Wire("RAIL5V", "+", "HALL_SCREW", "+ (middle)", "5V_BOARD", "5V_BOARD", connector=_HALL_CONN),
    Wire("RAIL5V", "+", "HALL_HOME", "+ (middle)", "5V_BOARD", "5V_BOARD", connector=_HALL_CONN),
    Wire("RAIL5V", "+", "FLOW", "red", "5V_BOARD", "5V_BOARD",
         cable="5V_BOARD ONLY, never 12 V: the pulses swing to the supply"),
    Wire("RAIL5V", "+", "DHT", "VCC", "5V_BOARD", "5V_BOARD", connector=_GROVE),
    Wire("RAIL5V", "+", "LDR", "VCC", "5V_BOARD", "5V_BOARD", connector=_GROVE),
    *[Wire("RAIL5V", "+", f"MOIST{i}", "VCC", "5V_BOARD", "5V_BOARD", connector=_PH,
           cable="lead + extension <= 1.5 m") for i in range(1, 6)],
    Wire("RAIL5V", "+", "PERFBOARD", "5V_BOARD", "5V_BOARD", "5V_BOARD",
         connector="screw terminal", cable="74HC00 VCC, 100 k float pull-up, 100 nF"),
    # -- GND ----------------------------------------------------------------
    Wire("STAR", "GND", "RAILGND", "-", "GND", "GND", cable="one wire, star -> breadboard GND rail"),
    Wire("RAILGND", "-", "MUX1", "GND", "GND", "GND"),
    Wire("RAILGND", "-", "PCF8575", "GND", "GND", "GND"),
    Wire("RAILGND", "-", "HALL_SCREW", "-", "GND", "GND", connector=_HALL_CONN),
    Wire("RAILGND", "-", "HALL_HOME", "-", "GND", "GND", connector=_HALL_CONN),
    Wire("RAILGND", "-", "FLOW", "black", "GND", "GND"),
    Wire("RAILGND", "-", "DHT", "GND", "GND", "GND", connector=_GROVE),
    Wire("RAILGND", "-", "LDR", "GND", "GND", "GND", connector=_GROVE),
    *[Wire("RAILGND", "-", f"MOIST{i}", "GND", "GND", "GND", connector=_PH) for i in range(1, 6)],
    Wire("MUX1", "EN", "RAILGND", "-", "GND", "MUX1_EN",
         cable="EN tied LOW: mux always enabled (breakouts may pull EN down with 10 k)"),
    # -- analog into the mux ------------------------------------------------
    *[Wire(f"MOIST{i}", "AOUT", "MUX1", f"C{i - 1}", "SIGNAL", f"MOIST{i}", connector=_PH,
           cable="~10 k source; 0-3 V") for i in range(1, 6)],
    Wire("LDR", "SIG", "MUX1", "C5", "SIGNAL", "LIGHT", connector=_GROVE, cable="0-5 V"),
    # -- select lines from the expander ------------------------------------
    *[Wire("PCF8575", f"P{i}", "MUX1", f"S{i}", "SIGNAL", f"MUX_S{i}", cable="<= 20 cm")
      for i in range(4)],
    # -- float hall -> perfboard ------------------------------------------
    Wire("HALL_FLOAT", "S", "PERFBOARD", "FLT_S", "SIGNAL", "HALL_FLOAT",
         via="100 k pull-up to 5V_BOARD on the perfboard (R4)",
         connector=_HALL_CONN + " plug: the one pulled in bring-up 7d",
         cable="to the reservoir top stop, <= 1 m"),
    Wire("HALL_FLOAT", "+ (middle)", "PERFBOARD", "FLT_+", "5V_BOARD", "5V_BOARD", connector=_HALL_CONN),
    Wire("HALL_FLOAT", "-", "PERFBOARD", "FLT_-", "GND", "GND", connector=_HALL_CONN),
    # -- 12 V, servo power, pump loop -------------------------------------
    Wire("BRICK", "12V+", "PERFBOARD", "12V_IN", "12V", "12V",
         via="T 3 A slow-blow F1, + leg only", connector="screw terminal", cable=">= 0.5 mm2"),
    Wire("BRICK", "12V+", "UBEC", "IN+", "12V", "12V",
         via="1 A fuse F2 (shared with VIN)", cable=">= 0.5 mm2"),
    Wire("BRICK", "12V-", "STAR", "GND", "GND", "GND", connector="screw terminal", cable=">= 0.5 mm2"),
    Wire("UBEC", "IN-", "STAR", "GND", "GND", "GND", cable=">= 0.5 mm2"),
    Wire("UBEC", "OUT+", "SERVO", "red", "5V_SERVO", "5V_SERVO",
         connector="JR 3-pin", cable="the ONLY destination of the UBEC output; never the UNO 5 V pin"),
    Wire("UBEC", "OUT-", "STAR", "GND", "GND", "GND"),
    Wire("SERVO", "brown", "STAR", "GND", "GND", "GND", connector="JR 3-pin"),
    Wire("PERFBOARD", "PUMP+", "PUMP", "+", "12V", "PUMP+",
         connector="screw terminal", cable=">= 0.5 mm2; flyback diode stripe on this side"),
    Wire("PERFBOARD", "PUMP-", "PUMP", "-", "PUMP_SW", "PUMP-",
         connector="screw terminal", cable=">= 0.5 mm2; switched return to the MOSFET drain, NOT ground"),
    # -- later: second mux, next manifolds (dashed) -------------------------
    *[Wire("PCF8575", f"P{i}", "MUX2", f"S{i}", "SIGNAL", f"MUX_S{i}", later=True,
           cable="select lines shared with MUX1") for i in range(4)],
    Wire("PCF8575", "P5", "MUX2", "EN", "SIGNAL", "MUX2_EN", later=True),
    Wire("MUX2", "SIG", "UNO", "A1", "SIGNAL", "MUX2_SIG", later=True),
]

# Board pins not wired on this bench, and what they are earmarked for.
BOARD_PINS_FREE: list[tuple[str, str]] = [
    ("D0 / D1", "serial: keep free"),
    ("D8", "free"),
    ("D10", "HALL_SCREW manifold 2 (later)"),
    ("D11", "HALL_HOME manifold 2 (later)"),
    ("D12", "SERVO_PWM manifold 2 (later)"),
    ("D13", "SERVO_PWM manifold 3 (later)"),
    ("A1", "MUX2 SIG (later)"),
    ("A2", "HALL_HOME manifold 3 (later; digital-capable)"),
    ("A3", "HALL_SCREW manifold 3 (later; digital-capable)"),
]

# Per-manifold pin plan (manifold 1 is the bench; 2 and 3 are later).
MANIFOLD_PINS: list[dict[str, str]] = [
    {"manifold": "1 (bench)", "servo": "D9", "hall_screw": "D3", "hall_home": "D4", "mux_sig": "A0 (MUX1)"},
    {"manifold": "2 (later)", "servo": "D12", "hall_screw": "D10", "hall_home": "D11", "mux_sig": "A1 (MUX2)"},
    {"manifold": "3 (later)", "servo": "D13", "hall_screw": "A3", "hall_home": "A2",
     "mux_sig": "A1 (MUX2, C6-C15)"},
]
MANIFOLD_NOTE = ("Manifolds 2-3 halls may go on PCF8575 P8-P15 instead (<= 2 Hz at 20:20 gears, a "
                 "2-byte read is ~0.3 ms). Manifold 1 stays on direct pins so the bench proves the "
                 "count without I2C in the loop.")


def pin_map() -> list[Wire]:
    """The wires that land on a UNO pin, in board-pin order (bench first, later last)."""
    order = ["D2", "D3", "D4", "D5", "D6", "D7", "D9", "A0", "A1", "A4", "A5", "5V", "GND", "VIN (barrel)"]
    rows = [w for w in WIRES if w.board_pin]
    return sorted(rows, key=lambda w: (w.later, order.index(w.board_pin)))


def wires_of(mid: str, include_later: bool = False) -> list[Wire]:
    """Every wire touching module `mid`."""
    return [w for w in WIRES if mid in (w.frm, w.to) and (include_later or not w.later)]


# ---------------------------------------------------------------- tables
MUX_CHANNELS: list[dict[str, str]] = [
    *[{"channel": f"C{i}", "source": f"moisture {i + 1} AOUT", "signal": f"MOIST{i + 1}",
       "note": "raw counts; the backend maps channel -> pot"} for i in range(5)],
    {"channel": "C5", "source": "Sensor Kit LDR SIG", "signal": "LIGHT", "note": "0-5 V"},
    *[{"channel": f"C{i}", "source": "open", "signal": "spare",
       "note": "next manifolds' pots; leave open"} for i in range(6, 16)],
]
MUX_NOTES = [
    "EN tied to GND (always enabled): some breakouts pull EN down with 10 k, which the expander cannot lift.",
    "Firmware: select, wait >= 1 ms, read twice, keep the second (10 k source + ~70 ohm switch into the ADC sample capacitor).",
    "100 nF across VCC/GND at the module.",
]

EXPANDER_PINS: list[dict[str, str]] = [
    *[{"pin": f"P{i}", "use": f"MUX1 S{i}", "note": "shared with MUX2 later"} for i in range(4)],
    {"pin": "P4", "use": "spare", "note": "MUX EN is tied to GND on the board"},
    {"pin": "P5", "use": "MUX2 EN (later)", "note": "dashed on the drawing"},
    {"pin": "P6", "use": "spare", "note": ""},
    {"pin": "P7", "use": "spare", "note": ""},
    *[{"pin": f"P{i}", "use": "spare", "note": "option: manifold 2-3 halls (input)"} for i in range(8, 16)],
    {"pin": "INT", "use": "not connected", "note": "nothing is read as an input on this bench"},
]
EXPANDER_NOTES = [
    "Quasi-bidirectional: pins power up HIGH, source ~100 uA high, sink 25 mA low.",
    "NEVER PUMP_EN or the servo on the expander (power-on HIGH would run them).",
    "Address 0x20 with A0-A2 low; 100 nF across VCC/GND.",
]

I2C_ADDRESSES: list[dict[str, str]] = [
    {"address": "0x20", "device": "PCF8575 expander", "note": "A0-A2 low; Wire (A4/A5, 5 V)"},
    {"address": "0x38", "device": "DHT20 temp/humidity", "note": "only if the kit has the DHT20 (Environment_I2C)"},
    {"address": "0x21-0x27", "device": "more PCF8575", "note": "later manifolds"},
]
I2C_NOTES = [
    "Wire on A4/A5 is 5 V with NO on-board pull-ups: the PCF8575 module's 10 k pull-ups serve (VERIFY, else 4.7 k to 5V_BOARD).",
    "The Qwiic connector is Wire1 at 3.3 V: not for these modules.",
]

# ---------------------------------------------------------------- perfboard
PERFBOARD_TERMINALS: list[dict[str, str]] = [
    {"terminal": "12V_IN", "wire": "brick 12V+ via F1 (T 3 A slow-blow)", "net": "12V", "gauge": ">= 0.5 mm2"},
    {"terminal": "PUMP+", "wire": "pump +; D1 stripe (cathode) here", "net": "12V", "gauge": ">= 0.5 mm2"},
    {"terminal": "PUMP-", "wire": "pump -; Q1 drain", "net": "PUMP_SW", "gauge": ">= 0.5 mm2"},
    {"terminal": "GND (star)", "wire": "brick 12V-, UBEC IN-/OUT-, servo brown, UNO GND, breadboard GND rail",
     "net": "GND", "gauge": ">= 0.5 mm2 for the 12 V returns"},
    {"terminal": "5V_BOARD", "wire": "UNO 5 V pin (U1 VCC, R4)", "net": "5V_BOARD", "gauge": "Dupont"},
    {"terminal": "PUMP_EN", "wire": "UNO D6 (R3 10 k pull-down)", "net": "SIGNAL", "gauge": "Dupont"},
    {"terminal": "FLOAT_OK", "wire": "UNO D5 (G1 out)", "net": "SIGNAL", "gauge": "Dupont"},
    {"terminal": "FLT_S", "wire": "float hall S (R4 100 k pull-up)", "net": "SIGNAL", "gauge": "3-pin plug"},
    {"terminal": "FLT_+", "wire": "float hall + (middle)", "net": "5V_BOARD", "gauge": "3-pin plug"},
    {"terminal": "FLT_-", "wire": "float hall -", "net": "GND", "gauge": "3-pin plug"},
]

INTERLOCK_PARTS: list[dict[str, str]] = [
    {"ref": "F1", "value": "T 3 A slow-blow, 5x20", "role": "pump branch, + leg only; value fixed after bring-up 7f"},
    {"ref": "F2", "value": "1 A, 5x20", "role": "UNO VIN + UBEC input, + leg only"},
    {"ref": "D1", "value": "SS34 / 1N5819", "role": "flyback across the pump, stripe (cathode) to PUMP+"},
    {"ref": "Q1", "value": "logic-level N-MOSFET module (AO3400 / IRLZ44N / D4184)",
     "role": "low side: drain PUMP-, source star GND, gate via R1; NOT an IRF520"},
    {"ref": "R1", "value": "100 ohm", "role": "G3 out -> gate series"},
    {"ref": "R2", "value": "10 k", "role": "gate pull-down to GND (even if the module has one)"},
    {"ref": "R3", "value": "10 k", "role": "PUMP_EN pull-down: LOW at reset / boot / floating"},
    {"ref": "R4", "value": "100 k", "role": "FLT_S pull-up to 5V_BOARD: unplugged = HIGH = block"},
    {"ref": "U1", "value": "74HC00 quad NAND, DIP-14", "role": "VCC 5V_BOARD (pin 14), GND star (pin 7)"},
    {"ref": "C1", "value": "100 nF", "role": "across U1 VCC / GND"},
]

# 74HC00 gates: (gate, input A, input B, output, DIP pins (A, B, Y), role)
GATES: list[dict[str, Any]] = [
    {"gate": "G1", "a": "FLT_S", "b": "FLT_S", "y": "FLOAT_OK", "pins": (1, 2, 3),
     "role": "inverter: hall LOW (magnet) -> FLOAT_OK HIGH; also to D5"},
    {"gate": "G2", "a": "PUMP_EN", "b": "FLOAT_OK", "y": "G2_OUT", "pins": (4, 5, 6),
     "role": "NAND: LOW only when both are HIGH"},
    {"gate": "G3", "a": "G2_OUT", "b": "G2_OUT", "y": "GATE", "pins": (9, 10, 8),
     "role": "inverter -> R1 100 ohm -> MOSFET gate"},
    {"gate": "G4", "a": "GND", "b": "GND", "y": "n/c", "pins": (12, 13, 11),
     "role": "unused: inputs tied to GND"},
]

# Interlock truth table. Only the first row runs the pump.
TRUTH_TABLE: list[dict[str, str]] = [
    {"case": "watering", "pump_en": "HIGH", "magnet": "at hall", "float_module": "plugged, powered",
     "logic_5v": "on", "flt_s": "LOW", "float_ok": "HIGH", "gate": "HIGH", "pump": "RUNS"},
    {"case": "firmware idle", "pump_en": "LOW", "magnet": "at hall", "float_module": "plugged, powered",
     "logic_5v": "on", "flt_s": "LOW", "float_ok": "HIGH", "gate": "LOW", "pump": "off"},
    {"case": "tank low (level past the margin)", "pump_en": "HIGH", "magnet": "away", "float_module": "plugged, powered",
     "logic_5v": "on", "flt_s": "HIGH", "float_ok": "LOW", "gate": "LOW", "pump": "off"},
    {"case": "tank lifted off the hall", "pump_en": "HIGH", "magnet": "away", "float_module": "plugged, powered",
     "logic_5v": "on", "flt_s": "HIGH", "float_ok": "LOW", "gate": "LOW", "pump": "off"},
    {"case": "float hall unplugged", "pump_en": "HIGH", "magnet": "any", "float_module": "S open",
     "logic_5v": "on", "flt_s": "HIGH (R4)", "float_ok": "LOW", "gate": "LOW", "pump": "off"},
    {"case": "float hall GND lead off", "pump_en": "HIGH", "magnet": "any", "float_module": "no return",
     "logic_5v": "on", "flt_s": "HIGH (R4)", "float_ok": "LOW", "gate": "LOW", "pump": "off"},
    {"case": "float hall VCC lost / dead hall", "pump_en": "HIGH", "magnet": "any", "float_module": "unpowered",
     "logic_5v": "on", "flt_s": "HIGH (R4)", "float_ok": "LOW", "gate": "LOW", "pump": "off"},
    {"case": "MCU in reset / boot / D6 not yet OUTPUT / jumper pulled", "pump_en": "floating -> LOW (R3)",
     "magnet": "any", "float_module": "any", "logic_5v": "on", "flt_s": "-", "float_ok": "-",
     "gate": "LOW", "pump": "off"},
    {"case": "board 5 V absent (USB out, board dead)", "pump_en": "-", "magnet": "any", "float_module": "any",
     "logic_5v": "off", "flt_s": "-", "float_ok": "LOW", "gate": "LOW (R2)", "pump": "off"},
    {"case": "12 V absent", "pump_en": "any", "magnet": "any", "float_module": "any",
     "logic_5v": "any", "flt_s": "-", "float_ok": "-", "gate": "-", "pump": "off (unpowered)"},
]
INTERLOCK_NOTES = [
    "Failure direction is dry: every open, unplug, power loss and reset lands on 'off'.",
    "Residual (not in the brief): a float hall output shorted to GND, or the magnet stuck to the hall, "
    "reads as a permanent 'allow' that D5 cannot tell apart; the firmware dose cap and the "
    "flow-meter no-flow timeout bound it.",
]

# ---------------------------------------------------------------- power
POWER_BUDGET: list[dict[str, str]] = [
    {"rail": "12V", "consumer": "pump (via F1)", "current": "<= 1.5 A running, 3-5x inrush", "note": "ASSUME: read the label, measure in 7f"},
    {"rail": "12V", "consumer": "UNO VIN (via F2)", "current": "~0.15 A", "note": "board + the 5V_BOARD load through the on-board buck"},
    {"rail": "12V", "consumer": "UBEC input (via F2)", "current": "~0.35 A at servo stall", "note": "F2 1 A covers VIN + UBEC"},
    {"rail": "5V_BOARD", "consumer": "5x moisture", "current": "~25 mA", "note": ""},
    {"rail": "5V_BOARD", "consumer": "3x hall (LEDs)", "current": "~30 mA", "note": "screw, home, float"},
    {"rail": "5V_BOARD", "consumer": "flow meter", "current": "~15 mA", "note": "never from 12 V"},
    {"rail": "5V_BOARD", "consumer": "MUX, PCF8575, 74HC00, DHT11, LDR, pull-ups", "current": "< 10 mA", "note": ""},
    {"rail": "5V_BOARD", "consumer": "total", "current": "~120 mA", "note": "the rows sum to ~80 mA; 120 mA is the budget with margin, of <= ~1 A on VIN"},
    {"rail": "5V_SERVO", "consumer": "SG90 continuous", "current": "~250 mA run, ~650 mA stall", "note": "UBEC >= 3 A; its only load"},
]
FUSES = [
    {"ref": "F1", "value": "T 3 A slow-blow", "branch": "pump (perfboard 12V_IN)", "leg": "+ only"},
    {"ref": "F2", "value": "1 A", "branch": "UNO VIN (barrel) and UBEC input", "leg": "+ only"},
]
NEVER = [
    "UBEC output to the UNO 5 V pin: never (5V_SERVO and 5V_BOARD stay apart; continuity check 0).",
    "12 V to any 5 V rail or to the flow meter: never.",
    "Feed the UNO 5 V pin from outside: never (it is an output).",
    "Servo or pump on the board's 5 V pin: never.",
    "A fuse in a return leg: never (+ leg only).",
    "The pump return through the board GND pin: never (MOSFET source -> star).",
    "PUMP_EN or the servo on the I2C expander: never (power-on HIGH).",
    "Breadboard or Dupont in the 12 V loop: never (soldered perfboard, screw terminals, >= 0.5 mm2).",
]
BENCH_POWER_ALT = ("Bench alternative: USB-C powers the UNO; the 12 V brick powers the pump branch and "
                   "the UBEC; grounds common at the star.")

# ---------------------------------------------------------------- hydraulics
HYDRAULIC_CHAIN: list[dict[str, str]] = [
    {"stage": "reservoir", "detail": "ABOVE the pump inlet (gravity-primed); float hall at the top stop, float keyed"},
    {"stage": "pump", "detail": "12 V diaphragm, inlet below the reservoir surface"},
    {"stage": "silicone tube 30-50 cm", "detail": "soft: pulsation damper"},
    {"stage": "flow meter", "detail": "vertical, flow UPWARD, tilt <= 5 deg; no pulses below its flow floor"},
    {"stage": "manifold inlet", "detail": "one manifold, 5 outlets"},
    {"stage": "outlets 1-5", "detail": "pots, or the bucket on the bench"},
]

# ---------------------------------------------------------------- parts
# status: in hand | ASSUME (ordered) | to buy | to build
PARTS: list[dict[str, str]] = [
    {"part": "Arduino UNO R4 WiFi", "qty": "1", "status": "in hand", "verify": ""},
    {"part": "PCF8575 I2C expander module", "qty": "1", "status": "in hand",
     "verify": "VERIFY 10 k pull-ups on SDA/SCL (else add 4.7 k to 5V_BOARD); A0-A2 low -> 0x20"},
    {"part": "CD74HC4067 mux module", "qty": "1 (+1 later)", "status": "in hand",
     "verify": "VERIFY EN pull-down on the breakout (EN goes to GND regardless)"},
    {"part": "Whadda WPSE313 hall module", "qty": "3 of 8", "status": "in hand",
     "verify": "VERIFY on-board pull-up (ours is fitted regardless); LED lights at the magnet's south pole"},
    {"part": "SG90 continuous-rotation servo", "qty": "1", "status": "in hand", "verify": "5V_SERVO only (650 mA stall)"},
    {"part": "Sensor Kit temperature/humidity", "qty": "1", "status": "in hand",
     "verify": "READ THE MODULE: DHT11 (D7, Environment.setPin(7)) or DHT20 (I2C 0x38, Environment_I2C)"},
    {"part": "Sensor Kit light (LDR)", "qty": "1", "status": "in hand", "verify": ""},
    {"part": "capacitive soil-moisture sensor v1.2/v2.0", "qty": "5", "status": "in hand", "verify": "AOUT 0-3 V, ~10 k source"},
    {"part": "neodymium magnets (cart, screw, float)", "qty": "3+", "status": "in hand",
     "verify": "VERIFY polarity: south pole toward the hall face"},
    {"part": "pump, 12 V DC diaphragm", "qty": "1", "status": "ASSUME",
     "verify": "READ THE LABEL: voltage, running current (assume <= 1.5 A), inrush 3-5x; measure in 7f, then fix F1"},
    {"part": "12 V brick", "qty": "1", "status": "ASSUME >= 3 A",
     "verify": "READ THE LABEL: amps (a 2 A brick browns out at pump start)"},
    {"part": "MOSFET module, logic level, low side", "qty": "1", "status": "ASSUME",
     "verify": "READ THE LABEL: AO3400 / IRLZ44N / D4184 ok, IRF520 NOT; meter: own gate pull-down? "
               "If a relay module came: H/L jumper to H or an NPN inverter (out -> 4.7 k -> base, emitter GND, collector -> IN)"},
    {"part": "flow meter YF-S401", "qty": "1", "status": "ASSUME",
     "verify": "READ THE SUFFIX: -0207 (0.2-3 L/min) or -3507 (0.3-6 L/min); ~5880 pulses/L; vertical, flow up; 5V_BOARD only"},
    {"part": "UBEC 5 V >= 3 A", "qty": "1", "status": "ASSUME",
     "verify": "VERIFY 5.0 V out unloaded before the servo goes on; output to the servo only"},
    {"part": "74HC00 quad NAND, DIP-14", "qty": "1", "status": "to buy", "verify": ""},
    {"part": "fuse holders 5x20 + T 3 A slow-blow + 1 A", "qty": "2 + spares", "status": "to buy", "verify": "F1 value fixed after 7f"},
    {"part": "Schottky SS34 / 1N5819", "qty": "1", "status": "to buy", "verify": ""},
    {"part": "resistors 100 ohm x1, 1 k x1, 4.7 k x2, 10 k x4, 100 k x1", "qty": "set", "status": "to buy",
     "verify": "10 k: R2, R3, 2 hall pull-ups; 4.7 k only if I2C pull-ups are missing / NPN inverter"},
    {"part": "100 nF ceramic", "qty": "3", "status": "to buy", "verify": "74HC00, mux, expander"},
    {"part": "perfboard, screw terminals (>= 10 positions), wire >= 0.5 mm2 red/black/purple", "qty": "1 set", "status": "to buy",
     "verify": "soldered; never breadboard in the 12 V loop"},
    {"part": "breadboard, Dupont jumpers (colours per the table), JST-PH 2.0 leads x5, Grove cables x2", "qty": "1 set", "status": "to buy", "verify": ""},
    {"part": "silicone tube 30-50 cm + tube for the meter's 7 mm outlet and the manifold inlet", "qty": "1 set", "status": "to buy", "verify": "meter variant sets the intake bore"},
    {"part": "reservoir with a keyed float carrying a magnet; bucket", "qty": "1", "status": "to build",
     "verify": "hall at the float's top stop; magnet leaves the hall as the level drops past the margin"},
]

# ---------------------------------------------------------------- bench firmware contract
BENCH_FIRMWARE_NOTE = ("The bench sketch is not part of this deliverable (pitch: 'Bench rig'); "
                       "it must provide these commands over serial.")
BENCH_COMMANDS: list[dict[str, str]] = [
    {"command": "i2c", "does": "scan Wire, list addresses (expect 0x20; 0x38 if DHT20)"},
    {"command": "mux <0-15>|all", "does": "select, wait >= 1 ms, read twice, print the second (14-bit raw)"},
    {"command": "hall", "does": "stream screw / home / float (D5 FLOAT_OK) pin states"},
    {"command": "flow", "does": "pulses per second on D2 and total since reset"},
    {"command": "servo <+-us> <ms>", "does": "bounded: pulse offset for <= cap ms, then stop"},
    {"command": "home", "does": "run toward home until HALL_HOME, bounded time, zero the count"},
    {"command": "goto <1-5>", "does": "step to the outlet counting screw pulses, bounded"},
    {"command": "pump <ms>", "does": "PUMP_EN HIGH for <= cap ms; refused while FLOAT_OK (D5) is LOW"},
    {"command": "status", "does": "pins, counts, last error, uptime"},
]

BRINGUP: list[dict[str, str]] = [
    {"step": "0", "do": "Continuity before power: UBEC+ to UNO 5 V OPEN; 12 V to every 5 V rail OPEN; all GNDs common at the star.",
     "proves": "the two 5 V rails are apart"},
    {"step": "1", "do": "Board alone on USB: `i2c` sees 0x20 (and 0x38 if DHT20).", "proves": "I2C, pull-ups"},
    {"step": "2", "do": "Mux + one moisture sensor: `mux all` reads all 16 channels, the wired one moves when wetted.",
     "proves": "select lines, ADC path"},
    {"step": "3", "do": "Halls: LED and pin follow a magnet; then the cart end-to-end three times with the same pulse count.",
     "proves": "pulse counting, home"},
    {"step": "4", "do": "Flow meter: prime with `pump` into the bucket until no bubbles; pump a weighed 500 ml through outlet 1 counting pulses = the ml/pulse calibration; record the lowest flow that still pulses and set the no-pulse timeout from it.",
     "proves": "meter variant, calibration, floor"},
    {"step": "5", "do": "Float: magnet away = D5 LOW = blocked; magnet at hall = D5 HIGH = allowed; meter the S line with the magnet away (>= 4 V).",
     "proves": "sense path and pull-up"},
    {"step": "6", "do": "Servo on 5V_SERVO only: `servo`, `home`, `goto`.", "proves": "servo power apart from the board"},
    {"step": "7a", "do": "Pump, bucket only: float blocked -> `pump 2000` must NOT run.", "proves": "interlock blocks"},
    {"step": "7b", "do": "Float allowed -> `pump 2000` runs.", "proves": "interlock allows"},
    {"step": "7c", "do": "RESET pressed mid-dose -> stops.", "proves": "R3 pull-down"},
    {"step": "7d", "do": "Float hall unplugged mid-dose -> stops.", "proves": "R4 pull-up"},
    {"step": "7e", "do": "D6 jumper pulled mid-dose -> stops.", "proves": "no hidden path to the gate"},
    {"step": "7f", "do": "Measure pump start and dead-head current; fix the F1 value.", "proves": "fuse value"},
]


# ---------------------------------------------------------------- rendering
def md_table(rows: Sequence[Any], columns: Sequence[tuple[str, str]] | None = None) -> str:
    """Render rows (dicts or dataclasses) as a GitHub markdown table.

    columns: (key, header) pairs; default = every key of the first row. A key
    may be a dataclass property (e.g. Wire.board_pin). Pipes are escaped, bools
    become yes/no, tuples are joined with ", ".
    """
    if not rows:
        return ""

    def get(row: Any, key: str) -> Any:
        return row[key] if isinstance(row, dict) else getattr(row, key)

    if columns is None:
        first = rows[0]
        keys = list(first.keys()) if isinstance(first, dict) else [f.name for f in fields(first)]
        columns = [(k, k) for k in keys]

    def cell(v: Any) -> str:
        if isinstance(v, bool):
            return "yes" if v else "no"
        if v is None:
            return ""
        if isinstance(v, (tuple, list)):
            v = ", ".join(str(x) for x in v)
        return str(v).replace("|", "\\|").replace("\n", " ")

    head = "| " + " | ".join(h for _, h in columns) + " |"
    sep = "|" + "|".join(" --- " for _ in columns) + "|"
    body = ["| " + " | ".join(cell(get(r, k)) for k, _ in columns) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def md_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {it}" for it in items)


def _check() -> None:
    """Self-consistency: every wire's modules and nets exist; anchors are unique per block."""
    for w in WIRES:
        assert w.frm in MODULES, w
        assert w.to in MODULES, w
        assert w.net in COLOUR_NAMES, w
    pins = [w.board_pin for w in pin_map()]
    assert len(pins) == len(set(pins)), pins
    ubec_out = [w for w in WIRES if w.frm == "UBEC" and w.frm_pin == "OUT+"]
    assert len(ubec_out) == 1 and ubec_out[0].to == "SERVO", "UBEC output has exactly one destination"


_check()

if __name__ == "__main__":
    print(md_table(pin_map(), [("board_pin", "board pin"), ("signal", "signal"), ("to", "module"),
                               ("to_pin", "module pin"), ("connector", "connector"), ("colour", "colour"),
                               ("cable", "cable / note"), ("later", "later")]))
    print()
    print(md_table(MUX_CHANNELS))
    print()
    print(md_table(EXPANDER_PINS))
    print()
    print(md_table(TRUTH_TABLE))
    print()
    print(md_table(PARTS))
    print(f"\n{len(WIRES)} wires, {len([w for w in WIRES if not w.later])} on the bench")
