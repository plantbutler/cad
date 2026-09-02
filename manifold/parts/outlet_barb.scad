// parts/outlet_barb.scad — the hose barb glued under the floor at each outlet [v2 connector]:
// lib/barb.scad's profile with the outlet_* parameters, flange cone on the floor, pointing −Y.
// `outlet_barb(i)` places it on gate i's outlet axis (W/2, 0, gate_z(i)); the assembly calls
// it once per gate. The barb's own axis (+Z from the flange face) is the print orientation.
include <../params.scad>
use <../lib/barb.scad>
$fn = fn_round;
for_print = false;
eps = 0.01;

// [x, y, z] extents in the assembly frame: the flange is the widest part
function outlet_barb_size() = [outlet_flange[0], outlet_barb[3], outlet_flange[0]];

// the barb on its own axis, +Z from the flange face at z=0 (= print orientation)
module outlet_barb_axial() {
    // the bore is already in the revolved profile; a cutter that lies inside it changes nothing
    // but makes the export a CGAL solid (a bare rotate_extrude reports only facets)
    difference() {
        barb(outlet_barb[0], outlet_barb[1], outlet_barb[2], outlet_barb[3], barb_ridges,
             outlet_barb_prof[0], outlet_barb_prof[1], barb_steep, outlet_flange, barb_ridge_gap);
        translate([0, 0, -eps]) cylinder(d=outlet_barb[0] - 2*eps, h=outlet_barb[3] + 2*eps);
    }
}

// in the assembly frame under gate i (rotate +90 about X points the barb's +Z down −Y)
module outlet_barb(i=0) { translate([W/2, 0, gate_z(i)]) rotate([90, 0, 0]) outlet_barb_axial(); }

// flange face on the bed, barb vertical: the ridges' steep faces are 0.5 mm steps
module outlet_barb_print() { outlet_barb_axial(); }

if (is_undef(ASSEMBLY)) {
    echo(outlet_barb_size=outlet_barb_size());
    if (for_print) outlet_barb_print(); else outlet_barb();
}
