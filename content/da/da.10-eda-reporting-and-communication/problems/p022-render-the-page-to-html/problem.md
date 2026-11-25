# Render the page to HTML

Chapter section 6.6. Managers read the finding in a browser or print it, so it becomes **one HTML file**: the figures are embedded as base64 so nothing is missing when the file is emailed,
and every piece of text is **escaped**, because a `<` or `&` in a sentence would otherwise break the page (or inject markup).

Write `render_html(f, source_note, figures_dir)` for a `Finding` `f` (the class is in `starter.py`). Return one string:

1. It starts with `<!doctype html>` and contains `<h1>` with the escaped headline.
2. Then six sections, each starting with an `<h3>` heading, in this order: `Recommendation`, `Impact`, `Evidence`, `Confidence`, `Limitations`, `Next steps`.
   Recommendations, evidence, limitations and next steps are `<ul>` lists with one `<li>` each; a recommendation item reads `action (owner: X; by Y)`.
3. After the Impact section, one `<img src='data:image/png;base64,...' alt='NAME'>` per name in `f.figures`, read from `figures_dir / name`.
4. At the end, `<p><small>source_note</small></p>`.

**Escape** every text that comes from the finding or the note with `html.escape`. A missing figure file should raise `FileNotFoundError` (do not hide it).

## Example

A headline `Churn <5% & rising` appears in the page as `Churn &lt;5% &amp; rising`.
