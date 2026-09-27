"""
Accurate AST Scope Analyzer handling:
- Comprehensions (ListComp, SetComp, DictComp, GeneratorExp)
- Exception handlers (ExceptHandler with `as name`)
- With statements (`with ... as name`)
- For loops (`for target in ...`)
"""
import ast
import builtins
import sys
from pathlib import Path
from scripts.verify_python_blocks import extract_python_blocks, ROOT

BUILTIN_NAMES = set(dir(builtins))

class Scope:
    def __init__(self, parent=None, scope_type="module"):
        self.parent = parent
        self.scope_type = scope_type
        self.defs = set()

    def add_def(self, name):
        if name:
            self.defs.add(name)

    def is_defined(self, name):
        if name in self.defs:
            return True
        if self.parent:
            return self.parent.is_defined(name)
        return False

class ScopeAnalyzer(ast.NodeVisitor):
    def __init__(self, filename="<string>"):
        self.filename = filename
        self.current_scope = Scope(scope_type="module")
        self.undefined_references = []
        self.all_imports = set()

    def _bind_target(self, target):
        if isinstance(target, ast.Name):
            self.current_scope.add_def(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._bind_target(elt)
        elif isinstance(target, ast.Starred):
            self._bind_target(target.value)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname or alias.name.split('.')[0]
            self.current_scope.add_def(name)
            self.all_imports.add(name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            self.current_scope.add_def(name)
            self.all_imports.add(name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for b in node.bases:
            self.visit(b)
        for kw in node.keywords:
            self.visit(kw)
        for dec in node.decorator_list:
            self.visit(dec)
            
        self.current_scope.add_def(node.name)
        old_scope = self.current_scope
        self.current_scope = Scope(parent=old_scope, scope_type="class")
        for item in node.body:
            self.visit(item)
        self.current_scope = old_scope

    def visit_FunctionDef(self, node):
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node):
        self._visit_func(node)

    def _visit_func(self, node):
        for dec in node.decorator_list:
            self.visit(dec)
        if node.args.defaults:
            for d in node.args.defaults:
                self.visit(d)
        if node.args.kw_defaults:
            for d in node.args.kw_defaults:
                if d:
                    self.visit(d)
                    
        self.current_scope.add_def(node.name)
        
        old_scope = self.current_scope
        self.current_scope = Scope(parent=old_scope, scope_type="function")
        
        for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
            self.current_scope.add_def(arg.arg)
            if arg.annotation:
                self.visit(arg.annotation)
        if node.args.vararg:
            self.current_scope.add_def(node.args.vararg.arg)
            if node.args.vararg.annotation:
                self.visit(node.args.vararg.annotation)
        if node.args.kwarg:
            self.current_scope.add_def(node.args.kwarg.arg)
            if node.args.kwarg.annotation:
                self.visit(node.args.kwarg.annotation)
                
        if node.returns:
            self.visit(node.returns)
            
        for item in node.body:
            self.visit(item)
            
        self.current_scope = old_scope

    def visit_For(self, node):
        self.visit(node.iter)
        self._bind_target(node.target)
        for b in node.body:
            self.visit(b)
        for o in node.orelse:
            self.visit(o)

    def visit_AsyncFor(self, node):
        self.visit(node.iter)
        self._bind_target(node.target)
        for b in node.body:
            self.visit(b)
        for o in node.orelse:
            self.visit(o)

    def visit_With(self, node):
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars:
                self._bind_target(item.optional_vars)
        for b in node.body:
            self.visit(b)

    def visit_AsyncWith(self, node):
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars:
                self._bind_target(item.optional_vars)
        for b in node.body:
            self.visit(b)

    def visit_ExceptHandler(self, node):
        if node.type:
            self.visit(node.type)
        if node.name:
            self.current_scope.add_def(node.name)
        for b in node.body:
            self.visit(b)

    def _handle_comp(self, generators, elt_func):
        old_scope = self.current_scope
        self.current_scope = Scope(parent=old_scope, scope_type="comprehension")
        for gen in generators:
            self.visit(gen.iter)
            self._bind_target(gen.target)
            for if_expr in gen.ifs:
                self.visit(if_expr)
        elt_func()
        self.current_scope = old_scope

    def visit_ListComp(self, node):
        self._handle_comp(node.generators, lambda: self.visit(node.elt))

    def visit_SetComp(self, node):
        self._handle_comp(node.generators, lambda: self.visit(node.elt))

    def visit_GeneratorExp(self, node):
        self._handle_comp(node.generators, lambda: self.visit(node.elt))

    def visit_DictComp(self, node):
        def visit_key_val():
            self.visit(node.key)
            self.visit(node.value)
        self._handle_comp(node.generators, visit_key_val)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.current_scope.add_def(node.id)
        elif isinstance(node.ctx, ast.Load):
            name = node.id
            if name not in BUILTIN_NAMES:
                curr = self.current_scope
                found = False
                while curr:
                    if name in curr.defs:
                        found = True
                        break
                    curr = curr.parent
                if not found:
                    self.undefined_references.append((name, node.lineno, node.col_offset))
        self.generic_visit(node)

def analyze_file(doc_name):
    blocks = extract_python_blocks(ROOT / doc_name)
    print(f"\n==========================================")
    print(f"Checking Undefined Symbols: {doc_name} ({len(blocks)} blocks)")
    print(f"==========================================")
    
    issues_by_block = []
    for idx, b in enumerate(blocks, 1):
        content = b["content"]
        first_line = content.splitlines()[0] if content.splitlines() else ""
        tree = ast.parse(content)
        analyzer = ScopeAnalyzer(f"{doc_name}:{b['start']}")
        analyzer.visit(tree)
        
        is_test = "test_" in first_line.lower() or "tests/" in first_line.lower()
        
        real_issues = []
        for name, lineno, col in analyzer.undefined_references:
            if is_test and name in ["mock_llm", "client", "db_session", "sample_pr_diff", "tmp_path", "pytest"]:
                continue
            real_issues.append((name, lineno, col))
            
        if real_issues:
            issues_by_block.append((idx, b["start"], first_line, real_issues))
            print(f"[ISSUE] Block #{idx} (line {b['start']}) {first_line}:")
            for name, lineno, col in real_issues:
                doc_line = b["start"] + lineno - 1
                print(f"        Line {doc_line} (rel {lineno}:{col}): undefined symbol '{name}'")
                
    if not issues_by_block:
        print("  All blocks are completely free of undefined symbols!")
    else:
        print(f"  Total blocks with undefined symbols: {len(issues_by_block)}")

def main():
    for doc in ["PHASE_1_DETAILED_IMPLEMENTATION.md", "AGENT_SPECIFICATIONS.md", "API_SPECIFICATIONS.md", "DATABASE_DESIGN.md"]:
        analyze_file(doc)

if __name__ == "__main__":
    main()
