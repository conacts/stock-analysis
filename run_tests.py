#!/usr/bin/env python3
"""
Test runner for stock analysis system

Usage:
    python run_tests.py                    # Run all unit tests
    python run_tests.py --integration      # Run integration tests
    python run_tests.py --all              # Run all tests
    python run_tests.py --llm              # Run LLM tests (requires API key)
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --fast             # Run only fast unit tests
"""

import argparse
import os
import subprocess  # nosec B404 - subprocess is needed for running tests
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)

    try:
        subprocess.run(cmd, check=True, capture_output=False)  # nosec B603 - cmd is constructed internally
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for stock analysis system")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only (default)")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--llm", action="store_true", help="Run LLM tests (requires API key)")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--fast", action="store_true", help="Run only fast unit tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", "-n", type=int, help="Number of parallel workers")

    args = parser.parse_args()

    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])

    # Determine which tests to run
    if args.all:
        description = "Running all tests"
        cmd.extend(["-m", "not slow"])  # Skip slow tests unless explicitly requested
    elif args.integration:
        description = "Running integration tests"
        cmd.extend(["-m", "integration"])
    elif args.llm:
        description = "Running LLM tests"
        if not os.getenv("DEEPSEEK_API_KEY"):
            print("❌ DEEPSEEK_API_KEY environment variable required for LLM tests")
            return False
        cmd.extend(["-m", "llm"])
    elif args.fast:
        description = "Running fast unit tests"
        cmd.extend(["-m", "unit and not slow"])
    else:
        # Default: unit tests
        description = "Running unit tests"
        cmd.extend(["-m", "unit"])

    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing", "--cov-report=html"])
        description += " with coverage"

    # Run the tests
    success = run_command(cmd, description)

    if args.coverage and success:
        print("\n📊 Coverage report generated in htmlcov/index.html")

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")

        # Show quick stats
        if not args.verbose:
            print("\nFor detailed output, run with --verbose")

        print("\nTest categories available:")
        print("  --unit        : Fast unit tests (default)")
        print("  --integration : Integration tests with mocked external services")
        print("  --llm         : LLM tests (requires DEEPSEEK_API_KEY)")
        print("  --all         : All tests except slow ones")
        print("  --fast        : Only fastest unit tests")
        print("  --coverage    : Generate coverage report")

    else:
        print("💥 Some tests failed!")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
