# Paper ingest contract

- Treat the DOI printed in the paper as the strongest metadata identifier, but show it before applying changes.
- Query Crossref with the DOI only. Do not upload the PDF.
- Default filename: `first-author-year-short-title.pdf`, using lowercase ASCII and hyphens.
- Default BibTeX key: `firstauthorYEARshorttitle`.
- Never replace an existing PDF, bibliography entry, or conflicting key.
- A matching DOI in the bibliography is a duplicate signal, not permission to overwrite.
- When metadata is incomplete or inconsistent with the visible paper, stop for manual confirmation.
- Preserve the original file until an authorized apply operation succeeds.
