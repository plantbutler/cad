// lib/shapes.scad — geometry helpers shared by every part. `use` it: it defines no variables.
// $fn is dynamically scoped, so round things here take the caller's $fn: set `$fn = fn_round;`
// at the top of a part file (after the include) and pass `$fn = fn_small` on small features.

// 2D rectangle `size` = [w, h] with its four corners cut at 45° by c.
// Corner at the origin unless center=true.
module chamfered_rect(size, c, center=false) {
    translate(center ? [-size.x/2, -size.y/2] : [0, 0])
        polygon([[c, 0], [size.x - c, 0], [size.x, c], [size.x, size.y - c],
                 [size.x - c, size.y], [c, size.y], [0, size.y - c], [0, c]]);
}

// 2D rectangle `size` = [w, h] with its four corners rounded by r.
// Corner at the origin unless center=true.
module rounded_rect(size, r, center=false) {
    translate(center ? [0, 0] : [size.x/2, size.y/2])
        offset(r=r) square([size.x - 2*r, size.y - 2*r], center=true);
}

// Box `size` = [x, y, z] with all twelve edges chamfered at 45° by c: the hull of three boxes,
// each shrunk by c along two of its axes, is exactly that.
// Corner at the origin unless center=true.
module chamfered_box(size, c, center=false) {
    translate(center ? -size/2 : [0, 0, 0]) hull() {
        translate([c, c, 0]) cube([size.x - 2*c, size.y - 2*c, size.z]);
        translate([c, 0, c]) cube([size.x - 2*c, size.y, size.z - 2*c]);
        translate([0, c, c]) cube([size.x, size.y - 2*c, size.z - 2*c]);
    }
}

// Hexagonal prism (nut, nut trap): across-flats af, height h along +Z from z=0
// (center=true: centred on z=0). Corners on ±X, flats at y = ±af/2.
module hex(af, h, center=false) {
    cylinder(d=af/cos(30), h=h, center=center, $fn=6);
}

// Torus about Z: centreline radius R, tube radius r, tube centre in the plane z=0.
// The ring takes the caller's $fn; fn_tube (default: the same) sets the tube's.
module torus(R, r, fn_tube) {
    rotate_extrude() translate([R, 0]) circle(r=r, $fn=is_undef(fn_tube) ? $fn : fn_tube);
}

// 2D right triangle: right angle at the origin, leg a along +X, leg b along +Y (b defaults
// to a: a 45° chamfer or gusset). Mirror/rotate it into place, then linear_extrude.
module right_triangle(a, b) {
    polygon([[0, 0], [a, 0], [0, is_undef(b) ? a : b]]);
}

// Section helpers for renders: keep only the part of the children whose coordinate along
// axis ("x" | "y" | "z") is below (keep_below) or above (keep_above) `at`.
// `big` must exceed the model's extent in every direction.
module keep_below(axis, at, big=1000) {
    difference() { children(); translate(_axis_vec(axis)*(at + big)) cube(2*big, center=true); }
}
module keep_above(axis, at, big=1000) {
    difference() { children(); translate(_axis_vec(axis)*(at - big)) cube(2*big, center=true); }
}
function _axis_vec(axis) = axis == "x" ? [1, 0, 0] : axis == "y" ? [0, 1, 0] : [0, 0, 1];
