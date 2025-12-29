---
name: Python Development Instructions
description: Modern Python 3.12+ standards, type hints, and best practices
applyTo: "**/*.py"
---

# Python Development Instructions

## Language Version & Features
- Target **Python 3.12+** for new projects
- Use modern syntax features:
  - Union types with `|` operator (e.g., `str | None`)
  - Pattern matching with `match`/`case` (3.10+)
  - Exception groups and `except*` (3.11+)
  - Type parameter syntax with `type` (3.12+)
  - Per-interpreter GIL and improved performance (3.12+)
  - `@override` decorator for explicit method overriding (3.12+)

## Type Hints & Annotations
- **Always use type hints** for function signatures, class attributes, and variables
- Use `typing` module constructs appropriately:
  - `list[T]`, `dict[K, V]`, `set[T]` (not `List`, `Dict`, `Set` from typing)
  - `tuple[T, ...]` for variable-length, `tuple[T, U]` for fixed-length
  - `Callable[[Args], Return]` for function types
  - `Protocol` for structural subtyping
  - `TypeAlias` for complex type aliases
  - `TypeVar` for generic type parameters
- Use `None` instead of `Optional[T]` where possible (prefer `T | None`)
- Run type checkers: `mypy`, `pyright`, or `pyre`

## Code Style & Formatting
- Follow **PEP 8** style guide strictly
- Use automated formatters:
  - `autopep8` for code formatting
  - `isort` for import sorting
- Naming conventions:
  - `snake_case` for functions, variables, and modules
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
  - Leading underscore `_private` for internal/private names

## Data Structures & Classes
- Use `@dataclass` for simple data containers (Python 3.7+)
- Consider `pydantic.BaseModel` for data validation and serialization
- Use `NamedTuple` for immutable, typed tuples
- Prefer `dict` over custom classes when structure is dynamic
- Use `frozenset` and `tuple` for immutable collections

## Modern Idioms & Best Practices
- Use **f-strings** for string formatting (not `.format()` or `%`)
- Use comprehensions for simple transformations: list/dict/set comprehensions
- Use context managers (`with` statement) for resource management
- Use `pathlib.Path` for file system operations (not `os.path`)
- Prefer `enumerate()` and `zip()` over manual indexing
- Use `yield` and generators for memory-efficient iteration
- Use `@property` for computed attributes
- Leverage `functools`: `@lru_cache`, `@cached_property`, `partial`

## Error Handling
- Catch **specific exceptions**, never bare `except:`
- Create custom exception classes for domain-specific errors
- Use `raise ... from` to chain exceptions and preserve context
- Consider `contextlib.suppress()` for acceptable exceptions
- Document exceptions in docstrings

## Async Programming
- Use `async`/`await` for I/O-bound concurrent operations
- Use `asyncio` for event loop management
- Consider `aiohttp`, `httpx` for async HTTP requests
- Use `asyncio.gather()` for parallel async operations
- Be mindful of blocking operations in async code

## Dependency Management
- Use modern package managers: `poetry`, `uv`, or `pdm`
- Pin exact versions in production dependencies
- Use virtual environments (`venv`, `virtualenv`, or tools like `poetry`)
- Define dependencies with semantic versioning

## Testing & Quality
- Write tests using `pytest` (preferred) or `unittest`
- Use fixtures for test setup and teardown
- Use `pytest-cov` for coverage reports
- Run linters: `pylint`
- Use `mypy` for static type checking
- Consider property-based testing with `hypothesis`

## Documentation
- Use **Google-style** or **NumPy-style** docstrings
- Document all public modules, classes, functions, and methods
- Include:
  - Brief summary
  - Args/Parameters with types (if not obvious from type hints)
  - Returns with type
  - Raises for exceptions
  - Examples for complex functions
- Use `"""triple quotes"""` for all docstrings

## Performance Considerations
- Profile before optimizing (`cProfile`, `line_profiler`)
- Use `__slots__` for classes with many instances
- Consider `numpy` or `pandas` for numerical/data operations
- Use `itertools` for efficient iteration patterns
- Consider C extensions (`Cython`, `pybind11`) for performance-critical code
