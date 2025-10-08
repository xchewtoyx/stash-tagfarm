"""Main CLI module for TagFarm."""

import click
from rich.console import Console
from rich.progress import track
from pathlib import Path
from typing import Optional

from .config import ConfigManager
from .stash_client import StashClient
from .linkfarm import LinkFarmManager

console = Console()


@click.group()
@click.version_option()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    default="tagfarm.yaml",
    help="Path to configuration file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def main(ctx: click.Context, config: Path, verbose: bool) -> None:
    """Stash TagFarm - Create linkfarms from StashApp data."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["verbose"] = verbose
    
    if verbose:
        console.print(f"[dim]Using config file: {config}[/dim]")


@main.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.pass_context
def build(ctx: click.Context, dry_run: bool) -> None:
    """Build the linkfarm from StashApp data."""
    config_path = ctx.obj["config_path"]
    verbose = ctx.obj["verbose"]
    
    try:
        # Load configuration
        config_manager = ConfigManager(config_path)
        config = config_manager.load()
        
        if verbose:
            console.print(f"[dim]Farm path: {config.farm_path}[/dim]")
            console.print(f"[dim]Use title: {config.use_title}[/dim]")
        
        # Initialize StashApp client
        stash_client = StashClient(
            url=config.stash_url,
            api_key=config.api_key
        )
        
        # Initialize LinkFarm manager
        linkfarm = LinkFarmManager(
            farm_path=config.farm_path,
            use_title=config.use_title,
            dry_run=dry_run
        )
        
        console.print("[bold green]Building linkfarm...[/bold green]")
        
        # Process tags
        if config.tags:
            console.print("[blue]Processing tags...[/blue]")
            
            # Get favourite tags if enabled
            if config.tags.favourite:
                fav_tags = stash_client.get_favourite_tags()
                for tag in track(fav_tags, description="Processing favourite tags"):
                    scenes = stash_client.get_scenes_by_tag(tag["id"])
                    linkfarm.create_tag_links(tag["name"], scenes)
            
            # Get manual tag overrides
            if config.tags.names:
                for tag_name in track(config.tags.names, description="Processing manual tags"):
                    tag = stash_client.get_tag_by_name(tag_name)
                    if tag:
                        scenes = stash_client.get_scenes_by_tag(tag["id"])
                        linkfarm.create_tag_links(tag_name, scenes)
                    else:
                        console.print(f"[yellow]Warning: Tag '{tag_name}' not found[/yellow]")
        
        # Process performers
        if config.performers:
            console.print("[blue]Processing performers...[/blue]")
            
            # Get favourite performers if enabled
            if config.performers.favourite:
                fav_performers = stash_client.get_favourite_performers()
                for performer in track(fav_performers, description="Processing favourite performers"):
                    scenes = stash_client.get_scenes_by_performer(performer["id"])
                    linkfarm.create_performer_links(performer["name"], scenes)
            
            # Get manual performer overrides
            if config.performers.names:
                for performer_name in track(config.performers.names, description="Processing manual performers"):
                    performer = stash_client.get_performer_by_name(performer_name)
                    if performer:
                        scenes = stash_client.get_scenes_by_performer(performer["id"])
                        linkfarm.create_performer_links(performer_name, scenes)
                    else:
                        console.print(f"[yellow]Warning: Performer '{performer_name}' not found[/yellow]")
        
        console.print("[bold green]✓ Linkfarm build complete![/bold green]")
        
    except FileNotFoundError:
        console.print(f"[red]Error: Configuration file '{config_path}' not found[/red]")
        console.print("Run 'tagfarm init' to create a sample configuration file.")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


@main.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be removed without making changes",
)
@click.pass_context
def clean(ctx: click.Context, dry_run: bool) -> None:
    """Clean up dangling symlinks in the linkfarm."""
    config_path = ctx.obj["config_path"]
    verbose = ctx.obj["verbose"]
    
    try:
        # Load configuration
        config_manager = ConfigManager(config_path)
        config = config_manager.load()
        
        # Initialize LinkFarm manager
        linkfarm = LinkFarmManager(
            farm_path=config.farm_path,
            use_title=config.use_title,
            dry_run=dry_run
        )
        
        console.print("[bold yellow]Cleaning linkfarm...[/bold yellow]")
        
        dangling_links = linkfarm.find_dangling_links()
        
        if not dangling_links:
            console.print("[green]✓ No dangling links found[/green]")
            return
        
        console.print(f"[yellow]Found {len(dangling_links)} dangling links[/yellow]")
        
        if dry_run:
            console.print("[dim]Dry run - would remove:[/dim]")
            for link in dangling_links:
                console.print(f"  [red]- {link}[/red]")
        else:
            linkfarm.remove_dangling_links(dangling_links)
            console.print(f"[green]✓ Removed {len(dangling_links)} dangling links[/green]")
        
    except FileNotFoundError:
        console.print(f"[red]Error: Configuration file '{config_path}' not found[/red]")
        console.print("Run 'tagfarm init' to create a sample configuration file.")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


@main.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="tagfarm.yaml",
    help="Output path for configuration file",
)
def init(output: Path) -> None:
    """Create a sample configuration file."""
    if output.exists():
        if not click.confirm(f"Configuration file '{output}' already exists. Overwrite?"):
            console.print("[yellow]Configuration file creation cancelled.[/yellow]")
            return
    
    config_manager = ConfigManager()
    config_manager.create_sample_config(output)
    
    console.print(f"[green]✓ Sample configuration created at '{output}'[/green]")
    console.print("[dim]Edit the configuration file to match your setup.[/dim]")


if __name__ == "__main__":
    main()