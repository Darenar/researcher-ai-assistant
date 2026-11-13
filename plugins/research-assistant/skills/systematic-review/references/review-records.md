# Systematic review records

Maintain separate, joinable records rather than a single free-form spreadsheet:

- `protocol`: question framework, eligibility criteria, sources, complete queries, dates, and planned synthesis.
- `search-results`: stable record ID, source database, query/run ID, retrieved date, DOI or other identifiers, and original metadata.
- `duplicates`: retained ID, duplicate ID, matching evidence, and reviewer decision.
- `screening`: record ID, stage, decision (`include`, `exclude`, `unclear`), controlled reason, reviewer, and timestamp.
- `included-studies`: record ID, report-to-study grouping, final status, and linked evidence-matrix rows.
- `risk-of-bias`: study ID, assessment tool/version, domain judgments, support, reviewer, and date.

Valid flow transitions are identification to deduplication, title/abstract screening, full-text retrieval, full-text eligibility, and inclusion. Preserve every imported record and every decision. Generate PRISMA counts from these transitions and flag records that skip a required stage.
