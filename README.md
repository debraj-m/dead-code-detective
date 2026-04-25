# Dead Code Detective

Find code your repo forgot about.

Scans Python files and reports functions that are defined but never called by name. It is intentionally conservative and meant as a cleanup starting point.

## Usage

```bash
dead-code-detective src
dead-code-detective . --json
```
