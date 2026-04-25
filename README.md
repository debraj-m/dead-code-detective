# Dead Code Detective

**Find code your repo forgot about.**

Dead Code Detective scans Python projects for functions that are defined but not
called or imported by name. It is intentionally conservative: the goal is to
start cleanup conversations, not delete code automatically.

## Install

```bash
git clone https://github.com/debraj-m/dead-code-detective.git
cd dead-code-detective
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

Scan a package:

```bash
dead-code-detective src
```

JSON output:

```bash
dead-code-detective . --json
```

Ignore paths:

```bash
dead-code-detective . --ignore "*/migrations/*" --ignore "*/generated/*"
```

Use in CI:

```bash
dead-code-detective src --fail-on-detect
```

## Output

```text
src/app.py:42 unused_helper (medium): defined but not called or imported by name
```

Each finding includes:

- file
- line
- symbol name
- kind
- confidence
- reason

## Limitations

Python is dynamic. Functions can be called through decorators, reflection,
framework routing, string references, plugins, or dependency injection. Treat
findings as cleanup candidates, not proof.

## Local Checks

```bash
pip install -e .
python -m unittest discover -s tests
dead-code-detective .
```

## Roadmap

- Class and method analysis
- Import graph mode
- Framework-aware plugins
- Git-age ranking
- SARIF output

## License

MIT. See [LICENSE](LICENSE).
