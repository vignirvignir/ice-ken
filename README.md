# example_package

A minimal, modern Python package example using PEP 517/621 standards.

## Features

- Modern Python packaging with `pyproject.toml`
- src/ layout for better project structure
- No setup.py required
- Python 3.9+ compatible

## Installation

Install the package using pip:

```bash
pip install -e .
```

## Usage

```python
from example_package import __version__
from example_package.placeholder import hello

print(__version__)  # 0.1.0
print(hello())      # Hello from example_package!
```

## License

This project is licensed under the GNU General Public License v3.0 or later - see the LICENSE file for details.
