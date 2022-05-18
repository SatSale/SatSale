#!/usr/bin/env bash
# Based on https://github.com/JoinMarket-Org/joinmarket-clientserver/blob/master/test/lint/lint-python.sh
# Based on Bitcoin Core's test/lint/lint-python.sh

# E265 block comment should start with '# '
# E402 module level import not at top of file
# E501 line too long
IGNORE_ERRORS="E265,E402,E501"

EXCLUDE_PATTERNS="docs/*"

if ! command -v flake8 > /dev/null; then
    echo "Skipping Python linting since flake8 is not installed."
    exit 0
elif flake8 --version | grep -q "Python 2"; then
    echo "Skipping Python linting since flake8 is running under Python 2. Install the Python 3 version of flake8."
    exit 0
fi

if [[ $# == 0 ]]; then
    flake8 $(git ls-files "*.py") \
        --extend-ignore "${IGNORE_ERRORS}" \
        --extend-exclude "${EXCLUDE_PATTERNS}"
else
    flake8 "$@" \
        --extend-ignore "${IGNORE_ERRORS}"
fi
