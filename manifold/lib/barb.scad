// lib/barb.scad — hose barb: a rotate_extrude of a 2D (r, z) profile, axis +Z from z=0.
// Reproduces valveV2's connector (outlet, flanged) and connector_8mm (inlet) sketches:
//   a shank of shank_d carrying `ridges` crests of ridge_d; each crest rises on a face `steep`°
//   from the axis (on the base side) and tapers back to the shank over taper_len; the last
//   taper ends at tip_d on the end face z=len; bore through.
//   flange = [d, h]: a cone from ø d on z=0 to the shank at z=h (v2 exitSupport), undef = none.
//   gap: shank between the end of one taper and the next crest. v2 constrains it to 2 in both
//   sketches (DistanceX 2), so the 9-argument call reproduces v2; params.scad's barb_ridge_gap
//   is the same number for callers that want it explicit.
// The caller's $fn sets the roundness (use fn_round: these seal).

// z of crest i (0-based, counted from the base): the last crest is taper_len short of the end.
function barb_crest_z(len, ridges, taper_len, gap, i) = len - taper_len - (ridges - 1 - i)*(taper_len + gap);
// axial length of a crest's steep rise
function barb_rise_dz(shank_d, ridge_d, steep) = (ridge_d - shank_d)/2/tan(steep);

// Drop consecutive duplicate points (a rise that starts exactly where the shank starts).
function _dedupe(p, i=0, acc=[]) =
    i >= len(p) ? acc
    : _dedupe(p, i + 1, (len(acc) > 0 && norm(p[i] - acc[len(acc) - 1]) < 1e-9) ? acc : concat(acc, [p[i]]));

// The (r, z) polygon: base face, shank, crests, end face, back along the bore.
function barb_profile(bore, shank_d, ridge_d, len, ridges, taper_len, tip_d, steep, flange, gap=2) =
    let(rb = bore/2, rs = shank_d/2, rr = ridge_d/2, rt = tip_d/2,
        dz = barb_rise_dz(shank_d, ridge_d, steep),
        z_shank0 = is_undef(flange) ? 0 : flange[1],
        base = is_undef(flange) ? [[rb, 0], [rs, 0]] : [[rb, 0], [flange[0]/2, 0], [rs, flange[1]]],
        crests = [for (i = [0 : ridges - 1]) let(zc = barb_crest_z(len, ridges, taper_len, gap, i))
                    each [[rs, zc - dz], [rr, zc], i == ridges - 1 ? [rt, len] : [rs, zc + taper_len]]],
        ok = assert(ridges >= 1, "barb: ridges >= 1")
             assert(rr > rs && rs > rb && rt >= rb, "barb: need ridge_d > shank_d > bore and tip_d >= bore")
             assert(barb_crest_z(len, ridges, taper_len, gap, 0) - dz >= z_shank0 - 1e-9,
                    "barb: first crest rises before the shank starts: shorter flange, fewer ridges or a longer barb")
             assert(gap >= dz - 1e-9, "barb: gap shorter than the crest rise")
             true)
    _dedupe(concat(base, crests, [[rb, len]]));

module barb(bore, shank_d, ridge_d, len, ridges, taper_len, tip_d, steep, flange, gap=2) {
    rotate_extrude()
        polygon(barb_profile(bore, shank_d, ridge_d, len, ridges, taper_len, tip_d, steep, flange, gap));
}
