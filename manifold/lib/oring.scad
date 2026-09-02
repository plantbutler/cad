// lib/oring.scad — O-rings: the ghost for the assembly and the counterbore that seats one.
// Both about +Z. The caller's $fn sets the roundness.

// O-ring ghost: torus of inner diameter id and cross-section cs, tube centre in the plane z=0
// (place it at y_ring). Centreline radius (id + cs)/2.
module oring(id, cs) {
    rotate_extrude() translate([(id + cs)/2, 0]) circle(d=cs);
}

// Cutter for the seat: a cylinder ø(id + 2 cs + clear), the ring's OD plus radial slack, from
// `depth` below z=0 to `overshoot` above it. Put z=0 on the face the ring drops into, +Z out
// of the material; the ring's ID then lands on the hole edge when id equals the hole diameter.
module oring_counterbore(id, cs, clear, depth, overshoot=0.01) {
    translate([0, 0, -depth]) cylinder(d=id + 2*cs + clear, h=depth + overshoot);
}
