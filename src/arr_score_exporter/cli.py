"""Command-line interface for Arr Score Exporter."""

import click
import logging
import sys
from pathlib import Path
from typing import Optional

from .config import Config
from .exporters import RadarrExporter, SonarrExporter


def setup_logging(level: str, log_file: Optional[str] = None) -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Setup file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Path to configuration file')
@click.option('--log-level', default='INFO', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Set logging level')
@click.option('--log-file', type=click.Path(), 
              help='Path to log file')
@click.pass_context
def cli(ctx, config: Optional[str], log_level: str, log_file: Optional[str]):
    """Arr Score Exporter - Export IMDb/TMDb scores to Radarr and Sonarr."""
    ctx.ensure_object(dict)
    
    # Setup logging
    setup_logging(log_level, log_file)
    
    # Load configuration
    try:
        ctx.obj['config'] = Config(config)
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def radarr(ctx):
    """Export scores to Radarr."""
    config = ctx.obj['config']
    
    if not config.is_radarr_enabled():
        click.echo("❌ Radarr is disabled in configuration", err=True)
        return
    
    click.echo("Starting Radarr score export...")
    
    try:
        exporter = RadarrExporter(config)
        results = exporter.export_scores()
        
        click.echo(f"✅ Export completed!")
        click.echo(f"   Processed: {results['processed']} movies")
        click.echo(f"   Updated: {results['updated']} movies")
        if results['errors'] > 0:
            click.echo(f"   ⚠️  Errors: {results['errors']} movies")
    
    except Exception as e:
        click.echo(f"❌ Export failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def sonarr(ctx):
    """Export scores to Sonarr."""
    config = ctx.obj['config']
    
    if not config.is_sonarr_enabled():
        click.echo("❌ Sonarr is disabled in configuration", err=True)
        return
    
    click.echo("Starting Sonarr score export...")
    
    try:
        exporter = SonarrExporter(config)
        results = exporter.export_scores()
        
        click.echo(f"✅ Export completed!")
        click.echo(f"   Processed: {results['processed']} series")
        click.echo(f"   Updated: {results['updated']} series")
        if results['errors'] > 0:
            click.echo(f"   ⚠️  Errors: {results['errors']} series")
    
    except Exception as e:
        click.echo(f"❌ Export failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def both(ctx):
    """Export scores to both Radarr and Sonarr."""
    config = ctx.obj['config']
    
    click.echo("Starting export to both Radarr and Sonarr...")
    
    total_results = {"processed": 0, "updated": 0, "errors": 0}
    
    # Export to Radarr
    if config.is_radarr_enabled():
        try:
            click.echo("Exporting to Radarr...")
            radarr_exporter = RadarrExporter(config)
            radarr_results = radarr_exporter.export_scores()
            for key in total_results:
                total_results[key] += radarr_results[key]
        except Exception as e:
            click.echo(f"❌ Radarr export failed: {e}", err=True)
            total_results["errors"] += 1
    else:
        click.echo("Radarr is disabled, skipping...")
    
    # Export to Sonarr
    if config.is_sonarr_enabled():
        try:
            click.echo("Exporting to Sonarr...")
            sonarr_exporter = SonarrExporter(config)
            sonarr_results = sonarr_exporter.export_scores()
            for key in total_results:
                total_results[key] += sonarr_results[key]
        except Exception as e:
            click.echo(f"❌ Sonarr export failed: {e}", err=True)
            total_results["errors"] += 1
    else:
        click.echo("Sonarr is disabled, skipping...")
    
    click.echo(f"✅ All exports completed!")
    click.echo(f"   Total processed: {total_results['processed']}")
    click.echo(f"   Total updated: {total_results['updated']}")
    if total_results['errors'] > 0:
        click.echo(f"   ⚠️  Total errors: {total_results['errors']}")


@cli.command()
@click.pass_context
def test_config(ctx):
    """Test configuration and API connectivity."""
    config = ctx.obj['config']
    
    click.echo("Testing configuration...")
    
    # Test Radarr connection
    if config.is_radarr_enabled():
        click.echo("Testing Radarr connection... ", nl=False)
        try:
            radarr_exporter = RadarrExporter(config)
            if radarr_exporter.test_connection():
                click.echo("✅ OK")
            else:
                click.echo("❌ Failed")
        except Exception as e:
            click.echo(f"❌ Failed: {e}")
    else:
        click.echo("Radarr: Disabled")
    
    # Test Sonarr connection
    if config.is_sonarr_enabled():
        click.echo("Testing Sonarr connection... ", nl=False)
        try:
            sonarr_exporter = SonarrExporter(config)
            if sonarr_exporter.test_connection():
                click.echo("✅ OK")
            else:
                click.echo("❌ Failed")
        except Exception as e:
            click.echo(f"❌ Failed: {e}")
    else:
        click.echo("Sonarr: Disabled")
    


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
