.PHONY: all check-example count bundle

PYTHON ?= python3
FIGURES = tikz/flow_chart/flow_chart.pdf

all: $(FIGURES)
	latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex

paper.pdf: all

tikz/%.pdf: tikz/%.tex
	latexmk -cd -pdf -interaction=nonstopmode -halt-on-error $<

check-example:
	$(PYTHON) examples/parse_recorded_transaction.py --check
	$(PYTHON) examples/verify_recording.py

count:
	texcount -inc -sum paper.tex

bundle: all
	$(PYTHON) build_submission.py
