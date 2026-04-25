from __future__ import annotations

import argparse
import ast
import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_IGNORE = ["*/.venv/*", "*/venv/*", "*/__pycache__/*", "*/tests/*"]


@dataclass
class Definition:
    name: str
    file: str
    line: int
    kind: str


class Collector(ast.NodeVisitor):
    def __init__(self, file: Path):
        self.file = file
        self.defined: list[Definition] = []
        self.called: set[str] = set()
        self.imported: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if not node.name.startswith("_"):
            self.defined.append(
                Definition(node.name, str(self.file), node.lineno, "function")
            )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if not node.name.startswith("_"):
            self.defined.append(
                Definition(node.name, str(self.file), node.lineno, "async_function")
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            self.called.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.called.add(node.func.attr)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            self.imported.add(alias.asname or alias.name)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imported.add(alias.asname or alias.name.split(".")[0])


def ignored(path: Path, patterns: list[str]) -> bool:
    text = str(path)
    return any(fnmatch.fnmatch(text, pattern) for pattern in patterns)


def scan(path: str | Path, ignore: list[str] | None = None) -> list[dict[str, Any]]:
    root = Path(path)
    ignore_patterns = [*DEFAULT_IGNORE, *(ignore or [])]
    definitions: list[Definition] = []
    called: set[str] = set()
    imported: set[str] = set()

    for file in root.rglob("*.py"):
        if ignored(file, ignore_patterns):
            continue
        try:
            tree = ast.parse(file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        collector = Collector(file)
        collector.visit(tree)
        definitions.extend(collector.defined)
        called.update(collector.called)
        imported.update(collector.imported)

    findings = []
    for definition in definitions:
        if definition.name in called or definition.name in imported:
            continue
        findings.append(
            {
                "name": definition.name,
                "file": definition.file,
                "line": definition.line,
                "kind": definition.kind,
                "confidence": "medium",
                "reason": "defined but not called or imported by name",
            }
        )
    return sorted(findings, key=lambda item: (item["file"], item["line"]))


def print_findings(findings: list[dict[str, Any]]) -> None:
    if not findings:
        print("No likely dead functions found.")
        return
    for item in findings:
        print(
            f"{item['file']}:{item['line']} {item['name']} "
            f"({item['confidence']}): {item['reason']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find likely unused Python functions before they fossilize."
    )
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        help="Glob pattern to ignore. Can be used more than once.",
    )
    parser.add_argument(
        "--fail-on-detect",
        action="store_true",
        help="Exit with code 1 if likely dead code is found.",
    )
    args = parser.parse_args()
    result = scan(args.path, ignore=args.ignore)
    if args.json:
        print(json.dumps({"findings": result, "count": len(result)}, indent=2))
    else:
        print_findings(result)
    if args.fail_on_detect and result:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
