# Cross-project review rubric

## Code and data

- Inputs are the intended versions and raw-data pointers resolve.
- Joins, filters, exclusions, grouping, units, denominators, and missing values match the stated method.
- Train/test or discovery/validation separation prevents leakage when applicable.
- Randomness, dependencies, and parameters are controlled sufficiently to reproduce results.
- Tables and figures are generated from the inspected analysis rather than manually diverging copies.

## Analysis

- Estimands, models, comparisons, and uncertainty measures answer the stated question.
- Assumptions and multiplicity are addressed where relevant.
- Sensitivity analyses support rather than replace the primary analysis.
- Numerical values agree across outputs and manuscript sections.

## Evidence and text

- Claims match study design and retrieved sources.
- Abstract and conclusions do not exceed results.
- Limitations include material validity threats.
- Citations resolve and support the nearby statement.

## Finding levels

- `critical`: likely invalidates a central result or makes it irreproducible.
- `high`: materially changes interpretation or creates a serious reliability risk.
- `medium`: important inconsistency, omission, or fragile practice.
- `low`: clarity, maintainability, or minor reporting problem.
- `question`: plausible concern that cannot be resolved with available evidence.
