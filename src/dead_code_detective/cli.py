import argparse, ast, json
from pathlib import Path

def scan(path):
    defined, called = {}, set()
    for file in Path(path).rglob('*.py'):
        if any(part.startswith('.') for part in file.parts):
            continue
        try:
            tree = ast.parse(file.read_text(encoding='utf-8'))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                defined[node.name] = str(file)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                called.add(node.func.id)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                called.add(node.func.attr)
    return [{'name': name, 'file': file} for name, file in sorted(defined.items()) if name not in called]

def main():
    parser = argparse.ArgumentParser(description='Find likely unused Python functions.')
    parser.add_argument('path', nargs='?', default='.')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = scan(args.path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for item in result:
            print(f"{item['file']}: {item['name']}")

if __name__ == '__main__':
    main()
