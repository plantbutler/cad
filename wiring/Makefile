# Bench wiring drawings and README: run from anywhere as `make -C cad/wiring`.
# uv fetches schemdraw + matplotlib into an ephemeral env; no project venv needed.

UV       := PYTHONDONTWRITEBYTECODE=1 uv run --with schemdraw --with matplotlib python
DRAWINGS := overview pump-driver sensor-bus power
SVGS     := $(DRAWINGS:%=%.svg)
PNGS     := $(DRAWINGS:%=%.png)

.PHONY: all drawings readme clean

all: drawings readme

drawings:
	$(UV) draw.py

readme:
	@if [ -f gen_readme.py ]; then $(UV) gen_readme.py; \
	else echo "readme: gen_readme.py not written yet (README.md unchanged)"; fi

clean:
	rm -f $(SVGS) $(PNGS)
	rm -rf __pycache__
