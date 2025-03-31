import ast
import sys
from typing import List, Dict

class SyncIssueDetector(ast.NodeVisitor):
    def __init__(self):
        self.issues: List[str] = []
        self.locked_vars: Dict[str, bool] = {}
        
    def visit_Call(self, node):
        # Detect lock/unlock operations
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'acquire':
                var = node.func.value.id
                self.locked_vars[var] = True
            elif node.func.attr == 'release':
                var = node.func.value.id
                self.locked_vars[var] = False
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        # Check for unprotected variable access
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in self.locked_vars:
                if not self.locked_vars[target.id]:
                    self.issues.append(
                        f"Line {node.lineno}: Unprotected write to '{target.id}'"
                    )

def analyze_file(filename: str) -> List[str]:
    with open(filename) as f:
        tree = ast.parse(f.read())
    detector = SyncIssueDetector()
    detector.visit(tree)
    return detector.issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <file_to_analyze>")
        sys.exit(1)
    
    results = analyze_file(sys.argv[1])
    print("\n".join(results) or "✅ No synchronization issues found")