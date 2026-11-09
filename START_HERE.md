# Start here

**Recovery-Time Guarantees for Safety Filtering under Sampled Actuation**

Hossein Nick Zinat Matin and Lipem Likwai Momnougui  
Laboratory of Computer Science (LIX), Ecole Polytechnique

Scientific release: paper Revision 11 and technical notes version 1.2, dated
8 November 2026. Repository packaging updated 9 November 2026.

## Read the documents

- [Conference paper, 8 pages](pdf/ECC_revision_v11_2026-11-08.pdf)
- [Complete technical notes, 81 pages](pdf/ECC_revision_v11_technical_notes_2026-11-08.pdf)
- [Repository and reproduction instructions](README.md)
- [Citation information](CITATION.cff)
- [MIT license for original software](LICENSE)
- [CC BY 4.0 license for notes, original figures and data](LICENSE-CC-BY-4.0.txt)
- [License scope and exceptions](LICENSE-SCOPE.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)
- [Release history](CHANGELOG.md)
- [Release checklist](RELEASE_CHECKLIST.txt)

## Check the download

The ZIP contains repository files directly at its top level. After extracting
the whole ZIP, README.md, LICENSE, CITATION.cff, reproduce.py, and the manuscript/
and pdf/ directories must be visible together. companion.tex is an editable
entry point inside manuscript/; it is only one of the release files.

From that directory, run:

```bash
python3 reproduce.py --verify
```

This standard-library-only command checks the supplied file hashes and dataset
counts. Reading the PDFs does not require installing the numerical dependencies.

For GitHub, place this entire extracted file tree at the repository root,
including .github/ and .gitignore. The root README will then appear on the
repository homepage. The approved licenses and their component scope are
included in LICENSE, LICENSE-CC-BY-4.0.txt and LICENSE-SCOPE.md. The release
checklist records the remaining publication actions.
