# Installation

## Basic Installation

For installing graphene-django-extras, just run this command in your shell:

```bash
pip install graphene-django-extras
```

## Date Directive Support

!!! info "Optional Dependency"
    Date directive depends on the `dateutil` module. If you don't have it installed, the date directive will not be available.

You can install the `dateutil` module manually:

```bash
pip install python-dateutil
```

Or install graphene-django-extras with date support:

```bash
pip install graphene-django-extras[date]
```

## Requirements

- **Python**: 3.10, 3.11, 3.12
- **Django**: 3.2, 4.0, 4.2, 5.0, 5.1
- **graphene-django**: ^3.2

## Development Installation

If you want to contribute to the project, you can install it in development mode:

```bash
# Clone the repository
git clone https://github.com/eamigo86/graphene-django-extras.git
cd graphene-django-extras

# Install with poetry
poetry install

# Or install with pip in editable mode
pip install -e .
```

## Verify Installation

You can verify the installation by importing the package:

```python
import graphene_django_extras
print(graphene_django_extras.__version__)
```