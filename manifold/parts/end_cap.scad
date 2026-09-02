// parts/end_cap.scad — closes the front (servo end) of the manifold [v2 Body004 end_cap].
//
// A block x∈[0,W], y∈[0,top_y], z∈[z_cap0, −joint_len]: the front wall (`wall` thick; the servo
// holder stands on it and shares its front face) plus the walls of a cavity `extra_len` long
// where the water turns before the first gate [v2 Sketch013 / Pad007, Sketch026 / Pocket005].
// Toward the body the block carries a ring `joint_len` long that laps over the body's front
// end [v2 Sketch014 / Pad008]: just the two side skins x∈[0, wall/2] (mirrored). Unlike v2's
// closed ring there is NO floor skin and NO top bar: the body's full-thickness front floor and
// the lid plate's front extension butt the block face instead (v2's floor skin there floated
// 0.8 mm above the bed; a top bar would leave the lid lip hanging 4 mm past its plate, a
// cantilever 0.8 mm above the bed in the lid's print orientation). The body's inner half side
// walls and the lid lip land between the skins; joint_clear is taken on the body and lid side,
// so the skins are nominal.
// v2's 0.4 lead-in chamfer on the ring's inner edges is not reproduced (the brief lists none).
//
// end_cap_outlet: an inlet barb through the front wall on the gallery axis, pointing −Z, for
// daisy-chaining manifolds. It is modelled rather than refused so the assembly shows the
// clash: the screw gear hangs in front of the plate over the same heights as the barb's first
// ridge. Moving the servo holder out of its way is out of scope.

include <../params.scad>
use <../lib/barb.scad>
$fn = fn_round;

for_print = false;

z_cav0 = -(joint_len + extra_len);   // cavity front face = inside of the front wall
eps    = 0.01;

// extents in the assembly frame; the barb, when present, is inside the block's x and y
function end_cap_bbox() = [[0, 0, z_cap0 - (end_cap_outlet ? inlet_barb[3] : 0)], [W, top_y, 0]];
function end_cap_size() = end_cap_bbox()[1] - end_cap_bbox()[0];

module end_cap() {
    difference() {
        union() {
            // block: front wall + cavity walls [v2 Pad007 = wallThickness + extraLength]
            translate([0, 0, z_cap0]) cube([W, top_y, wall + extra_len]);
            // ring [v2 Pad008 without its floor skin or top bar]: two side skins
            for (x0 = [0, W - wall/2]) translate([x0, 0, -joint_len]) cube([wall/2, top_y, joint_len]);
            if (end_cap_outlet)
                translate([W/2, gal_y, z_cap0]) rotate([180, 0, 0])   // +Z of the barb → −Z
                    barb(inlet_barb[0], inlet_barb[1], inlet_barb[2], inlet_barb[3], barb_ridges,
                         inlet_barb_prof[0], inlet_barb_prof[1], barb_steep, undef, barb_ridge_gap);
        }
        // water cavity, open toward the body (the overshoot ends inside the U, which is void there)
        translate([wall, wall, z_cav0]) cube([inner_w, inner_h, extra_len + eps]);
        // bore through the front wall, continuing the barb's own bore
        if (end_cap_outlet)
            translate([W/2, gal_y, z_cap0 - inlet_barb[3] - eps])
                cylinder(d=inlet_barb[0], h=inlet_barb[3] + wall + 2*eps);
    }
}

// Front wall on the bed: cavity and ring open upward, the U's skins stand as 0.8 mm walls.
// With the outlet barb the part is turned over instead — ring end on the bed, barb up — and
// the front wall then bridges the cavity (inner_w wide): out of scope, printable with care.
module end_cap_print() {
    if (end_cap_outlet) translate([W, 0, 0]) rotate([0, 180, 0]) end_cap();
    else translate([0, 0, -z_cap0]) end_cap();
}

if (is_undef(ASSEMBLY)) { if (for_print) end_cap_print(); else end_cap(); }
