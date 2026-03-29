import ast
import os
import sys

def get_imports(path):
    imports = set()
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        node = ast.parse(f.read(), filename=file_path)
                    for stmt in ast.walk(node):
                        if isinstance(stmt, ast.Import):
                            for alias in stmt.names:
                                imports.add(alias.name.split('.')[0])
                        elif isinstance(stmt, ast.ImportFrom):
                            if stmt.module:
                                imports.add(stmt.module.split('.')[0])
                except Exception as e:
                    pass
    return imports

if __name__ == "__main__":
    backend_imports = get_imports('backend')
    cron_imports = get_imports('cron')
    common_imports = get_imports('common/python')
    print("BACKEND:", sorted(backend_imports))
    print("CRON:", sorted(cron_imports))
    print("COMMON:", sorted(common_imports))
