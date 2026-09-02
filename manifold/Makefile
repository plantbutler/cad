# Plant Butler manifold v3 — export, preview and check every part.
#
#   make stl     build/stl/<part>.stl for every parts/*.scad (-D for_print=true), each one
#                verified to be a single solid ("Simple: yes", "Volumes: 2")
#   make png     renders/<part>.png previews and renders/assembly_<view>.png for every view
#   make check   every part and the assembly evaluated with the default parameters and with
#                each alternate set below; a set that cannot be built must fail with an assert
#   make report  echo every derived number from params.scad
#   make clean   remove build/ (renders/ is committed: regenerate it with make png)
#
# Parts are found by globbing parts/*.scad: a new part needs no Makefile change.
# GNU make 3.81 (macOS) compatible: no $(file), no shortest-stem rule ordering.

OPENSCAD ?= /Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD
IMG      ?= 1200,900
CAM      ?= --autocenter --viewall --camera=0,0,0,55,0,25,0 --projection=o --colorscheme=Tomorrow
ASM_OPTS ?= --projection=o --colorscheme=Tomorrow   # the assembly echoes its own --camera per view
PNG_MAX_KB ?= 150

PARTS := $(sort $(basename $(notdir $(wildcard parts/*.scad))))
LIBS  := $(wildcard lib/*.scad)
VIEWS := iso length gate between cart front
# Alternate parameter sets from the brief (name=value, one variable each).
SETS  := lift_factor=1 lift_factor=3 ball_d=10 oring_cs=2 n_gates=3 inner_w=20 gear_module=1

STLS      := $(PARTS:%=build/stl/%.stl)
PART_PNGS := $(PARTS:%=renders/%.png)
ASM_PNGS  := $(if $(wildcard assembly.scad),$(VIEWS:%=renders/assembly_%.png))   # none until the assembly exists

.PHONY: all stl png check check-params check-parts check-assembly report clean

all: stl png

# ---- stl -------------------------------------------------------------------------------------
# The export summary of a boolean is a CGAL Nef polyhedron: "Simple: yes" and "Volumes: 2"
# (outer volume + one solid) mean one watertight body. A bare primitive prints "Facets" instead:
# wrap such a part in a difference() with a hole it has anyway.
stl: $(STLS)

build/stl/%.stl: parts/%.scad params.scad $(LIBS)
	@mkdir -p build/stl
	$(OPENSCAD) -o $@ -D for_print=true $< 2> build/stl/$*.log || { cat build/stl/$*.log; exit 1; }
	@grep -q 'Simple: *yes' build/stl/$*.log && grep -qE 'Volumes: +2$$' build/stl/$*.log \
	  || { cat build/stl/$*.log; echo "$*: not a single solid"; exit 1; }
	@grep -E 'WARNING|ECHO' build/stl/$*.log || true

# ---- png -------------------------------------------------------------------------------------
png: $(PART_PNGS) $(ASM_PNGS)

# assembly rule first: make 3.81 takes the first pattern rule whose prerequisites exist.
# Two passes: an .echo export (evaluation only, fast) yields the camera the assembly computes
# for the view — --viewall is useless on a sectioned preview, it fits the uncut leaves — then
# the preview is rendered with it.
renders/assembly_%.png: assembly.scad params.scad $(LIBS) $(wildcard parts/*.scad)
	@mkdir -p renders build
	@$(OPENSCAD) -o build/assembly_$*.echo -D 'view="$*"' assembly.scad > build/assembly_$*.log 2>&1 \
	  && ! grep -q 'ERROR' build/assembly_$*.echo build/assembly_$*.log \
	  || { grep -hE 'ERROR|WARNING' build/assembly_$*.echo build/assembly_$*.log; exit 1; }
	cam=$$(sed -n 's/^ECHO: camera = "\(.*\)"$$/\1/p' build/assembly_$*.echo); \
	  [ -n "$$cam" ] || { echo "assembly_$*: no camera echoed"; exit 1; }; \
	  $(OPENSCAD) -o $@ --imgsize=$(IMG) $(ASM_OPTS) --camera=$$cam -D 'view="$*"' assembly.scad >> build/assembly_$*.log 2>&1 \
	  || { cat build/assembly_$*.log; exit 1; }
	@grep -hE 'WARNING' build/assembly_$*.log || true
	@$(call png_size,$@)

renders/%.png: parts/%.scad params.scad $(LIBS)
	@mkdir -p renders build
	$(OPENSCAD) -o $@ --imgsize=$(IMG) $(CAM) $< 2> build/png_$*.log || { cat build/png_$*.log; exit 1; }
	@$(call png_size,$@)

# renders are committed: keep each under PNG_MAX_KB
define png_size
s=$$(wc -c < $(1)); if [ $$s -gt $$(( $(PNG_MAX_KB) * 1024 )) ]; then \
  echo "WARNING: $(1) is $$s bytes (> $(PNG_MAX_KB) KB): lower IMG"; fi
endef

# ---- check -----------------------------------------------------------------------------------
# Every part and the assembly, with the defaults and with each SETS entry. Parts take the
# override as -D (params.scad is included, so the -D reaches it). The assembly `use`s the
# parts, and a -D does not reach a used file, so for it the whole tree is copied to
# build/check/<set>/ with the override substituted into that copy's params.scad (sed on the
# first assignment; the copy is then grepped to prove the substitution happened). Parts are
# exported as STL (the single-solid test); the assembly is evaluated with an .echo export
# (no CSG, so it is quick). That pass runs params.scad's top-level asserts and echoes (it is
# `include`d) and the asserts inside the parts' module bodies (every part keeps its asserts
# there); a `use`d file's top-level statements never execute, so a statement at a part
# file's top level is only exercised by check-parts or by rendering that part on its own,
# not by the assembly alone (GUI work on assembly.scad, `make png`).
# OpenSCAD 2021.01 exits 0 on a failed assert (the ERROR goes to the console, or into the
# .echo file), so every check greps for ERROR.
check: check-params check-parts check-assembly

build/report.scad: params.scad
	@mkdir -p build
	@printf 'include <../params.scad>\nreport();\n' > $@

report: build/report.scad
	$(OPENSCAD) -o build/report.echo $< 2>&1 | grep -E 'WARNING|ERROR' || true
	@cat build/report.echo

check-params: build/report.scad
	@fail=0; for s in default $(SETS); do d=$$(echo $$s | tr = -); mkdir -p build/check/$$d; \
	  dopt=$$( [ $$s = default ] || echo "-D $$s" ); \
	  if $(OPENSCAD) -o build/check/$$d/params.echo $$dopt build/report.scad > build/check/$$d/params.log 2>&1 \
	     && ! grep -q 'ERROR' build/check/$$d/params.echo build/check/$$d/params.log; \
	  then echo "params  $$s: ok"; else echo "params  $$s: FAIL"; grep -hE 'ERROR|WARNING' build/check/$$d/params.echo build/check/$$d/params.log; fail=1; fi; \
	done; exit $$fail

check-parts:
	@fail=0; for p in $(PARTS); do for s in default $(SETS); do d=$$(echo $$s | tr = -); mkdir -p build/check/$$d; \
	  dopt=$$( [ $$s = default ] || echo "-D $$s" ); log=build/check/$$d/$$p.log; \
	  if $(OPENSCAD) -o build/check/$$d/$$p.stl -D for_print=true $$dopt parts/$$p.scad > $$log 2>&1 \
	     && ! grep -q 'ERROR' $$log && grep -q 'Simple: *yes' $$log && grep -qE 'Volumes: +2$$' $$log; \
	  then echo "$$p  $$s: ok"; else echo "$$p  $$s: FAIL"; grep -E 'ERROR|WARNING|Volumes|Simple' $$log; fail=1; fi; \
	done; done; exit $$fail

check-assembly:
	@if [ ! -f assembly.scad ]; then echo "assembly.scad not present yet: skipped"; exit 0; fi; \
	fail=0; for s in default $(SETS); do d=$$(echo $$s | tr = -); t=build/check/$$d/tree; \
	  rm -rf $$t; mkdir -p $$t; cp -R lib parts assembly.scad $$t/; \
	  if [ $$s = default ]; then cp params.scad $$t/params.scad; else \
	    n=$${s%%=*}; v=$${s#*=}; \
	    sed -E "s/(^|[^A-Za-z0-9_])$$n *= *[^;]*;/\1$$n = $$v;/" params.scad > $$t/params.scad; \
	    grep -qE "(^|[^A-Za-z0-9_])$$n = $$v;" $$t/params.scad || { echo "assembly  $$s: could not substitute $$n in params.scad"; fail=1; continue; }; \
	  fi; \
	  log=build/check/$$d/assembly.log; e=build/check/$$d/assembly.echo; \
	  if $(OPENSCAD) -o $$e $$t/assembly.scad > $$log 2>&1 \
	     && ! grep -q 'ERROR' $$e $$log && grep -q 'ECHO: camera' $$e; \
	  then echo "assembly  $$s: ok"; else echo "assembly  $$s: FAIL"; grep -hE 'ERROR|WARNING' $$e $$log; fail=1; fi; \
	done; exit $$fail

# ---- clean -----------------------------------------------------------------------------------
clean:
	rm -rf build
