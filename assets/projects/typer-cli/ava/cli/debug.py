import typer
import rich
from ava import settings, console, CustomTyperGroup
from typing_extensions import Annotated
from typer import Context


app = typer.Typer(
    cls=CustomTyperGroup, 
    no_args_is_help=True, 
    short_help="Debug CLI settings",
    rich_markup_mode="rich",
)


@app.command("commands", help=f"Debug [green b]{settings.project.name}[/] commands")
def commands(
        ctx: Context,
        verbose: Annotated[bool, typer.Option("--verbose", "-v")] = None,
        fmt: Annotated[str, typer.Option("--fmt")] = 'table',
    ):
    """ Debug cli commands """
    from ava.utils import debug_cli
    verbose and console.log(f'command="{ctx.command_path}"')
    debug_cli(app, settings.project.name, fmt=fmt, verbose=verbose)


@app.command("settings")
def display_settings(
        key: str = None, 
        verbose:bool=None, 
        quiet:bool=None
    ):
    """
    Display cli settings
    
    Usage: 
        ava settings

        ava settings --key=project
        
        ava settings --key=resources.data.path
    """
    settings_file=settings.project.path_settings
    data = settings.model_dump()
    if key:
        parts = key.split(".")
        if len(parts)>1:
            for i in range(0,len(parts)):
                data = data.get(parts[i],None)
                if data is None:
                    data = f"key not found: [red bold]{key}"
                    break
        else:
            data = data[key] if key in data else f"key not found: [red bold]{key}"
        
    if quiet is None:
        console.print(data)
    if verbose:
        console.print(f"{settings_file=}")
    return data



@app.command("settings-key")
def list_settings_keys(
        name: str, 
        verbose:bool=None, 
        quiet:bool=None):
    """
    Show keys in settings for a given entry
    
    Usage: 
        xc settings-key app

        xc settings-key gh.api
    """
    data = settings.model_dump()
    if name:
        parts = name.split(".")
        if len(parts)>1:
            for i in range(0,len(parts)):
                data = data.get(parts[i],None)
                if data is None:
                    data = f"key not found: [red bold]{name}"
                    break
        else:
            data = data[name] if name in data else f"entry not found: [red bold]{name}"
        try:
            data = list(data.keys())
        except:
            console.print(f"{name} not found")
            exit(1)
    if quiet is None:
        console.print(f"key=[yellow b]{name}")
        console.print(data)
    return data


if __name__ == "__main__":
    app()
