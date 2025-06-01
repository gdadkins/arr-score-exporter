"""
Rich HTML reporting system for Arr Score Exporter.

Generates beautiful, interactive HTML reports with charts, tables, and insights
to help users understand their library quality and identify optimization opportunities.
"""

import json
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import webbrowser
import os
import base64

from ..analysis import LibraryHealthReport, UpgradeCandidate
from ..models import LibraryStats, DatabaseManager
from .chart_generators import ChartGenerator
from .html_builders import HTMLSectionBuilder


class HTMLReporter:
    """Generates rich HTML reports with charts and interactive elements."""
    
    def __init__(self, output_dir: Optional[Path] = None, db_manager: Optional[DatabaseManager] = None):
        """Initialize HTML reporter."""
        if output_dir is None:
            output_dir = Path.cwd() / "reports"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_manager = db_manager
        self.chart_generator = ChartGenerator(db_manager)
        self.section_builder = HTMLSectionBuilder(db_manager)
    
    def generate_library_health_report(self, health_report: LibraryHealthReport,
                                     library_stats: LibraryStats) -> Path:
        """Generate comprehensive HTML library health report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{health_report.service_type}_health_report_{timestamp}.html"
        output_path = self.output_dir / filename
        
        html_content = self._build_health_report_html(health_report, library_stats)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _build_health_report_html(self, health_report: LibraryHealthReport,
                                library_stats: LibraryStats) -> str:
        """Build the complete HTML content for health report."""
        
        # Generate chart data
        score_distribution_chart = self.chart_generator.create_score_distribution_chart(library_stats)
        format_effectiveness_chart = self.chart_generator.create_format_effectiveness_chart(health_report)
        
        # Load external CSS and JS
        css_content = self._load_asset_content('css/report.css')
        js_content = self._load_asset_content('js/dashboard.js')
        
        # Build HTML sections
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{health_report.service_type.title()} Library Health Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/pdfmake.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/vfs_fonts.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css">
    <style>
        {css_content}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{health_report.service_type.title()} Library Health Report</h1>
            <div class="report-meta">
                <span>Generated: {health_report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</span>
                <div class="health-score">
                    <span class="score-label">Health Score:</span>
                    <span class="score-value grade-{health_report.health_grade.lower()}">{health_report.health_score:.1f}/100</span>
                    <span class="score-grade">({health_report.health_grade})</span>
                </div>
            </div>
        </header>

        <div class="summary-cards">
            <div class="card">
                <h3>Total Files</h3>
                <div class="metric-value">{library_stats.total_files:,}</div>
            </div>
            <div class="card">
                <h3>Average Score</h3>
                <div class="metric-value {'positive' if library_stats.avg_score > 0 else 'negative'}">{library_stats.avg_score:.1f}</div>
            </div>
            <div class="card">
                <h3>Upgrade Candidates</h3>
                <div class="metric-value">{len(health_report.upgrade_candidates)}</div>
            </div>
            <div class="card">
                <h3>Total Size</h3>
                <div class="metric-value">{library_stats.total_size_gb / 1024:.1f} TB</div>
            </div>
        </div>

        {self._build_achievements_warnings_section(health_report)}
        
        <div class="chart-section">
            <h2>Visual Analytics</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>Score Distribution</h3>
                    <canvas id="scoreDistChart"></canvas>
                    <div class="chart-interaction-hint">💡 Click the grey "Zero Scores" area to view details</div>
                </div>
                <div class="chart-container">
                    <h3>Custom Format Effectiveness</h3>
                    <canvas id="formatEffectivenessChart"></canvas>
                </div>
            </div>
        </div>

        {self.section_builder.build_dashboard_controls()}
        
        {self.section_builder.build_zero_scores_table_section(health_report, library_stats)}
        
        {self.section_builder.build_upgrade_candidates_section(health_report)}
        
        {self.section_builder.build_intelligent_categories_section(health_report)}
        
        <div class="collapsible-section">
            <button class="collapsible">Advanced Analysis</button>
            <div class="collapsible-content">
                {self.section_builder.build_quality_profile_analysis_section(health_report)}
                {self.section_builder.build_format_analysis_section(health_report)}
                {self.section_builder.build_historical_trends_section(health_report)}
            </div>
        </div>
        
        <footer class="footer">
            <p>Report generated by Arr Score Exporter on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>

    <script>
        {js_content}
        
        // Initialize dashboard data
        dashboardData = {self._generate_dashboard_data(health_report, library_stats)};
        
        // Function to initialize charts (called from dashboard.js DOMContentLoaded)
        function initializeCharts() {{
            try {{
                // Initialize dashboard data
                initializeDashboardData(dashboardData);
                
                // Initialize charts with proper context
                const scoreDistCtx = document.getElementById('scoreDistChart')?.getContext('2d');
                if (scoreDistCtx) {{
                    scoreDistributionChart = new Chart(scoreDistCtx, {score_distribution_chart});
                    
                    // Add onClick handler for zero scores functionality
                    scoreDistributionChart.options.onClick = function(event, activeElements) {{
                        handleScoreDistributionClick(event, activeElements);
                    }};
                    scoreDistributionChart.update();
                }} else {{
                    console.warn('Score distribution chart canvas not found');
                }}
                
                const formatEffCtx = document.getElementById('formatEffectivenessChart')?.getContext('2d');
                if (formatEffCtx) {{
                    formatEffectivenessChart = new Chart(formatEffCtx, {format_effectiveness_chart});
                }} else {{
                    console.warn('Format effectiveness chart canvas not found');
                }}
                
            }} catch (error) {{
                console.error('Error initializing charts:', error);
            }}
        }}
    </script>
</body>
</html>
"""
        
        return html
    
    def _build_achievements_warnings_section(self, health_report: LibraryHealthReport) -> str:
        """Build the achievements section."""
        if not health_report.achievements:
            return ""
        
        sections = []
        
        if health_report.achievements:
            sections.append(self.section_builder.build_achievements_section(health_report))
        
        return f'<div class="status-section">{"".join(sections)}</div>' if sections else ""
    
    def _load_asset_content(self, asset_path: str) -> str:
        """Load content from asset files."""
        assets_dir = Path(__file__).parent / "assets"
        file_path = assets_dir / asset_path
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def _generate_dashboard_data(self, health_report: LibraryHealthReport, 
                               library_stats: LibraryStats) -> str:
        """Generate JSON data for dashboard interactivity."""
        data = {
            'service_type': health_report.service_type,
            'generated_at': health_report.generated_at.isoformat(),
            'health_score': health_report.health_score,
            'health_grade': health_report.health_grade,
            'total_files': library_stats.total_files,
            'avg_score': library_stats.avg_score
        }
        
        return json.dumps(data, indent=2)
    
    def list_reports(self) -> List[Dict[str, Any]]:
        """List all generated reports."""
        reports = []
        
        if not self.output_dir.exists():
            return reports
        
        for file_path in self.output_dir.glob("*_health_report_*.html"):
            stats = file_path.stat()
            reports.append({
                'path': file_path,
                'name': file_path.name,
                'service_type': self._extract_service_type(file_path.name),
                'created': datetime.fromtimestamp(stats.st_mtime),
                'size_kb': stats.st_size / 1024
            })
        
        # Sort by creation date, newest first
        reports.sort(key=lambda x: x['created'], reverse=True)
        return reports
    
    def _extract_service_type(self, filename: str) -> str:
        """Extract service type from filename."""
        if filename.startswith('radarr_'):
            return 'radarr'
        elif filename.startswith('sonarr_'):
            return 'sonarr'
        return 'unknown'
    
    def open_latest_report(self, service_type: Optional[str] = None) -> bool:
        """Open the latest report in browser."""
        reports = self.list_reports()
        
        if service_type:
            reports = [r for r in reports if r['service_type'] == service_type]
        
        if not reports:
            print("No reports found.")
            return False
        
        latest_report = reports[0]
        return self.open_report(latest_report['path'])
    
    def open_report(self, report_path: Path) -> bool:
        """Open a specific report in the browser."""
        if not report_path.exists():
            print(f"Report not found: {report_path}")
            return False
        
        try:
            # Convert to file URL for browser
            file_url = f"file://{report_path.absolute()}"
            webbrowser.open(file_url)
            print(f"Opened report in browser: {report_path.name}")
            return True
        except Exception as e:
            print(f"Failed to open report: {e}")
            return False
    
    def print_reports_list(self) -> None:
        """Print a formatted list of available reports."""
        reports = self.list_reports()
        
        if not reports:
            print("No reports found.")
            return
        
        print("\nAvailable Reports:")
        print("-" * 80)
        print(f"{'Service':<10} {'Filename':<40} {'Created':<20} {'Size':<10}")
        print("-" * 80)
        
        for report in reports:
            created_str = report['created'].strftime('%Y-%m-%d %H:%M:%S')
            size_str = f"{report['size_kb']:.1f} KB"
            print(f"{report['service_type']:<10} {report['name']:<40} {created_str:<20} {size_str:<10}")
        
        print(f"\nTotal reports: {len(reports)}")
        print(f"Reports directory: {self.output_dir}")