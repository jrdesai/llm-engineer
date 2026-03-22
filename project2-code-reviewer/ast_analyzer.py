"""
AST Analyzer - Extracts structural facts from Python code

WHY AST instead of asking the LLM to read raw code?
    The LLM is good at reasoning. It's not a reliable code parser.
    If you ask "count the nested loops in this function", the LLM might miss one,
    especially in complex code. The Python ast module NEVER misses — it's deterministic.

    So we split the work:
    - ast module → counts loops, recursion, data structures (facts)
    - LLM         → reasons about what those facts mean (complexity + explanation)

    This is the right pattern: use deterministic tools for deterministic tasks,
    use AI for reasoning tasks.

HOW the ast module works:
    Python's ast module parses source code into a tree of Node objects.
    Every element of your code is a node:
        - FunctionDef  → a function definition
        - For          → a for loop
        - While        → a while loop
        - Call         → a function call (e.g. sorted(), dict())
        - Subscript    → an index access (e.g. arr[i])
    By walking this tree, we can count structural elements precisely.
"""

import ast
from dataclasses import dataclass, field
from typing import List


@dataclass
class FunctionAnalysis:
    """
    Structural facts extracted from a single function.
    These facts are what we pass to the LLM for reasoning.
    """
    name: str
    loop_depth: int          # Maximum nesting depth of loops (1 = single loop, 2 = nested, etc.)
    loop_count: int          # Total number of loops (for + while)
    has_recursion: bool      # Does this function call itself?
    has_sorting: bool        # Any calls to sorted() or .sort()?
    data_structures: List[str]  # Which built-in structures are used (dict, list, set)
    lines_of_code: int       # Rough size indicator


@dataclass
class CodeAnalysis:
    """
    Complete analysis of a submitted code snippet.
    May contain multiple functions.
    """
    functions: List[FunctionAnalysis] = field(default_factory=list)
    parse_error: str = ""    # Non-empty if the code couldn't be parsed


def analyze_code(source_code: str) -> CodeAnalysis:
    """
    Parse Python source code and extract structural facts from each function.

    Returns a CodeAnalysis with one FunctionAnalysis per function found.
    If the code has syntax errors, returns a CodeAnalysis with parse_error set.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return CodeAnalysis(parse_error=f"Syntax error: {e}")

    analysis = CodeAnalysis()

    # Walk the top-level tree looking for function definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            analysis.functions.append(_analyze_function(node))

    return analysis


def _analyze_function(func_node: ast.FunctionDef) -> FunctionAnalysis:
    """Extract structural facts from a single function node."""
    return FunctionAnalysis(
        name=func_node.name,
        loop_depth=_max_loop_depth(func_node),
        loop_count=_count_loops(func_node),
        has_recursion=_has_recursion(func_node),
        has_sorting=_has_sorting(func_node),
        data_structures=_find_data_structures(func_node),
        lines_of_code=_count_lines(func_node),
    )


def _max_loop_depth(node: ast.AST, current_depth: int = 0) -> int:
    """
    Recursively find the maximum loop nesting depth.

    Examples:
        for i in range(n):           → depth 1
            for j in range(n):       → depth 2  ← O(n²) indicator
                for k in range(n):   → depth 3  ← O(n³) indicator
    """
    max_depth = current_depth

    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.For, ast.While)):
            # Found a loop — recurse into it at depth + 1
            child_depth = _max_loop_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        else:
            child_depth = _max_loop_depth(child, current_depth)
            max_depth = max(max_depth, child_depth)

    return max_depth


def _count_loops(node: ast.AST) -> int:
    """Count total number of for and while loops in the function."""
    return sum(
        1 for child in ast.walk(node)
        if isinstance(child, (ast.For, ast.While))
    )


def _has_recursion(func_node: ast.FunctionDef) -> bool:
    """
    Detect if this function calls itself.
    A recursive function is at minimum O(n) — often O(n log n) or worse.
    """
    func_name = func_node.name
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            # Direct call: func_name(...)
            if isinstance(node.func, ast.Name) and node.func.id == func_name:
                return True
    return False


def _has_sorting(func_node: ast.FunctionDef) -> bool:
    """
    Detect calls to sorted() or .sort().
    Sorting is always O(n log n) — a key fact for complexity analysis.
    """
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            # sorted(x) — built-in function call
            if isinstance(node.func, ast.Name) and node.func.id == "sorted":
                return True
            # x.sort() — method call
            if isinstance(node.func, ast.Attribute) and node.func.attr == "sort":
                return True
    return False


def _find_data_structures(func_node: ast.FunctionDef) -> List[str]:
    """
    Identify which built-in data structures are used.
    This matters because dict/set lookups are O(1) while list lookups are O(n).
    """
    structures = set()
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ("dict", "set", "list", "defaultdict", "Counter"):
                structures.add(node.func.id)
        # Dict literal: {}
        if isinstance(node, ast.Dict):
            structures.add("dict")
        # Set literal: {1, 2, 3}
        if isinstance(node, ast.Set):
            structures.add("set")
        # List literal: [1, 2, 3]
        if isinstance(node, ast.List):
            structures.add("list")
    return sorted(structures)


def _count_lines(func_node: ast.FunctionDef) -> int:
    """Approximate lines of code using AST line number metadata."""
    lines = set()
    for node in ast.walk(func_node):
        if hasattr(node, "lineno"):
            lines.add(node.lineno)
    return len(lines)


def format_analysis_for_llm(analysis: CodeAnalysis) -> str:
    """
    Convert the structural analysis into a clear text summary for the LLM.

    WHY format it this way?
        The LLM doesn't need raw Python objects. It needs a clear, structured
        description it can reason about. We do the parsing, it does the thinking.
    """
    if analysis.parse_error:
        return f"Code could not be parsed: {analysis.parse_error}"

    if not analysis.functions:
        return "No functions found in the submitted code."

    lines = ["STRUCTURAL ANALYSIS (extracted from AST — not LLM-generated):\n"]

    for fn in analysis.functions:
        lines.append(f"Function: {fn.name}()")
        lines.append(f"  Lines of code    : {fn.lines_of_code}")
        lines.append(f"  Total loops      : {fn.loop_count}")
        lines.append(f"  Max loop depth   : {fn.loop_depth} {'← nested loops detected' if fn.loop_depth >= 2 else ''}")
        lines.append(f"  Recursion        : {'yes' if fn.has_recursion else 'no'}")
        lines.append(f"  Sorting calls    : {'yes — O(n log n) at minimum' if fn.has_sorting else 'no'}")
        lines.append(f"  Data structures  : {', '.join(fn.data_structures) if fn.data_structures else 'none detected'}")
        lines.append("")

    return "\n".join(lines)
