"""
Enhanced CLI for the next-generation Arr Score Exporter.

Features:
- Rich command-line interface with progress bars
- Advanced analytics and reporting
- Historical tracking and trend analysis
- Intelligent upgrade candidate identification
- Performance optimization with caching
- Multiple output formats (CSV, JSON, HTML)
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .config import Config
from .models import DatabaseManager
from .analysis import IntelligentAnalyzer
from .reporting import HTMLReporter
from .exporters.enhanced_base import ExportConfig
from .exporters.enhanced_radarr import EnhancedRadarrExporter
from .exporters.enhanced_sonarr import EnhancedSonarrExporter


console = Console()


def setup_logging(verbose: bool = False, log_file: Optional[Path] = None):
    """Setup enhanced logging with rich formatting."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Configure logging
    handlers = []
    
    # Console handler with rich formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--log-file', type=click.Path(path_type=Path), help='Log file path')
@click.pass_context
def cli(ctx, verbose: bool, log_file: Optional[Path]):
    """Arr Score Exporter - TRaSH Guides Custom Format Analysis Tool
    
    Advanced tool for analyzing and optimizing media libraries based on
    TRaSH Guides custom format scores. Export scores, identify upgrade
    candidates, and generate comprehensive reports.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    setup_logging(verbose, log_file)
    
    # Welcome banner
    if not verbose:  # Only show banner in normal mode
        console.print(Panel.fit(
            "[bold blue]Arr Score Exporter v2.0[/bold blue]\n"
            "[dim]TRaSH Guides Custom Format Analysis Tool[/dim]",
            border_style="blue"
        ))


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path')
@click.option('--api-key', help='API key (overrides config)')
@click.option('--url', help='Application URL (overrides config)')
@click.option('--output-dir', type=click.Path(path_type=Path), 
              help='Output directory for files')
@click.option('--formats', multiple=True, default=['csv', 'html'],
              type=click.Choice(['csv', 'json', 'html']),
              help='Output formats to generate')
@click.option('--max-workers', type=int, default=20, 
              help='Maximum parallel workers')
@click.option('--cache/--no-cache', default=True,
              help='Enable/disable API response caching')
@click.option('--analyze/--no-analyze', default=True,
              help='Enable/disable intelligent analysis')
@click.pass_context
def radarr(ctx, config: Optional[Path], api_key: Optional[str], url: Optional[str],
           output_dir: Optional[Path], formats: List[str], max_workers: int,
           cache: bool, analyze: bool):
    """Collect fresh data from Radarr, analyze, and export to CSV/HTML.
    
    This command connects to your Radarr instance to download current library data,
    stores it in the local database, and generates reports. Use this command after
    upgrading files to refresh your library data.
    
    For generating reports from cached data only, use: arr-export-enhanced report --service radarr
    """
    
    try:
        export_config = _build_export_config(
            'radarr', config, api_key, url, output_dir, formats, 
            max_workers, cache, analyze
        )
        
        with console.status("[bold green]Initializing Radarr exporter..."):
            exporter = EnhancedRadarrExporter(export_config)
        
        console.print(f"[bold]Starting Radarr export to: {output_dir or Path.cwd()}[/bold]")
        
        # Run export with progress tracking
        success = exporter.export()
        
        if success:
            console.print("[bold green]Radarr export completed successfully![/bold green]")
            
            # Show performance stats
            stats = exporter.client.get_performance_stats()
            _display_performance_stats(stats)
            
        else:
            console.print("[bold red]Radarr export failed![/bold red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path')
@click.option('--api-key', help='API key (overrides config)')
@click.option('--url', help='Application URL (overrides config)')
@click.option('--output-dir', type=click.Path(path_type=Path), 
              help='Output directory for files')
@click.option('--formats', multiple=True, default=['csv', 'html'],
              type=click.Choice(['csv', 'json', 'html']),
              help='Output formats to generate')
@click.option('--max-workers', type=int, default=20, 
              help='Maximum parallel workers')
@click.option('--cache/--no-cache', default=True,
              help='Enable/disable API response caching')
@click.option('--analyze/--no-analyze', default=True,
              help='Enable/disable intelligent analysis')
@click.pass_context
def sonarr(ctx, config: Optional[Path], api_key: Optional[str], url: Optional[str],
           output_dir: Optional[Path], formats: List[str], max_workers: int,
           cache: bool, analyze: bool):
    """Collect fresh data from Sonarr, analyze, and export to CSV/HTML.
    
    This command connects to your Sonarr instance to download current library data,
    stores it in the local database, and generates reports. Use this command after
    upgrading files to refresh your library data.
    
    For generating reports from cached data only, use: arr-export-enhanced report --service sonarr
    """
    
    try:
        export_config = _build_export_config(
            'sonarr', config, api_key, url, output_dir, formats, 
            max_workers, cache, analyze
        )
        
        with console.status("[bold green]Initializing Sonarr exporter..."):
            exporter = EnhancedSonarrExporter(export_config)
        
        console.print(f"[bold]Starting Sonarr export to: {output_dir or Path.cwd()}[/bold]")
        
        # Run export with progress tracking
        success = exporter.export()
        
        if success:
            console.print("[bold green]Sonarr export completed successfully![/bold green]")
            
            # Show performance stats
            stats = exporter.client.get_performance_stats()
            _display_performance_stats(stats)
            
        else:
            console.print("[bold red]Sonarr export failed![/bold red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option('--service', type=click.Choice(['radarr', 'sonarr']), required=True,
              help='Service to analyze')
@click.option('--min-score', type=int, default=-50,
              help='Minimum score threshold for upgrade candidates')
@click.option('--limit', type=int, default=20,
              help='Maximum number of candidates to show')
@click.option('--output', type=click.Path(path_type=Path),
              help='Save results to file')
def analyze(service: str, min_score: int, limit: int, output: Optional[Path]):
    """Analyze library and identify upgrade candidates."""
    
    try:
        db_manager = DatabaseManager()
        analyzer = IntelligentAnalyzer(db_manager)
        
        with console.status(f"[bold green]Analyzing {service} library..."):
            candidates = analyzer.identify_upgrade_candidates(service, min_score)
            health_report = analyzer.generate_library_health_report(service)
        
        if not candidates:
            console.print(f"[bold green]No upgrade candidates found! Your {service} library is in excellent shape.[/bold green]")
            return
        
        # Display results
        console.print(f"\n[bold]Library Health: {health_report.health_score:.1f}/100 ({health_report.health_grade})[/bold]")
        console.print(f"[bold]Found {len(candidates)} upgrade candidates[/bold]\n")
        
        # Create table
        table = Table(title=f"Top {min(limit, len(candidates))} Upgrade Candidates")
        table.add_column("Priority", style="bold")
        table.add_column("Title", max_width=40)
        table.add_column("Score", justify="right")
        table.add_column("Potential Gain", justify="right")
        table.add_column("Reason", max_width=50)
        
        priority_colors = {1: "red", 2: "orange3", 3: "yellow", 4: "dim"}
        priority_names = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM", 4: "LOW"}
        
        for candidate in candidates[:limit]:
            color = priority_colors.get(candidate.priority, "dim")
            priority_text = f"[{color}]{priority_names.get(candidate.priority, 'LOW')}[/{color}]"
            gain_text = f"+{candidate.potential_score_gain}" if candidate.potential_score_gain else "N/A"
            
            table.add_row(
                priority_text,
                candidate.media_file.display_name,
                str(candidate.media_file.total_score),
                gain_text,
                candidate.reason
            )
        
        console.print(table)
        
        # Show achievements and warnings
        if health_report.achievements:
            console.print(f"\n[bold green]Achievements:[/bold green]")
            for achievement in health_report.achievements[:3]:
                console.print(f"  - {achievement}")
        
        if health_report.warnings:
            console.print(f"\n[bold red]Warnings:[/bold red]")
            for warning in health_report.warnings[:3]:
                console.print(f"  - {warning}")
        
        # Save to file if requested
        if output:
            _save_analysis_results(candidates, health_report, output)
            console.print(f"\nResults saved to: {output}")
            
    except Exception as e:
        console.print(f"[bold red]Error during analysis: {e}[/bold red]")
        sys.exit(1)


@cli.command()
@click.option('--service', type=click.Choice(['radarr', 'sonarr']), required=True,
              help='Service to generate report for')
@click.option('--output-dir', type=click.Path(path_type=Path),
              help='Output directory for report')
@click.option('--limit', type=int, help='Limit number of files to include in report (for testing)')
def report(service: str, output_dir: Optional[Path], limit: Optional[int]):
    """Generate HTML health report from cached database data.
    
    This command reads data from the local database (no API calls) and creates
    interactive HTML dashboards. To refresh data with latest changes from your
    Arr services, first run the data collection commands:
    
    \b
    arr-export-enhanced radarr    # Refresh Radarr data, then generate report
    arr-export-enhanced sonarr    # Refresh Sonarr data, then generate report
    
    Use this command for fast report generation from existing cached data."""
    
    try:
        if output_dir is None:
            output_dir = Path.cwd() / "reports"
        
        db_manager = DatabaseManager()
        
        # If limit is specified, create a temporary limited database
        temp_db_path = None
        if limit:
            console.print(f"[bold yellow]Creating test report with {limit} files for {service}[/bold yellow]")
            temp_db_path = Path.cwd() / "temp_limited_report.db"
            limited_db_manager = _create_limited_database(db_manager, service, limit, temp_db_path)
            analyzer = IntelligentAnalyzer(limited_db_manager)
            html_reporter = HTMLReporter(output_dir, limited_db_manager)
            actual_db_manager = limited_db_manager
        else:
            analyzer = IntelligentAnalyzer(db_manager)
            html_reporter = HTMLReporter(output_dir, db_manager)
            actual_db_manager = db_manager
        
        try:
            with console.status(f"[bold green]Generating {service} health report..."):
                # Check if we have data first
                library_stats = actual_db_manager.calculate_library_stats(service)
                
                if library_stats.total_files == 0:
                    console.print(f"[bold yellow]No data found for {service}![/bold yellow]")
                    console.print(f"[dim]You need to collect data first by running:[/dim]")
                    console.print(f"[bold cyan]arr-export-enhanced {service}[/bold cyan]")
                    console.print(f"[dim]This will download and analyze your {service} library, then you can generate reports.[/dim]")
                    sys.exit(1)
                
                health_report = analyzer.generate_library_health_report(service)
                
                report_path = html_reporter.generate_library_health_report(
                    health_report, library_stats
                )
            
            console.print(f"[bold green]Report generated successfully![/bold green]")
            console.print(f"Report saved to: {report_path}")
            console.print(f"Open in browser: file://{report_path.absolute()}")
            
            # Show summary
            console.print(f"\n[bold]Health Summary:[/bold]")
            console.print(f"  Score: {health_report.health_score:.1f}/100 ({health_report.health_grade})")
            console.print(f"  Files: {library_stats.total_files:,}")
            console.print(f"  Upgrade Candidates: {len(health_report.upgrade_candidates)}")
            
        finally:
            # Clean up temporary database if created - ensure all connections are closed first
            if limit and temp_db_path and temp_db_path.exists():
                # Force garbage collection to close any lingering connections
                import gc
                gc.collect()
                
                # Small delay to ensure Windows releases file handles
                import time
                time.sleep(0.2)
                
                try:
                    temp_db_path.unlink()
                    console.print(f"[dim]Cleaned up temporary database[/dim]")
                except PermissionError:
                    console.print(f"[dim yellow]Could not remove temporary database (file in use)[/dim yellow]")
        
    except Exception as e:
        console.print(f"[bold red]Error generating report: {e}[/bold red]")
        # Clean up on error too
        if limit and 'temp_db_path' in locals() and temp_db_path and temp_db_path.exists():
            try:
                import gc
                import time
                gc.collect()
                time.sleep(0.2)
                temp_db_path.unlink()
            except PermissionError:
                pass  # Ignore cleanup errors during exception handling
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True, path_type=Path), 
              help='Configuration file path')
def validate_config(config: Optional[Path]):
    """Validate configuration and test API connectivity."""
    
    try:
        # Load configuration
        if config:
            cfg = Config(str(config))
        else:
            cfg = Config()  # Will search for config file
        
        console.print("[bold]Validating configuration...[/bold]\n")
        
        # Check Radarr
        if cfg.is_radarr_enabled():
            _test_service_connection('Radarr', cfg.radarr_url, cfg.radarr_api_key)
        else:
            console.print("[yellow]Radarr not enabled in configuration[/yellow]")
        
        # Check Sonarr
        if cfg.is_sonarr_enabled():
            _test_service_connection('Sonarr', cfg.sonarr_url, cfg.sonarr_api_key)
        else:
            console.print("[yellow]Sonarr not enabled in configuration[/yellow]")
        
        console.print("\n[bold green]Configuration validation completed![/bold green]")
        
    except FileNotFoundError as e:
        console.print(f"[bold red]Configuration file not found: {e}[/bold red]")
        console.print("Create a config.yaml file from config.yaml.example")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Configuration error: {e}[/bold red]")
        sys.exit(1)


def _build_export_config(service_type: str, config_path: Optional[Path], 
                        api_key: Optional[str], url: Optional[str],
                        output_dir: Optional[Path], formats: List[str],
                        max_workers: int, cache: bool, analyze: bool) -> ExportConfig:
    """Build export configuration from CLI options."""
    
    # Load base configuration
    if config_path:
        cfg = Config(str(config_path))
    else:
        cfg = Config()  # Will search for config file
    
    # Get service-specific settings
    if service_type == 'radarr':
        config_api_key = cfg.radarr_api_key
        config_url = cfg.radarr_url
    else:
        config_api_key = cfg.sonarr_api_key
        config_url = cfg.sonarr_url
    
    # Build final configuration
    final_api_key = api_key or config_api_key
    final_url = url or config_url
    
    if not final_api_key or final_api_key == "YOUR_APP_API_KEY_HERE":
        raise click.ClickException(f"API key required for {service_type}")
    
    if not final_url:
        raise click.ClickException(f"URL required for {service_type}")
    
    # Convert formats list
    output_formats = [f for f in formats if f in ['csv', 'json']]
    generate_html = 'html' in formats
    
    return ExportConfig(
        api_key=final_api_key,
        url=final_url,
        max_workers=max_workers,
        cache_enabled=cache,
        cache_dir=output_dir / "cache" if output_dir else None,
        output_formats=output_formats,
        generate_html_report=generate_html,
        store_in_database=True,
        enable_analysis=analyze
    )


def _test_service_connection(service_name: str, url: str, api_key: str):
    """Test connection to a service."""
    import requests
    
    if not url or not api_key or api_key == "YOUR_APP_API_KEY_HERE":
        console.print(f"[yellow]{service_name}: Invalid configuration[/yellow]")
        return
    
    try:
        with console.status(f"Testing {service_name} connection..."):
            response = requests.get(
                f"{url.rstrip('/')}/api/v3/system/status",
                headers={'X-Api-Key': api_key},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        
        console.print(f"[green]{service_name}: Connected successfully[/green]")
        console.print(f"   Version: {data.get('version', 'Unknown')}")
        console.print(f"   URL: {url}")
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]{service_name}: Connection failed - {e}[/red]")


def _display_performance_stats(stats: dict):
    """Display performance statistics."""
    table = Table(title="Performance Statistics")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    
    table.add_row("API Requests", f"{stats['requests_made']:,}")
    table.add_row("Cache Hits", f"{stats['cache_hits']:,}")
    table.add_row("Cache Misses", f"{stats['cache_misses']:,}")
    table.add_row("Cache Hit Rate", f"{stats['cache_hit_rate']:.1f}%")
    
    console.print("\n")
    console.print(table)


def _create_limited_database(source_db: DatabaseManager, service: str, limit: int, temp_db_path: Path) -> DatabaseManager:
    """Create a temporary database with limited entries for testing."""
    # Remove existing temp database if it exists
    if temp_db_path.exists():
        temp_db_path.unlink()
    
    # Create new limited database
    limited_db = DatabaseManager(temp_db_path)
    
    # Copy limited data from source to temporary database
    source_conn = None
    temp_conn = None
    try:
        source_conn = source_db._get_connection()
        temp_conn = limited_db._get_connection()
        
        # Get limited media files (top scored files for better chart visualization)
        files = source_conn.execute("""
            SELECT * FROM media_files 
            WHERE service_type = ? 
            ORDER BY total_score DESC 
            LIMIT ?
        """, (service, limit)).fetchall()
        
        if not files:
            console.print(f"[bold red]No files found for {service} in database[/bold red]")
            return limited_db
        
        # Get column names for media_files
        columns = [desc[0] for desc in source_conn.execute("SELECT * FROM media_files LIMIT 1").description]
        placeholders = ','.join(['?' for _ in columns])
        
        # Insert limited files
        temp_conn.executemany(f"""
            INSERT INTO media_files ({','.join(columns)}) 
            VALUES ({placeholders})
        """, files)
        
        temp_conn.commit()
        
    finally:
        # Explicitly close connections
        if source_conn:
            source_conn.close()
        if temp_conn:
            temp_conn.close()
    
    console.print(f"[dim]Created temporary database with {len(files)} {service} files[/dim]")
    return limited_db


def _save_analysis_results(candidates, health_report, output_path: Path):
    """Save analysis results to file."""
    import json
    
    data = {
        'generated_at': datetime.now().isoformat(),
        'health_report': {
            'service_type': health_report.service_type,
            'health_score': health_report.health_score,
            'health_grade': health_report.health_grade,
            'total_files': health_report.total_files,
            'achievements': health_report.achievements,
            'warnings': health_report.warnings,
            'recommendations': health_report.recommendations
        },
        'upgrade_candidates': [
            {
                'title': c.media_file.display_name,
                'score': c.media_file.total_score,
                'priority': c.priority,
                'reason': c.reason,
                'potential_gain': c.potential_score_gain,
                'recommendation': c.recommendation
            }
            for c in candidates
        ]
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__':
    cli()