"""
Main entry point for the ChromaLens CLI.
"""

import sys
import os

import click

from chromalens.cli.commands import cli


def main():
    """Run the ChromaLens CLI."""
    # Check for environment variables
    if "CHROMALENS_HOST" in os.environ:
        os.environ.setdefault("CHROMA_HOST", os.environ["CHROMALENS_HOST"])
    
    if "CHROMALENS_PORT" in os.environ:
        os.environ.setdefault("CHROMA_PORT", os.environ["CHROMALENS_PORT"])
    
    if "CHROMALENS_API_KEY" in os.environ:
        os.environ.setdefault("CHROMA_API_KEY", os.environ["CHROMALENS_API_KEY"])
    
    # Run the CLI
    cli()


if __name__ == "__main__":
    main()