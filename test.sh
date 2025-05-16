#!/bin/bash

echo "Running all tests..."

echo "Testing sweep.py"
python3 test_sweep.py || exit 1

echo "Testing comment.py"
python3 test_comment.py || exit 1

echo "Testing view.py"
python3 test_view.py || exit 1

echo "Testing resolve.py"
python3 test_resolve.py || exit 1

echo "Testing reopen.py"
python3 test_reopen.py || exit 1

echo "All tests passed successfully."
