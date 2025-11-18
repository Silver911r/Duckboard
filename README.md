# Duckboard - Lightweight Data Analytics GUI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
![DuckDB](https://img.shields.io/badge/duckdb-1.4.1-green)

A desktop data analytics tool powered by DuckDB for fast, interactive analysis of CSV, Parquet, and Arrow files. Built with PySide6 to explore modern Qt capabilities while solving real data analysis friction points.

![Duckboard Screenshot](images/sample%20query.png)

## Motivation

I wanted to continue building with Qt/PySide6 while tackling something more directly useful - a lightweight alternative to tools like Azure Data Studio, but focused on local file analysis with the speed of DuckDB. This combines GUI development practice with the modern data stack (DuckDB, Arrow, Polars) for exploratory data analysis.

## Planned Features

### V1 MVP
- **File browser** - Drag & drop CSVs, Parquet, and Arrow files
- **SQL editor** - Query interface with syntax highlighting
- **Results table** - Fast rendering of query results
- **Quick stats** - Auto-generated summary statistics for loaded tables
- **Query history** - Click to re-run previous queries
- **Export options** - Save results as CSV, Parquet, or Arrow
- **Dashboard view** - Auto-generated visualizations (bar charts, line charts, scatter plots)
- **Workspace saving** - Save collections of files and queries as projects

### Tech Stack
- **Python 3.11+** - Core language
- **PySide6** - Qt GUI framework
- **DuckDB** - Fast analytical queries on local files
- **Polars** - Additional data manipulation capabilities
- **Matplotlib** - Embedded visualizations

## Why DuckDB?

DuckDB can query CSV, Parquet, and Arrow files directly without loading them fully into memory. It's exceptionally fast for aggregations and analytical workloads, making it perfect for exploratory data analysis on local files.

## Running It

```bash
uv sync
uv run main.py
```

## Current State

Project scaffolding phase - building out the core GUI structure and DuckDB integration layer.

## Future Enhancements
- Remote file support (S3, HTTP)
- Advanced visualizations (heatmaps, correlation matrices)
- Query templates for common analysis patterns
- Parquet metadata inspection
- Schema comparison across files

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
