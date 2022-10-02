#!/usr/bin/env bash
cd "$(dirname "$0")/.."
pytest test/test_*.py
