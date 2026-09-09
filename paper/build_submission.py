"""Assemble arXiv sources and the recorded example; run from any directory."""

from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

paper = Path(__file__).resolve().parent
output = paper / "submission"
output.mkdir(exist_ok=True)
shutil.copyfile(paper / "paper.pdf", output / "paper.pdf")
with ZipFile(output / "recorded-example.zip", "w", ZIP_DEFLATED) as archive:
    for source in sorted((paper / "examples").rglob("*")):
        if source.suffix in {".py", ".json", ".md"}:
            archive.write(source, source.relative_to(paper))
    archive.write(paper.parent / "LICENSE", "LICENSE")
with ZipFile(output / "arxiv-source.zip", "w", ZIP_DEFLATED) as archive:
    for name in (
        "paper.tex",
        "paper.bib",
        "paper.bbl",
        "tikz/flow_chart/flow_chart.pdf",
    ):
        archive.write(paper / name, name)
    archive.write(output / "recorded-example.zip", "anc/recorded-example.zip")
print(f"Submission files written to {output}")
