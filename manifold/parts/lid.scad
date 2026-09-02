// parts/lid.scad — closes the gallery and carries the ball cages. Reproduces valveV2's lid
// (lid_body, back_connection / front_connection laps, internal_chamfer fillets,
// LinearPattern 5×pitch) with the brief's changes: the plunger guide tube is now a cage
// ø cage_od / ø cage_bore reaching down to cage_bottom_y around each ball, the lip has
// joint_clear toward the body walls, and an optional magnet groove along the top.
// Frame: X across (0..W), Y up, Z along. Plate z∈[0, body_z1], plus a narrowed extension over
// the front lap z∈[body_z0, 0] (departs from the brief: the end cap's ring has no top bar, the
// plate itself is the top there, mirroring how the body's full floor replaces the ring's floor
// skin — otherwise the lip and its fillets hang 4 mm past the plate as a cantilever 0.8 mm above
// the bed); lip z∈[body_z0, body_z1 − joint_len] (it laps into the end cap's ring at the front
// and stops short of the inlet plug).
include <../params.scad>
use <../lib/shapes.scad>
$fn = fn_round;
for_print = false;
eps = 0.01;   // overlap between unioned solids / overshoot of cutters: no coincident CGAL faces

// [x, y, z] extents in the assembly frame (cage bottoms to plate top)
function lid_size() = [W, top_y - cage_bottom_y, body_z1 - body_z0];

module lid() {
    // over the back lap only the plate exists, so a groove deeper than the plate would open it
    assert(lid_slot_depth < wall/2, "lid_slot_depth must be less than the plate thickness wall/2");
    x_lip0 = wall + joint_clear;  lip_w = inner_w - 2*joint_clear;   // lip drops between the body walls
    y_plate0 = top_y - wall/2;                                        // plate underside = body wall tops
    y_roof   = top_y - wall;                                          // lip underside: the lifted ball touches it
    z_lip0 = body_z0;  z_lip1 = body_z1 - joint_len;
    slot_w = mag_d + mag_clear + line_w;   // magnet hole plus one extrusion width of running clearance
    difference() {
        union() {
            translate([0, y_plate0, 0]) cube([W, wall/2, body_z1]);                        // plate
            // plate over the front lap, narrowed by joint_clear per side to sit inside the end
            // cap's ring opening (same x formula as the body's front floor): puts the lip's
            // whole length on the bed and closes the top of the ring, which has no bar of its own
            translate([wall/2 + joint_clear, y_plate0, body_z0])
                cube([W - wall - 2*joint_clear, wall/2, -body_z0 + eps]);
            translate([x_lip0, y_roof, z_lip0]) cube([lip_w, wall/2, z_lip1 - z_lip0]);     // lip
            // 45° fillets hanging under both long lip edges [v2 internal_chamfer]: they brace the
            // lip against the wall and turn the roof/wall corner into a slope
            lip_fillet();
            translate([W/2, 0, 0]) mirror([1, 0, 0]) translate([-W/2, 0, 0]) lip_fillet();
            // cages: an annulus per gate from the lip underside down to cage_bottom_y; the lip
            // itself is the ball's stop, so the bore is not cut into it
            for (i = [0 : n_gates - 1])
                translate([W/2, cage_bottom_y, gate_z(i)]) rotate([-90, 0, 0])
                    linear_extrude(y_roof - cage_bottom_y + eps)
                        difference() { circle(d=cage_od); circle(d=cage_bore); }
        }
        // optional magnet groove along the lid top centre
        if (lid_slot_depth > 0)
            translate([W/2 - slot_w/2, top_y - lid_slot_depth, -eps]) cube([slot_w, lid_slot_depth + eps, body_z1 + 2*eps]);
    }
    // the −X fillet: vertical leg down the lip's outer face, horizontal leg along its underside,
    // plus an eps strip up into the lip so the union has no coincident faces
    module lip_fillet() translate([x_lip0, y_roof, z_lip0]) linear_extrude(z_lip1 - z_lip0)
        polygon([[0, eps], [0, -lip_chamfer], [lip_chamfer, 0], [lip_chamfer, eps]]);
}

// plate top (y=top_y) on the bed: cages stand up, fillets are 45° slopes on the lip
module lid_print() { translate([0, -body_z0, top_y]) rotate([-90, 0, 0]) lid(); }

if (is_undef(ASSEMBLY)) {
    echo(lid_size=lid_size());
    if (for_print) lid_print(); else lid();
}
