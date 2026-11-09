# Recovery-Time Guarantees for Safety Filtering under Sampled Actuation

**V11 reproducibility snapshot — 8 November 2026. Technical notes version 1.2.**
Prepared for an **ECC 2027 submission**; this description does not assert acceptance.

**Authors:** Hossein Nick Zinat Matin and Lipem Likwai Momnougui, Laboratory of Computer Science (LIX), Ecole Polytechnique.

Repository destination: [hosein-matin/Recovery-time-safety](https://github.com/hosein-matin/Recovery-time-safety). This package supplies source and research artifacts; no Git commit, release tag, DOI, or ORCID is asserted. See `CITATION.cff` and `RELEASE_CHECKLIST.txt`.

## Start here

**Repository packaging updated 9 November 2026; scientific files remain V11 / notes 1.2.**
The ZIP places these files directly at its root. See [START_HERE.md](START_HERE.md)
for a short index. The repository metadata are [CITATION.cff](CITATION.cff),
[LICENSE](LICENSE), [LICENSE-CC-BY-4.0.txt](LICENSE-CC-BY-4.0.txt),
[LICENSE-SCOPE.md](LICENSE-SCOPE.md), [.gitignore](.gitignore),
[CHANGELOG.md](CHANGELOG.md), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md),
and [CONTRIBUTING.md](CONTRIBUTING.md). Original software and usage documentation
are licensed under MIT; technical notes, original accompanying figures and
generated experimental data are licensed under CC BY 4.0. See the scope file
for component boundaries and the conference-paper and third-party exceptions.

The conference manuscript is `pdf/ECC_revision_v11_2026-11-08.pdf`; complete proofs, scope, numerical protocols, and reproducibility details are in `pdf/ECC_revision_v11_technical_notes_2026-11-08.pdf`. Editable entry points are `manuscript/main.tex` and `manuscript/companion.tex`.

Run all commands below **from the package root**. The wrapper resolves internal paths and working directories. It does not require users to provide an internal `--legacy` path.

```bash
python3 reproduce.py --verify
python3 reproduce.py --render-only
```

`--verify` reads the supplied `SHA256SUMS.txt`, counts the release records, checks the historical hold total, and confirms that six policy archives exist. It needs only the Python standard library and does not modify the package. A checksum mismatch is a failed integrity check: use a clean, finalized snapshot, or reconcile a deliberate change and regenerate the release manifest before distribution. Hash checking establishes byte integrity, not mathematical validity.

`--render-only` builds **both PDFs from supplied figures, tables, and bibliography sources**. No simulation, HJB solve, or interval-certificate recomputation is needed. It uses the portable `manuscript/build.sh` with ordinary `pdflatex` and `bibtex`; it does not depend on a private cached TeX format. The resulting PDFs are placed in the isolated run's `pdf/` directory. Overleaf users may select `main.tex` or `companion.tex` within `manuscript/`.

## Environment

Python 3.12 is the recorded interpreter series. Install the pinned numerical dependencies into an environment of your choice:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

The pins are NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, pypdf 6.10.0, and mpmath 1.3.0. Rendering requires a TeX Live installation with `pdflatex`, `bibtex`, IEEEtran, the usual AMS and graphics packages, and the packages named in the document preambles. A typical Debian/Ubuntu installation uses `texlive-latex-extra`, `texlive-fonts-recommended`, `texlive-science`, and `texlive-publishers`. HJB regeneration requires a C++ compiler; sampled and fixed-period wrapper commands compile the outward arithmetic helper using `cc`. The Python helper implementation is retained in the package, but these wrapper paths request the compiled configuration used for the recorded runs.

The Linux production drivers use process workers; the sampled matrix explicitly uses the `fork` multiprocessing context. Linux is the supported direct execution environment, including Linux containers or WSL. The wrapper fixes `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, and `OMP_NUM_THREADS` to one so each worker does not spawn an additional numerical thread pool.

## Reproduce a component

Every execution command creates a fresh directory at `output/reproduced/<UTC timestamp>-<action>/`, copies the package there, and runs inside that copy. Existing output trees, virtual environments, Python caches, Git metadata, and compiled shared objects are excluded. The supplied release data therefore remain intact. Each run has `reproduction_run.json` with the input location, commands, return codes, elapsed times, and completion state. A failed command retains its partial output and stops the wrapper.

| Goal | Root command | What is computed |
|---|---|---|
| Regenerate six HJB action tables | `python3 reproduce.py --hjb` | Runs `scripts/reproduce_hjb_policies.py`; compares all `t`, `d`, `v`, and `u` arrays against the six supplied archives and fails if any array differs. |
| Continuous appendix | `python3 reproduce.py --continuous --fresh --workers 4` | Runs the 936 base episodes and 504 refinements, then refreshes manuscript assets. |
| Continuous kernel benchmark | `python3 reproduce.py --continuous-benchmark` | Runs the separate serial profile-preparation and supplied-state controller microbenchmark. |
| New fixed-period matrix | `python3 reproduce.py --fixed-periods --fresh --workers 3` | Prepares the .01 witnesses using the supplied rigorous profile enclosures, runs all 192 cases at .01/.025, audits them, and copies the regenerated overview figure and two tables into the manuscript. |
| New serial timing | `python3 reproduce.py --fixed-benchmark` | Replays all pre-entry decisions from 16 declared stress episodes in one process, checks each reproduced decision, refreshes timing-dependent summaries, and updates the corresponding manuscript assets. |
| Historical sampled protocol | `python3 reproduce.py --sampled --fresh --workers 4` | Reexecutes the final sampled implementation over the 360-case base/sweep protocol, then refreshes its summaries and manuscript assets. |
| Historical serial benchmark | `python3 reproduce.py --sampled-benchmark` | Executes the separately defined sampled decision benchmark and refreshes its summaries and manuscript assets. |
| Analytic and uniform certificates | `python3 reproduce.py --certificates` | Performs the 51-check analytic verification, recomputes the uniform .025 interval certificate, and updates the manuscript's certificate table and budget figure. This is the potentially long, hours-scale offline calculation. |
| Compile documents | `python3 reproduce.py --render-only` | Builds both PDFs using the supplied assets. |
| Check supplied integrity/counts | `python3 reproduce.py --verify` | Read-only checksum/count audit; does not run numerical calculations. |

Fresh simulation is the default; `--fresh` makes that choice explicit. `--reuse` deliberately permits existing case caches. For the continuous driver, this enables its resume mode. The fixed-period driver always recomputes every requested case, even if `--reuse` is passed; this avoids source-only cache keys omitting changed policy or certificate data. The wrapper removes only that isolated copy's case cache in fresh mode. Fresh simulation still uses supplied frozen HJB policies and rigorous offline certificate/profile inputs: regenerate those components separately when needed.

Use `--plan` with any execution action to print its exact command sequence without copying or executing. Use `--output-root PATH` to choose the parent output directory. To build upon a previous isolated result without modifying it, pass `--from-run`:

```bash
python3 reproduce.py --fixed-benchmark --from-run output/reproduced/<completed-fixed-period-run>
python3 reproduce.py --render-only --from-run output/reproduced/<completed-analysis-run>
```

Each invocation recomputes only the selected component. For example, a fresh matrix run retains the supplied serial timing record unless `--fixed-benchmark` or `--sampled-benchmark` is then requested. Report a new timing measurement only from the relevant benchmark output. The original release checksum manifest remains a record of delivered inputs; it is expected to differ after intentionally recomputing files in a run directory.

After the sampled, fixed-period, or certificate analysis completes, the wrapper calls `scripts/refresh_manuscript_assets.py` inside the isolated copy. The sampled refresh transfers all generated figure PDFs/PNGs and tables, including the notes-only figures, and derives main Tables II–IV directly from the base episode CSV. In Table II, the progress controller's floor departures are counted using `floor_min_diagnostic < -1e-8` and marked as diagnostic; the retained data give 55. Table III's four median/maximum rows use three decimal places, and Table IV uses the original raw paired threshold `1e-10`. This separate reporting step preserves the historical generators and their source hashes.

The fixed-period refresh copies `fixed_period_overview.pdf` into `manuscript/figures/v11/` and both `fixed_period_overview.tex` and `historical_comparison.tex` into `manuscript/tables/v11/`. The certificate refresh copies the generated ratio table to `manuscript/tables/period_certificate.tex` and the budget figure to `manuscript/figures/period_certificate_budget_profiles.pdf`. Each refresh records its source/destination files and hashes in `output/manuscript_asset_refresh_<component>.json` inside the run. `--render-only` then compiles the prepared manuscript assets; it performs no numerical refresh or simulation.

## What the three experiment histories mean

The **historical continuous study** is in `numerics_v6/`, with 936 base episodes and 504 refined episodes. Its event-driven continuous controller and post-entry policy differ from the sampled study. Its comparisons and timing cannot be pooled with sampled-controller results.

The **retained historical sampled study** is in `numerics_v7/`: **360 records and 64,067 recorded holds**, comprising 288 base records and 72 selected period-sweep records. The base matrix uses requested period .05. It contains 96 matched band/progress pairs, plus the naive comparison. This release retains those results and their earlier source/provenance records; preparation of the V11 fixed-period matrix did not rerun that historical matrix. Historical filenames and source hashes intentionally remain historical. The per-trajectory .05 checks are not a uniform .05 period theorem.

The **new V11 fixed-period study** is in `fixed_period_experiments/`: **192 runs**, with 96 at .01 and 96 at .025. Its controller first tests the clipped nominal over a complete hold and otherwise uses a stored clearance witness. The full matrix, source hashes, certificate provenance, whole-hold audits, and separate serial decision replay are recorded there. Its numerical results are not substituted for historical .05 rows. See `fixed_period_experiments/METHOD.txt`, `protocol.json`, and `audit_results.json` for the exact protocol and scope.

The six supplied HJB policies remain the nominal inputs used in all reported comparisons. `reproducibility/hjb_policy_inventory.json` records their array and file metadata. `reproducibility/hjb_regeneration_check.json` records regeneration of all six policies with exact equality of all four arrays. Container metadata can change an NPZ archive's byte hash even when its mathematical arrays agree; the regeneration report makes that distinction explicit.

Directories named `numerics_v5`, `numerics_v6`, and `numerics_v7` are retained for data provenance and path compatibility. They identify experiment histories, not the current document version. The root wrapper is the current user entry point. Earlier README files document historical local workflows and should be read in that context.

## Paper and notes artifact map

Table and figure numbering below follows the V11 main manuscript. Theory tables/parameters remain authored LaTeX; derived figures and comparison tables are generated from the indicated retained data.

| Main artifact / notes topic | Editable or delivered artifact | Generator / underlying evidence |
|---|---|---|
| Table I: optimal-velocity models | `manuscript/sections/numerics_v7_main.tex` | Declared fixtures in `numerics_v7/reference_v6.py`, `fixed_period_experiments/protocol.json`; no statistical fit. |
| Table II: .05 domain/floor and entry outcomes | `manuscript/tables/v7/safety_summary.tex` | `scripts/refresh_manuscript_assets.py --sampled`, `numerics_v7/data/episodes.csv`; progress floor departures are counted at `-1e-8` and identified as diagnostic. |
| Table III: .05 entry ratios | `manuscript/tables/v7/rate_main.tex` | `scripts/refresh_manuscript_assets.py --sampled`; raw base entry times and clocks, 48 cases per row, three-decimal median/maximum formatting. |
| Table IV: .05 paired common-horizon comparisons | `manuscript/tables/v7/paired_counts.tex` | `scripts/refresh_manuscript_assets.py --sampled`; 96 base matched pairs from the episode CSV at a raw difference threshold of `1e-10`. |
| Figure 1: sample/hold failure and repair | `manuscript/figures/v7/sample_hold_failure_and_repair.pdf` | `numerics_v7/analyze_v7.py`, retained naive/band stress-case traces and full-hold residual checks. |
| Figure 2: new fixed-period overview | `manuscript/figures/v11/fixed_period_overview.pdf` | `fixed_period_experiments/analyze_results.py`; `data/rows.json`, `matched_pairs_full_precision.csv`, `serial_timing.json`. |
| Notes: fixed-period evidence and comparisons | `fixed_period_experiments/tables/`, `summary.csv`, `summary.json` | `run_matrix.py`, `audit_results.py`, `analyze_results.py`, `metric_sensitivity.py`; retained 192-run records and quadrature sensitivity. |
| Notes: full sampled tables and period sweep | `manuscript/tables/v7/all_*.tex`, `manuscript/sections/numerics_v7_full.tex` | `manuscript/make_v7_full_tables.py`, `numerics_v7/analyze_v7.py`, all 360 retained records. |
| Notes: HJB nominal construction | `manuscript/sections/hjb_nominal_full.tex`, `reproducibility/hjb_*.json` | `scripts/reproduce_hjb_policies.py`, `manuscript/numerics/engine.py`, `kernel.cpp`, six policies. |
| Notes: analytic period and offline uniform certificate | `manuscript/sections/period_ovm_full.tex`, `period_verification_full.tex`, `manuscript/tables/period_certificate.tex` | `sampling_certificate/ovm_analytic_constants.py`, `certify_balanced.py`, `make_certificate_summary.py`, JSON/NPZ certificate records. |
| Notes: continuous appendix | `manuscript/sections/numerics_v6_full.tex`, `manuscript/tables/v6/`, `manuscript/figures/v6/` | `numerics_v6/run_v6.py`, `benchmark_v6.py`, `manuscript/make_v6_paper_assets.py`, `data/episodes.csv`, `data/refinement.csv`. |
| Generic theorem constant displays | `reproducibility/generic_period_constants.csv` | `reproducibility/generate_release_diagnostics.py`; 24 plant/start/floor/target combinations. |
| Historical paired stratification | `reproducibility/historical_paired_strata.csv`, `release_diagnostics.json` | Same diagnostic script; partitions by plant, task, start speed, nominal, and floor fraction. Each partition sums to the global counts. |

The notes' opening paper-to-notes map gives the theorem and proof cross-references. Appendix and historical assets outside the main figure/table set are retained to support those extended sections.

## Precision, proof scope, and numerical diagnostics

Three different precision settings are intentional. The whole-hold trajectory residual routines use mpmath interval transcendental operations at **40 decimal digits**; the uniform offline certificate uses **45 decimal digits**; the analytic coefficient/contact/period checker uses **60 decimal digits**. All use **mpmath 1.3.0**. The supplied vendored mpmath copy supports the historical path. The outward binary64 helper is compiled with `-fno-fast-math -ffp-contract=off` and enlarges elementary results using `nextafter`.

Ordinary integration, entry-root estimates, cost and intervention quadrature, and motion diagnostics are binary64 numerical results. Dense plotted samples and numerical minima are useful diagnostics; the continuous residual tube and stored interval certificates provide the stated whole-hold evidence. In particular, an endpoint-only performance-floor check is unsound near a saturation kink: a residual can cross below zero inside the hold even when both endpoints pass. The manuscript describes the interval and kink-splitting checks used to avoid that error.

The periods .01 and .025 are sufficient **normalized model-time** periods for the declared exact-state OVM fixtures and target sets. They are not maximum allowable periods. Their proof does not establish uniform .05 feasibility, robustness to observation/model error, a physical sampling deadline, or universally lower cost/intervention/acceleration variation.

The generic-constant CSV evaluates

`P = alpha * (max(abs(V(epsilon)), abs(V(d0))) + M) + U`,
`L_B = M/gamma`,
`K = P + max(theta*max(P,L_B),L_B)`,
`S_e = d0-epsilon-.002`,
`S = d0-epsilon-target_x`,
`g = (1-theta)*.5*(.002/gamma)^2`, and
`delta_0 = min(S_e-S,g/(4*K))/M`.

It contains binary64 **display diagnostics of the theorem formula**, not a new rigorous certificate. The 24 displayed values range from approximately `5.8406974716e-8` to `2.1400719610e-7`. The much more useful fixture-specific .01/.025 results come from the separate analytic and interval constructions.

All matrices are deterministic enumerations of declared scenarios. There is no RNG or iid sampling model, and no inferential confidence interval is claimed. Lower/tied/higher counts and medians describe these finite matrices. The historical strata use the same raw `1e-10` tie threshold as their original paired summary; the newer fixed-period comparison script documents its metric-specific tolerances separately.

## Computation records

The new fixed-period environment records an **AMD EPYC 9V74 80-Core Processor**, nine available logical CPUs (affinity 0–8), three production workers, one BLAS/OpenMP thread per worker, and the compiler/configuration in `fixed_period_experiments/environment.json`. Production wall time and the exact serial results are in `fixed_period_experiments/data/run_summary.json` and `fixed_period_experiments/serial_timing.json`. The separate serial replay validates identical decisions before recording elapsed times.

The historical sampled serial record reports 312 band decisions with median **69.194 ms**, 95th percentile **124.257 ms**, and maximum **235.801 ms**; its progress comparison reports 299 decisions with median **2.500 ms**, 95th percentile **4.092 ms**, and maximum **10.255 ms** (`numerics_v7/timing_summary.json`). Its timing scope includes ODE proposals, continuous residual certification, profile queries, candidate search, and nominal evaluation, and excludes profile precomputation and the common tail. That historical benchmark record does not identify the CPU model; do not attribute the new fixed-period host model to it.

The continuous microbenchmark separately records median profile preparation **91.355 ms** and a median rate-kernel cost **17.973 microseconds**, with the exact scope in `numerics_v6/timing_summary.json`. These supplied-state kernel measurements are not full sampled decisions. Neither serial elapsed timing nor parallel simulation wall time is a hard real-time guarantee.

## Licensing, citation and attribution

**Original research software and usage documentation:** [MIT License](LICENSE).

**Technical notes, original accompanying figures and generated experimental data:** [Creative Commons Attribution 4.0 International](LICENSE-CC-BY-4.0.txt).

Copyright (c) 2026 Hossein Nick Zinat Matin and Lipem Likwai Momnougui, for their original material. The licenses apply by component as described in [LICENSE-SCOPE.md](LICENSE-SCOPE.md). The conference manuscript is outside the new license grant, and bundled third-party components retain the terms identified in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

`CITATION.cff` supplies the authors, affiliation, title, notes version, date and repository. Please cite the paper and technical notes when using the research artifacts. This scholarly citation request does not add a condition to the MIT License; license notice and attribution obligations are governed by the applicable license. An actual release tag or DOI can be added after publication of a release.

This work benefited from Hi! PARIS and State funding managed by the French National Research Agency (ANR) under the France 2030 program, reference **ANR-23-IACL-0005**.
