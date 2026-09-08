# Paper

This directory holds the JOSS paper for `dexamine`.

```text
.
├── paper.md                 # the paper (JOSS markdown + YAML frontmatter)
├── paper.bib                # references
├── paper.pdf                # built output
└── tikz/                    # retained figure sources (not used in the paper)
    ├── event_classification/
    └── flow_chart/
```

## Build the paper

The paper is built on every push by
[`.github/workflows/draft-pdf.yml`](../.github/workflows/draft-pdf.yml), which uploads
`paper.pdf` as a workflow artifact.

To build it locally with the same toolchain JOSS uses, run the Open Journals `inara`
image from the repository root:

```bash
docker run --rm -v "$PWD/paper":/data -u $(id -u):$(id -g) \
    -e JOURNAL=joss openjournals/inara
```

The workflow builds from the checked-out sources without restoring the paper directory
from a cache, so bibliography and figure changes cannot reuse a stale PDF.

A plain `pandoc` build is also possible, but it will not apply the JOSS template:

```bash
pandoc paper/paper.md --citeproc --bibliography=paper/paper.bib -o paper/paper.pdf
```

## Rebuild a figure

Each figure is a standalone TikZ document. To rebuild the routing figure and export the
PNG that `paper.md` embeds:

```bash
cd tikz/event_classification
pdflatex event_classification.tex
convert -density 600 event_classification.pdf -strip -quality 100 \
    event_classification.png
```

The same applies to `tikz/flow_chart`. LaTeX build artifacts (`.aux`, `.log`, ...) are
gitignored; the `.tex`, `.pdf` and `.png` files are tracked.
