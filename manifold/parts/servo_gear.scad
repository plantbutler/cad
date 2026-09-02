// parts/servo_gear.scad — the spur gear on the SG90 spline [gears.FCStd servo_gear].
//
// Axis Z on the servo shaft (W/2, servo_y), z∈[gear_z0, gear_z1] outboard of the servo
// holder. A ø`servo_spline_d` pocket `servo_spline_depth` deep from the +Z (servo) face takes
// the 21T spline as a press fit; the ø`servo_screw_d` hole through the rest passes the horn
// screw. The gear already carries its meshing phase: one tooth points at the screw gear (−Y),
// which has a gap there (screw_gear.scad) — the assembly places both as they are.

include <../params.scad>
use <../lib/gear.scad>
$fn = fn_round;
eps = 0.01;

sg_root_r = gear_root_r(servo_teeth, gear_module);   // hub material outside the pocket must stay a wall

// The asserts live inside the module, not at file top level: `use <servo_gear.scad>` (assembly.scad)
// imports modules, functions and variables but does not execute top-level statements, so a
// file-top assert would be silent in the assembly and only fire on a standalone render.
module servo_gear() {
    assert(servo_spline_depth < gear_t - num_tol, "servo_gear: spline pocket goes through the gear");
    assert(servo_spline_d/2 + wall <= sg_root_r + num_tol, "servo_gear: less than a wall between the spline pocket and the tooth roots");
    assert(servo_screw_d < servo_spline_d, "servo_gear: horn screw hole wider than the spline pocket");
    translate([W/2, servo_y, gear_z0]) difference() {
        // gear_2d puts a tooth on +X: turned so it points at the screw gear below (−Y)
        rotate([0, 0, -90]) spur_gear(servo_teeth, gear_module, gear_t, pressure_angle, gear_backlash);
        translate([0, 0, gear_t - servo_spline_depth]) cylinder(d=servo_spline_d, h=servo_spline_depth + eps);
        translate([0, 0, -eps]) cylinder(d=servo_screw_d, h=gear_t + 2*eps, $fn=fn_small);
    }
}

// Print: the pocket-free −Z face (z = gear_z0) on the bed, spline pocket opening up.
module servo_gear_print() { translate([0, 0, -gear_z0]) servo_gear(); }

function servo_gear_size() = [gear_od(servo_teeth), gear_od(servo_teeth), gear_t];

for_print = false;
if (is_undef(ASSEMBLY)) {
    echo(servo_gear_size=servo_gear_size(), sg_root_r=sg_root_r, pitch_r=gear_pitch_r(servo_teeth, gear_module));
    if (for_print) servo_gear_print(); else servo_gear();
}
