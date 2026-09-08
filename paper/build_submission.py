"""Assemble manuscript files for SoftwareX; run from any working directory."""

from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

paper = Path(__file__).resolve().parent
output = paper / "submission"
output.mkdir(exist_ok=True)
for name in ("paper.pdf", "highlights.txt", "cover-letter.txt"):
    shutil.copyfile(paper / name, output / name)
with ZipFile(output / "latex-source.zip", "w", ZIP_DEFLATED) as archive:
    for name in ("paper.tex", "paper.bib", "paper.bbl"):
        archive.write(paper / name, name)
    for name in ("elsarticle.cls", "elsarticle-num.bst"):
        source = subprocess.check_output(["kpsewhich", name], text=True).strip()
        if not source:
            raise SystemExit(f"Missing LaTeX dependency: {name}")
        archive.write(source, name)
print(f"Submission files written to {output}")
