.PHONY: setup fetch eval web serve clean

PY=python

setup:
	$(PY) -m venv .venv && . .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

fetch:
	$(PY) scripts/fetch_paths.py --bbox -84.30 30.43 -84.28 30.46 --out data/paths_osm.geojson

eval:
	$(PY) scripts/eval_ada.py --dem data/dem.tif --paths data/paths_osm.geojson --out outputs/paths_ada_eval.geojson

web:
	cp outputs/paths_ada_eval.geojson web/paths_ada_eval.geojson

serve:
	cd web && $(PY) -m http.server 8080

clean:
	rm -f outputs/paths_ada_eval.geojson web/paths_ada_eval.geojson
