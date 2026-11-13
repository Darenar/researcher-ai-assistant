# Evidence matrix schema

The default CSV uses these columns:

- `study_id`: stable BibTeX key, DOI, or project identifier.
- `citation`: short human-readable citation.
- `research_question`: question or hypothesis addressed by the study.
- `design`: study design and setting.
- `sample`: population and analysed sample size.
- `exposure_or_intervention`: focal exposure, intervention, or predictor.
- `comparator`: comparison condition when applicable.
- `outcome`: one outcome per row.
- `effect`: reported estimate with direction and uncertainty when available.
- `finding`: careful paraphrase of the result.
- `limitations`: reported or clearly identified limitations.
- `source`: project-relative paper or note path.
- `page`: one-based source page, range, or `not available`.
- `notes`: extraction uncertainty or reviewer notes.

Use one row per study-outcome combination so different outcomes and estimates are not collapsed. Preserve original units. Do not calculate missing estimates during extraction unless the method and derived status are recorded.
