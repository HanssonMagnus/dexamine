.PHONY: all check-example count bundle

PYTHON ?= python3
FIGURES = tikz/flow_chart/flow_chart.pdf tikz/event_classification/event_classification.pdf

all: paper.pdf

paper.pdf: paper.tex paper.bib $(FIGURES)
	latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex

tikz/%.pdf: tikz/%.tex
	latexmk -cd -pdf -interaction=nonstopmode -halt-on-error $<

check-example:
	$(PYTHON) examples/parse_recorded_transaction.py --check
	$(PYTHON) examples/verify_recording.py

count:
	texcount -inc -sum paper.tex

bundle: all
	$(PYTHON) build_submission.py
