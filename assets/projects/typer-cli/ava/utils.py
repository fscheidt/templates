import os
import fnmatch
import inspect
import functools
from pathlib import Path
import rich
from rich import print


def debug_func(func):
    """ 
    Decorator to debug function arguments 
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the function's signature and bind the passed arguments.
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()  # Fill in default values for missing arguments.
        is_verbose = bound_args.arguments.get('verbose', None)
        if is_verbose:
            print("-"*60)
            full_name = f"{func.__module__}.[red b]{func.__qualname__}[/]"
            print(f"{full_name} (*args)")
            print(bound_args.arguments)
            print("-"*60)
        return func(*args, **kwargs)
    return wrapper

@debug_func
def search_files(
        folderpath: Path, 
        extensions: list = ['*'],
        ignore_extensions: list = None,
        max_files: int = 0,
        ignore_parts: list[str] = [],
        keywords: str = None,
        sort_files: bool = True,
        verbose: bool = None
    ) -> list[Path]:
    """
    Search in filesystem given a folder and criterias
    """
    ignore_extensions = ignore_extensions or []
    ignore_parts = ignore_parts or []
    files = []
    for root, _, filenames in os.walk(folderpath):
        for ext in extensions:
            for filename in fnmatch.filter(filenames, ext):
                fp = Path(os.path.join(root, filename))
                if len(ignore_extensions) > 0 and fp.suffix in ignore_extensions: 
                    continue
                if any(part in fp.parts for part in ignore_parts):
                    continue
                if keywords:
                    # Read the file's text content. Again, errors='ignore' helps avoid encoding issues.
                    content = fp.read_text(encoding='utf-8', errors='ignore')
                    if keywords not in content:
                        # print(f"Found keyword in: {fp}")
                        continue
                files.append(fp)
    
    # sort the list of Path objects
    files = sorted(files, key=lambda f: str(f)) if sort_files else files

    if max_files > 0 and len(files) > max_files:
        files = files[:max_files]
    
    if verbose:
        print(locals())
        print(f"found={len(files)}")
        
    return files


def debug_cli(app, 
              cli_name: str, 
              fmt: str = "table", 
              verbose: bool = None):
    """ 
    Show all commands, groups and subcommands in the CLI app
    """
    FMT_OPTS = ['table','json','text']
    SEP = 60
    CMD_SEP = " --- "
    NO_NAME = "UNK"
    assert fmt in FMT_OPTS
    
    app_cmds = sorted([rc.name for rc in app.registered_commands])
    verbose and print("[green b]app_cmds:")
    verbose and print(app_cmds)
    verbose and print("-"*SEP)
    
    groups = sorted([rc.name for rc in app.registered_groups])
    verbose and print("[green b]groups:") 
    verbose and print(groups)
    verbose and print("-"*SEP)
    sub_cmds = [{
        "group": cli_name,
        "commands": app_cmds
    }]
    for i, cmd in enumerate(app.registered_groups,1):
        verbose and print(f"group/{i}: [red b]{cmd.name}")
        cmd_info = cmd.typer_instance.registered_commands
        sub_cmd_names = []
        for j, sub in enumerate(cmd_info,1):
            name = f"{NO_NAME}/{j}" if sub.name is None else sub.name
            sub_cmd_names.append(name)
        sub_cmd_names.sort()
        verbose and print(sub_cmd_names)
        sub_cmds.append({
            "group": cmd.name,
            "commands": sub_cmd_names
        })
        verbose and print("-"*SEP)
        
    verbose and print(sub_cmds)
    verbose and print("-"*SEP)
    
    if fmt == 'text':
        verbose and print("xc")
        verbose and print(f"commands={app_cmds}")
        verbose and print(f"sub_commands={groups}")
        for cmd in sub_cmds:
            print(f"{cmd["group"]}={cmd["commands"]}")
            # print(f"{cmd["commands"]}")
            
    elif fmt == 'json':
        print(sub_cmds)

    elif fmt == 'table':
        table = rich.table.Table(title="Groups Commands")
        table.add_column("group", style="bold cyan", justify="right", no_wrap=True)
        table.add_column("commands", style="green3", max_width=120)
        for cmd in sub_cmds:
            # cmd_name = cmd["command"] if cmd["command"]
            table.add_row(
                cmd["group"], 
                f"{CMD_SEP}".join(cmd["commands"]), 
            )
        print(table)
    else:
        print(f"[red b]Unknow format={fmt}")
