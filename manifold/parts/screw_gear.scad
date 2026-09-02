// parts/screw_gear.scad — the spur gear on the M3 lead screw [gears.FCStd screw_gear].
//
// Axis Z on the rod (W/2, screw_y), z∈[gear_z0, gear_z1] outboard of the servo holder,
// meshing with the servo gear `gear_cd` above it. A ø`screw_hole_d` clearance hole through,
// and a hex trap `nut_af + nut_clear` across flats, `nut_t` deep, on the −Z (outer) face:
// the nut in it is what drives the rod. A second nut outboard clamps the gear, through an M3
// washer (`washer_od`): the nut alone (`nut_af` across flats) fits inside the trap outline, so
// it would only jam against the trapped nut and leave the gear free to slide up the rod; the
// washer is what bears on the gear's annular face outside the trap (root radius ≥ nut_ac/2 +
// wall, so the washer, r = washer_od/2, clears the tooth roots).
// The gear already carries its meshing phase: a gap faces the servo gear (+Y), whose tooth
// points down into it (servo_gear.scad) — the assembly places both as they are.

include <../params.scad>
use <../lib/gear.scad>
use <../lib/shapes.scad>
$fn = fn_round;
eps = 0.01;

scg_root_r = gear_root_r(screw_teeth, gear_module);   // hub material outside the trap must stay a wall

// The asserts live inside the module, not at file top level: `use <screw_gear.scad>` (assembly.scad)
// imports modules, functions and variables but does not execute top-level statements, so a
// file-top assert would be silent in the assembly and only fire on a standalone render.
module screw_gear() {
    assert(nut_t < gear_t - num_tol, "screw_gear: nut trap goes through the gear");
    assert(nut_ac/2 + wall <= scg_root_r + num_tol, "screw_gear: less than a wall between the nut trap and the tooth roots");
    assert(screw_hole_d < nut_af, "screw_gear: rod hole wider than the nut");
    translate([W/2, screw_y, gear_z0]) difference() {
        // gear_2d puts a tooth on +X: turned so a gap (half a pitch past a tooth) faces the servo gear above (+Y)
        rotate([0, 0, 90 + 180/screw_teeth]) spur_gear(screw_teeth, gear_module, gear_t, pressure_angle, gear_backlash);
        translate([0, 0, -eps]) cylinder(d=screw_hole_d, h=gear_t + 2*eps, $fn=fn_small);
        // nut trap from the outer face, flats vertical like the cart's slot (hex() has corners on ±X)
        translate([0, 0, -eps]) rotate([0, 0, 90]) hex(nut_af + nut_clear, nut_t + eps);
    }
}

// Print: the pocket-free +Z face (z = gear_z1) on the bed, so the part is flipped over;
// the nut trap then opens up. rotate([180,0,0]) maps (x, y, z) onto (x, −y, −z).
module screw_gear_print() { rotate([180, 0, 0]) translate([0, 0, -gear_z1]) screw_gear(); }

function screw_gear_size() = [gear_od(screw_teeth), gear_od(screw_teeth), gear_t];

for_print = false;
if (is_undef(ASSEMBLY)) {
    echo(screw_gear_size=screw_gear_size(), scg_root_r=scg_root_r, pitch_r=gear_pitch_r(screw_teeth, gear_module), nut_ac=nut_ac);
    if (for_print) screw_gear_print(); else screw_gear();
}
