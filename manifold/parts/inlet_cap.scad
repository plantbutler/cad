// parts/inlet_cap.scad — plug + hose barb closing the back (inlet end) of the manifold
// [v2 in_cap = Body005 plug fused with connector_8mm].
//
// The plug fills the body's back end between its outer half-skins (wall/2 in from the body's
// outside on both sides and the floor) and under the lid plate, `joint_len` deep, with
// joint_clear per side so it slides in and leaves room for glue. The barb starts on the plug's
// front (gallery-side) face and runs `inlet_barb[3]` along +Z: its shank passes through the
// plug and the ridges stand `inlet_barb[3] − joint_len` proud of the back face, as v2. The
// bore ø inlet_barb[0] runs through plug and barb on the gallery axis (v2's plug hole was the
// separate barb's ø10 shank; here they are one part, so the hole is the bore).

include <../params.scad>
use <../lib/barb.scad>
$fn = fn_round;

for_print = false;

z_plug0 = body_z1 - joint_len;               // plug front face = barb base (the barb sits on gal_y, params.scad)
plug_x0 = wall/2 + joint_clear;  plug_x1 = W - wall/2 - joint_clear;
plug_y0 = wall/2 + joint_clear;  plug_y1 = top_y - wall/2 - joint_clear;
eps = 0.01;

// extents in the assembly frame: the ridges may stand proud of the plug in y (they do with the
// defaults: 13.15 above 12.85), so take the larger of plug and ridge each way
function inlet_cap_bbox() =
    [[min(plug_x0, W/2 - inlet_barb[2]/2), min(plug_y0, gal_y - inlet_barb[2]/2), z_plug0],
     [max(plug_x1, W/2 + inlet_barb[2]/2), max(plug_y1, gal_y + inlet_barb[2]/2), z_plug0 + inlet_barb[3]]];
function inlet_cap_size() = inlet_cap_bbox()[1] - inlet_cap_bbox()[0];

module inlet_cap() {
    difference() {
        union() {
            translate([plug_x0, plug_y0, z_plug0])
                cube([plug_x1 - plug_x0, plug_y1 - plug_y0, joint_len]);
            translate([W/2, gal_y, z_plug0])
                barb(inlet_barb[0], inlet_barb[1], inlet_barb[2], inlet_barb[3], barb_ridges,
                     inlet_barb_prof[0], inlet_barb_prof[1], barb_steep, undef, barb_ridge_gap);
        }
        // one bore through plug and barb: the plug fills the barb's bore where they overlap
        translate([W/2, gal_y, z_plug0 - eps]) cylinder(d=inlet_barb[0], h=inlet_barb[3] + 2*eps);
    }
}

// Plug front face on the bed, barb vertical: each ridge's rise overhangs at barb_steep from
// vertical over (ridge − shank)/2 of radius, which the layers step out without support.
module inlet_cap_print() { translate([0, 0, -z_plug0]) inlet_cap(); }

if (is_undef(ASSEMBLY)) { if (for_print) inlet_cap_print(); else inlet_cap(); }
