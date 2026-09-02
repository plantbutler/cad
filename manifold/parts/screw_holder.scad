// parts/screw_holder.scad — bearing plate for the back end of the lead screw [v2 Body008].
//
// A plate `wall` thick standing on the lid plate at the very back, z∈[body_z1 − wall, body_z1]
// (over the inlet plug, glued to the lid): W wide, sh_side_h tall at the sides, straight
// chamfers up to a flat apex at sh_top spanning 2·sh_flat around the rod hole, so exactly one
// wall of material is left above the hole [v2 Sketch020 / Pad013]. Two feet at the sides reach
// sh_foot_len toward the body along the lid's edges and square the plate up [v2 Sketch025 /
// Pad017, 4 long: the cart could not reach the last gate]. The feet's free top corner is
// chamfered 45° [v2 Chamfer006] by sh_foot_chamfer, asserted no larger than the foot.

include <../params.scad>
use <../lib/shapes.scad>
$fn = fn_round;

for_print = false;

z_plate0 = body_z1 - wall;                   // plate front face
z_foot0  = z_plate0 - sh_foot_len;           // feet's free end
foot_c   = sh_foot_chamfer;                  // asserted (in the module) no larger than the foot
eps = 0.01;

function screw_holder_bbox() = [[0, top_y, z_foot0], [W, sh_top, body_z1]];
function screw_holder_size() = screw_holder_bbox()[1] - screw_holder_bbox()[0];

// The asserts live inside the module, not at file top level: `use <screw_holder.scad>` (assembly.scad)
// imports modules, functions and variables but does not execute top-level statements, so a
// file-top assert would be silent in the assembly and only fire on a standalone render.
module screw_holder() {
    assert(foot_c <= min(sh_foot_len, sh_side_h) + num_tol, "screw_holder: foot chamfer larger than the foot");
    // plate with the rod hole
    translate([0, 0, z_plate0]) linear_extrude(wall) difference() {
        polygon([[0, top_y], [0, top_y + sh_side_h], [W/2 - sh_flat, sh_top],
                 [W/2 + sh_flat, sh_top], [W, top_y + sh_side_h], [W, top_y]]);
        translate([W/2, screw_y]) circle(d=screw_hole_d, $fn=fn_small);
    }
    // feet, chamfered on the corner away from the plate and the lid
    for (x0 = [0, W - wall]) translate([x0, 0, 0]) difference() {
        translate([0, top_y, z_foot0]) cube([wall, sh_side_h, sh_foot_len]);
        // rotate([90,0,90]) maps the 2D (u, v) plane to world (y, z), extruding along +X
        translate([-eps, 0, 0]) rotate([90, 0, 90]) linear_extrude(wall + 2*eps)
            translate([top_y + sh_side_h, z_foot0]) mirror([1, 0]) right_triangle(foot_c);
    }
}

// Plate back face on the bed (turned over), feet pointing up; their chamfer becomes a 45° roof.
module screw_holder_print() { translate([W, 0, body_z1]) rotate([0, 180, 0]) screw_holder(); }

if (is_undef(ASSEMBLY)) { if (for_print) screw_holder_print(); else screw_holder(); }
