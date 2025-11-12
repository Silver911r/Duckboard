# Contributing to Duckboard

Thanks for your interest in contributing to Duckboard! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Duckboard.git
   cd Duckboard
   ```
3. Set up the development environment:
   ```bash
   uv sync
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and test them:
   ```bash
   uv run main.py
   ```

3. Commit your changes with a clear message:
   ```bash
   git commit -m "feat: add your feature description"
   ```

4. Push to your fork and submit a pull request

## Commit Message Format

We follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## Code Style

- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Add docstrings to classes and functions
- Keep functions focused and single-purpose

## Areas for Contribution

Check out the [README](README.md) for planned features and future enhancements. Some areas that need work:

- Dashboard visualizations with Matplotlib
- SQL syntax highlighting in the query editor
- Drag & drop file support
- Query templates
- Performance improvements
- Bug fixes and testing

## Questions?

Feel free to open an issue for questions or discussions about potential contributions.
