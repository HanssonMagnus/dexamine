# SoftwareX manuscript

`paper.tex` is the editable manuscript source for an **Original Software Publication**
in SoftwareX. `paper.pdf` is the compiled manuscript, and `paper.bib` holds its references.
The source follows Elsevier's [official LaTeX template](https://legacyfileshare.elsevier.com/promis_misc/softwarex-osp-template.tex)
and [Word template, version 6, March 2026](https://legacyfileshare.elsevier.com/promis_misc/softwarex-osp-template.docx).
The template specifies five main sections, a code metadata table, about 100 abstract
words, at most six keywords, a 4,000-word limit and at most six figures. Its main-text
page target is six pages, excluding metadata, tables, figures and references.

## Build

Install a TeX distribution with `elsarticle`, `latexmk`, `xurl`, `microtype`, `listings`,
`tabularx` and `booktabs`. On Ubuntu:

```bash
sudo apt-get install latexmk texlive-publishers texlive-latex-extra texlive-fonts-recommended
make -C paper
make -C paper count
```

The PDF uses the template's preprint layout and numbered references. The word count
excludes the code metadata table and bibliography; inspect the abstract, captions and
code listing as well when evaluating the journal's limit.

## Reproduce the example

Install the package following the repository README, then run:

```bash
python paper/examples/parse_recorded_transaction.py --check
```

See [examples/README.md](examples/README.md) for the recorded transaction, transport
replay, supplied metadata and optional live-node execution. The expected output is
tracked, and CI checks it on every paper build. No live node is needed for the default
example. The code metadata table points to the public v1.0.0 software release; the
example and manuscript are maintained in this directory.

## Assemble submission files

```bash
make -C paper bundle
```

This creates `paper/submission/paper.pdf`, `highlights.txt`, `cover-letter.txt` and `latex-source.zip`.
The source archive includes the manuscript, bibliography, generated reference list,
and Elsevier class and bibliography style. Other TeX packages come from the TeX
distribution. Generated submission files are ignored by Git.

[The paper workflow](../.github/workflows/draft-pdf.yml) checks the example, builds
the manuscript, and uploads these files as an artifact. The `tikz/` directory retains
previous figure sources; the current manuscript does not include those figures.
