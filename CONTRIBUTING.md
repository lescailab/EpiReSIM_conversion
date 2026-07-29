# Contributing

Contributions should preserve the distinction between compatibility and strict
behavior. A change to compatibility output requires a MATLAB golden comparison
and an explicit changelog entry; strict-mode improvements require mathematical
tests and must not silently alter compatibility mode.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check src tests
mypy src/epiresim
pytest
python -m build
```

Add tests before implementation where possible. New model orders, file formats,
phenotypes, or frequency assumptions are scope changes and require a documented
design decision before code is added.

Fixtures must be synthetic, redistributable, and free of identifying sample,
cohort, phenotype, institution, server, and filesystem information.

## Pull requests

Pull requests should:

- describe the scientific or compatibility requirement;
- state whether outputs change;
- include focused tests and validation evidence;
- update documentation and the changelog when user-visible behavior changes;
- avoid unrelated additions or removals; and
- retain original authorship, license, and citation information.

Do not file automated reports against upstream projects. Reproduce and
understand any suspected upstream issue manually before contacting maintainers.
