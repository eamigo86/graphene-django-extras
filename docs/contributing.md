# Contributing Guide

We welcome contributions to graphene-django-extras! This guide will help you get started.

## Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/graphene-django-extras.git
   cd graphene-django-extras
   ```
3. **Install development dependencies**:
   ```bash
   poetry install
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.10, 3.11, or 3.12
- Poetry for dependency management
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/eamigo86/graphene-django-extras.git
cd graphene-django-extras

# Install dependencies
poetry install

# Install pre-commit hooks (optional but recommended)
poetry run pre-commit install
```

### Development Commands

We use `make` commands for common development tasks:

```bash
# Run tests
make test

# Run all tests across Python/Django versions
make test-all

# Code quality checks
make quality

# Security checks
make security

# Format code
make format

# Type checking
make type-check

# Build documentation
make docs

# Serve documentation locally
make docs-serve

# Clean build artifacts
make clean
```

## Code Standards

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all quality checks:
```bash
make quality
```

### Documentation Standards

- All public classes and methods must have docstrings
- Use Google-style docstrings
- Include examples in docstrings where helpful
- Keep documentation up-to-date with code changes

### Testing Standards

- Write tests for all new features
- Maintain or improve test coverage
- Use descriptive test names
- Follow the existing test structure

```python
def test_django_list_object_type_pagination():
    """Test that DjangoListObjectType properly paginates results."""
    # Test implementation
    pass
```

## Making Changes

### 1. Choose What to Work On

- Check [open issues](https://github.com/eamigo86/graphene-django-extras/issues)
- Look for issues labeled `good first issue` for beginners
- Propose new features by opening an issue first

### 2. Write Code

- Follow the code standards above
- Add tests for your changes
- Update documentation if needed
- Keep commits small and focused

### 3. Test Your Changes

```bash
# Run tests for your Python version
make test

# Run tests for all supported versions (takes longer)
make test-all

# Check code quality
make quality

# Check security
make security
```

### 4. Update Documentation

- Update docstrings for any changed APIs
- Add examples if you're adding new features
- Update the changelog if your change is user-facing

### 5. Submit a Pull Request

1. **Push your changes**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a pull request** on GitHub

3. **Describe your changes** clearly in the PR description

4. **Wait for review** and address any feedback

## Pull Request Guidelines

### Title Format

Use conventional commit format:
- `feat: add new pagination option`
- `fix: resolve issue with nested mutations`
- `docs: improve installation guide`
- `test: add tests for directive validation`

### Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] All new and existing tests pass locally
- [ ] I have run the full test suite (`make test-all`)

## Documentation
- [ ] I have updated the documentation accordingly
- [ ] I have updated the changelog if needed

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] My changes generate no new warnings
- [ ] Any dependent changes have been merged and published
```

## Types of Contributions

### Bug Fixes

- Always include a test that reproduces the bug
- Explain the root cause in the PR description
- Consider edge cases

### New Features

- Discuss the feature in an issue first
- Include comprehensive tests
- Update documentation and examples
- Consider backward compatibility

### Documentation

- Keep language clear and concise
- Include practical examples
- Test code examples to ensure they work
- Update related documentation

### Performance Improvements

- Include benchmarks showing the improvement
- Ensure the change doesn't break existing functionality
- Consider memory usage as well as speed

## Development Tips

### Running Specific Tests

```bash
# Run tests for a specific file
poetry run pytest tests/test_fields.py

# Run tests matching a pattern
poetry run pytest -k "test_pagination"

# Run with coverage
poetry run pytest --cov=graphene_django_extras
```

### Debugging

```bash
# Run with ipdb for debugging
poetry run pytest tests/test_fields.py -s --pdb
```

### Database Setup

The tests use a SQLite database by default. For testing with other databases:

```bash
# PostgreSQL
export DATABASE_URL=postgres://user:pass@localhost/test_db
poetry run pytest

# MySQL
export DATABASE_URL=mysql://user:pass@localhost/test_db
poetry run pytest
```

## Code Review Process

### What We Look For

- **Correctness**: Does the code work as intended?
- **Testing**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Performance**: Does it maintain good performance?
- **Style**: Does it follow our coding standards?
- **Compatibility**: Does it work with all supported versions?

### Timeline

- Initial review: Within 1-2 weeks
- Follow-up reviews: Within a few days
- Complex changes may take longer

## Getting Help

### Discord/Slack

We don't currently have a Discord or Slack, but you can:

### GitHub Discussions

Use [GitHub Discussions](https://github.com/eamigo86/graphene-django-extras/discussions) for:
- Questions about contributing
- Feature discussions
- General help

### Issues

Use [GitHub Issues](https://github.com/eamigo86/graphene-django-extras/issues) for:
- Bug reports
- Feature requests
- Documentation improvements

## Recognition

Contributors are recognized in several ways:

- Listed in the repository contributors
- Mentioned in release notes for significant contributions
- Can be added as maintainers for sustained contributions

## Code of Conduct

### Our Pledge

We are committed to making participation in our project a harassment-free experience for everyone, regardless of:
- Age, body size, disability, ethnicity
- Gender identity and expression
- Level of experience, education
- Nationality, personal appearance
- Race, religion, sexual identity and orientation

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Project maintainers have the right to:
- Remove, edit, or reject comments, commits, code, wiki edits, issues
- Ban temporarily or permanently any contributor for behaviors deemed inappropriate

Report any issues to the project maintainers via GitHub issues or email.

## Thank You! 🎉

Your contributions help make graphene-django-extras better for everyone. Whether it's:

- Fixing a typo in documentation
- Adding a new feature
- Reporting a bug
- Improving performance

Every contribution matters and is appreciated! 🙏
