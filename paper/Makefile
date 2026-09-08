.PHONY: all check-example count bundle

PYTHON ?= python3

all:
	latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex

check-example:
	$(PYTHON) examples/parse_recorded_transaction.py --check

count:
	texcount -inc -sum paper.tex

bundle: all
	$(PYTHON) build_submission.py
