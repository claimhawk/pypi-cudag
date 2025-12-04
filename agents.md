# Repository Guidelines

This file provides guidance to AI coding assistants when working with code in this repository.

## Project Overview

This is CUDAG (Computer Use Dataset Action Generator) - the framework for creating screen generators that produce synthetic screenshots and action labels for training vision-language models.

## Code Quality

- Target Python 3.12+, four-space indentation, and PEP 8 defaults
- All Python code must pass ruff, mypy, and radon checks
- Maximum cyclomatic complexity: 10
- All functions must have type hints

## Commands

```bash
pip install -e .
cudag new my-generator       # Create new generator
cudag validate <dataset>     # Validate dataset against schema
```

## Dataset Schema

See `docs/DATASET_SCHEMA.md` for the complete dataset schema definition.

Validation checks:
- Required filesystem structure (images/, test/, etc.)
- Training record schema (data.jsonl, train.jsonl, val.jsonl)
- Test record schema (test/test.json)
- Image path validity (all referenced images exist)

Schema files:
- `src/cudag/schemas/train_record.schema.json` - Training record JSON Schema
- `src/cudag/schemas/test_record.schema.json` - Test record JSON Schema
- `src/cudag/schemas/filesystem.json` - Filesystem structure definition

## Coordinate System

All coordinates use RU (Resolution Units) normalized to [0, 1000]:
- Conversion: `normalized = (pixel / image_dimension) * 1000`

## Git Commits

**DO NOT CO-AUTHOR COMMITS** - only use the GitHub user's name when committing. Do not add co-author trailers or attribute commits to AI assistants.
