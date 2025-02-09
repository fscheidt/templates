#!/usr/bin/env python
from pathlib import Path
import importlib.metadata
from typing_extensions import Annotated
import typer
from typer import Context
from rich import print
import zipfile
from ava import (
    settings,
    console,
    CustomTyperGroup, 
    debug_func,
)
from ava.utils import search_files

CLI_NAME = "ava"
__version__ = importlib.metadata.version(CLI_NAME)

DEBUG = False


# ============================================================
app = typer.Typer(
        cls=CustomTyperGroup,
        no_args_is_help=True,
        rich_markup_mode="rich"
    )

# ============================================================
@app.command("version")
def version():
    """ CLI version """
    print(f"{__version__}")


# ============================================================
@app.command("unzip-all")
@debug_func
def unzip_all(
        folder: Path = typer.Argument(
            Path("."), 
            help="Files folder path (cwd default)"
        ),
        dry_run: Annotated[bool, typer.Option("--dry")] = None,
        ext: list[str] = ['*.zip','*.rar'],
        verbose: Annotated[bool, typer.Option("--verbose", "-v")] = None,
    ):
    """
    Unzip all files recursivelly

    ava unzip-all
    ava unzip-all folder
    """
    
    files = search_files(
        folderpath=folder,
        extensions=ext,
        # max_files=500,
        # verbose=verbose,
    )
    if not dry_run:
        for file in files:
            # Extract the ZIP file
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(file.parent)  # Extracts to the ZIP file's directory
                print(f"Extracted to: {file.parent}")
    else:
        # print(results.data_table())
        # print(f"total={len(results.files)}")
        print(files)
        print(len(files))


# ============================================================
def main():
    import ava.cli as cli
    app.add_typer(cli.debug.app, name="debug")
    app()


if __name__ == "__main__":
    main()
