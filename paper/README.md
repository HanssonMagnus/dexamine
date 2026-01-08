# Paper

## Compile the paper locally
You can compile your JOSS paper locally before submitting it to GitHub. JOSS uses a
lightweight markdown-based system for the paper, and you can build it locally using a
simple LaTeX environment.

JOSS uses pandoc to convert markdown into LaTeX and then PDF. Therefore you'll need both
`pandoc` and a LaTeX distribution like TeX Live. If you are using apt install `pandoc`
from their website instead, since the apt version does not have `citeproc`.

To compile the paper you need `paper.md` and `paper.bib` in a directory.

```bash
.
├── paper.md
├── paper.bib
└── paper.pdf   (this will be created after running `make` or `pandoc`)
```

To compile, run the following command:

```bash
pandoc paper.md --citeproc --bibliography=bibliography.bib -o paper.pdf
```

## Convert tikz pdfs to png

E.g., run the following command to create a `png` from the `pdf` for the event
classification flow chart,
```
convert -density 1000 event_classification.pdf -strip -quality 100 event_classification.png
```
