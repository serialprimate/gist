---
name: Bash Development Instructions
description: Best practices and modern idioms for Bash scripting
applyTo: "**/*.sh"
---

# Bash Development Instructions

## Script Headers & Strict Mode
- Always start scripts with a proper shebang:
  ```bash
  #!/usr/bin/env bash
  ```
- Enable **strict mode** for robustness:
  ```bash
  set -euo pipefail
  ```
  - `set -e`: Exit on first error
  - `set -u`: Treat unset variables as errors
  - `set -o pipefail`: Fail if any command in a pipeline fails
- Consider additional options:
  - `set -x`: Debug mode (prints commands as they execute)
  - `set -E`: Inherit ERR trap in functions

## Variables & Quoting
- **Always quote variables**: `"$var"` to prevent word splitting and globbing
- Use `"${var}"` for explicit variable boundaries
- Use `local` for function-scoped variables
- Naming conventions:
  - `lowercase_snake_case` for local/script variables
  - `UPPERCASE` for environment variables and constants
- Use `readonly` for constants: `readonly CONFIG_FILE="/etc/app.conf"`
- Default values: `"${var:-default}"` or `"${var:=default}"`

## Conditionals & Tests
- Use `[[ ... ]]` for tests (not `[ ... ]` or `test`)
- String comparisons: `[[ "$str" == "value" ]]` or `[[ "$str" =~ regex ]]`
- Numeric comparisons: `[[ $num -eq 42 ]]`, `-lt`, `-gt`, `-le`, `-ge`, `-ne`
- File tests: `[[ -f "$file" ]]`, `-d`, `-r`, `-w`, `-x`, `-e`
- Logical operators: `[[ cond1 && cond2 ]]` or `[[ cond1 || cond2 ]]`

## Functions
- Define functions using modern syntax:
  ```bash
  function_name() {
      local arg1="$1"
      local arg2="${2:-default}"

      # Function body

      return 0
  }
  ```
- Use `return` for exit status (0 for success, non-zero for failure)
- Use `echo` or `printf` to return values, capture with command substitution
- Document function parameters and behavior

## Arrays & Iteration
- Declare arrays: `my_array=("item1" "item2" "item3")`
- Access elements: `"${my_array[0]}"` or all: `"${my_array[@]}"`
- Iterate over arrays:
  ```bash
  for item in "${array[@]}"; do
      printf '%s\n' "$item"
  done
  ```
- Associative arrays (Bash 4+):
  ```bash
  declare -A assoc_array
  assoc_array["key"]="value"
  ```

## Output & Logging
- Use `printf` over `echo` for portability and formatting:
  ```bash
  printf '%s\n' "message"
  printf 'Name: %s, Age: %d\n' "$name" "$age"
  ```
- Write errors to stderr:
  ```bash
  printf 'Error: %s\n' "something went wrong" >&2
  ```
- Use logging functions:
  ```bash
  log_info() { printf '[INFO] %s\n' "$*"; }
  log_error() { printf '[ERROR] %s\n' "$*" >&2; }
  ```

## Command Execution & Substitution
- Use `$(command)` for command substitution (not backticks)
- Check command existence: `command -v cmd` or `type -P cmd`
- Run commands conditionally:
  ```bash
  if command -v docker &> /dev/null; then
      docker version
  fi
  ```

## Error Handling
- Check exit codes explicitly when needed:
  ```bash
  if ! command; then
      log_error "Command failed"
      exit 1
  fi
  ```
- Use traps for cleanup:
  ```bash
  cleanup() {
      rm -f "$temp_file"
  }
  trap cleanup EXIT
  ```
- Validate input and preconditions

## Best Practices
- Use ShellCheck to validate scripts (`shellcheck script.sh`)
- Keep scripts focused and modular
- Use meaningful variable names
- Avoid parsing `ls` output - use globs or `find`
- Use `||` and `&&` carefully with `set -e`
- Prefer `[[ ]]` over backticks and old test syntax
- Use here documents for multi-line strings:
  ```bash
  cat << 'EOF'
  Multi-line
  content
  EOF
  ```

## External Tools & Utilities
- Use standard POSIX tools when possible: `grep`, `sed`, `awk`, `cut`, `tr`
- For JSON: `jq`
- For YAML: `yq`
- For complex logic: consider Python or another language

## Portability
- If POSIX sh compatibility is required:
  - Avoid `[[`, `local`, arrays, `${var/pattern/replacement}`
  - Use `/bin/sh` shebang
  - Test with `dash` or `ash`
- Otherwise, prefer Bash for its features and maintainability

## Documentation
- Add file-level comments explaining purpose and usage
- Document complex sections with inline comments
- Include usage examples for scripts with arguments:
  ```bash
  # Usage: script.sh <input_file> <output_file>
  ```
