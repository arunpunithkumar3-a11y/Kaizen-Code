import typer

from kaizen.cli.commands.version import version

app = typer.Typer(help="Kaizen Code - AI Coding Agent")


app.command()(version)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):

    if ctx.invoked_subcommand is None:
        from kaizen.cli.ui.console import console
        from kaizen.cli.ui.panels import show_banner

        show_banner()

        console.print(" [bold #875fdf]Welcome to KAIZEN CODE![/bold #875fdf]")

        console.print(" To configure the AI coding agent environment, run:")

        console.print("   [bold #00d7ff]kaizen init[/bold #00d7ff]\n")

        console.print(" For a list of all commands and options, run:")

        console.print("   [bold #00d7ff]kaizen --help[/bold #00d7ff]\n")


if __name__ == "__main__":
    app()
