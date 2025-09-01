# Development Scripts

This directory contains helper scripts for maintaining code quality in the project.

## Scripts

### `format.sh`
Formats Python code using black and isort.
```bash
./scripts/format.sh
```

### `lint.sh` 
Runs ruff linting with automatic fixes where possible.
```bash
./scripts/lint.sh
```

### `check-all.sh`
Runs the complete code quality pipeline: formatting, linting, and tests.
```bash
./scripts/check-all.sh
```

### `pre-commit.sh`
Pre-commit hook that formats and lints only staged files.
```bash
./scripts/pre-commit.sh
```

## Setup Pre-commit Hook (Optional)

To automatically run quality checks before each commit:

```bash
# Copy the pre-commit script to git hooks
cp scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

This will ensure all staged Python files are properly formatted and linted before committing.