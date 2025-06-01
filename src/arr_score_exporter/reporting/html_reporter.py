"""
Rich HTML reporting system for Arr Score Exporter.

Generates beautiful, interactive HTML reports with charts, tables, and insights
to help users understand their library quality and identify optimization opportunities.
"""

import json
import html
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import base64
from io import BytesIO

from ..analysis import LibraryHealthReport, UpgradeCandidate
from ..models import LibraryStats, DatabaseManager


class HTMLReporter:
    """Generates rich HTML reports with charts and interactive elements."""
    
    def __init__(self, output_dir: Optional[Path] = None, db_manager: Optional[DatabaseManager] = None):
        """Initialize HTML reporter."""
        if output_dir is None:
            output_dir = Path.cwd() / "reports"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_manager = db_manager
    
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
        score_distribution_chart = self._create_score_distribution_chart(library_stats)
        format_effectiveness_chart = self._create_format_effectiveness_chart(health_report)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{health_report.service_type.title()} Library Health Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css">
    <style>
        {self._get_css_styles()}
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
                <h3>Quality Profiles</h3>
                <div class="metric-value">{len(health_report.quality_profile_analysis)}</div>
            </div>
        </div>        {self._build_dashboard_controls()}
        {self._build_achievements_section(health_report) if health_report.achievements else ''}

        <div class="charts-grid two-column">
            <div class="chart-container">
                <h3>Score Distribution</h3>
                <canvas id="scoreDistChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Custom Format Effectiveness</h3>
                <canvas id="formatEffectivenessChart"></canvas>
            </div>
        </div>

        <div class="charts-grid enhanced-viz">
            <div class="chart-container">
                <h3>Score vs File Size Analysis</h3>
                <canvas id="scoreFileSizeScatter"></canvas>
            </div>
        </div>


        {self._build_upgrade_candidates_section(health_report)}
        {self._build_quality_profile_analysis_section(health_report)}
        
        <div class="advanced-toggle">
            <button id="advancedToggle" onclick="toggleAdvanced()" class="btn-toggle">Show Advanced Analysis</button>
        </div>

        <div id="advancedSections" class="advanced-sections collapsed">
            {self._build_format_analysis_section(health_report)}
            {self._build_intelligent_categories_section(health_report)}
            {self._build_historical_trends_section(health_report)}
            {self._build_recommendations_section(health_report)}
        </div>

        <footer class="footer">
            <p>Generated by Arr Score Exporter - TRaSH Guides Custom Format Analysis Tool</p>
        </footer>
    </div>

    <script>
        // Dashboard data for filtering and interactivity
        window.dashboardData = {self._generate_dashboard_data(health_report, library_stats)};
        
        {score_distribution_chart}
        {format_effectiveness_chart}
        
        {self._create_score_filesize_scatter(health_report, library_stats)}
        
        {self._generate_datatables_js()}
        {self._generate_dashboard_js()}
    </script>
</body>
</html>"""
        
        return html
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .report-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 1.1em;
        }

        .health-score {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .score-value {
            font-size: 1.8em;
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
        }

        .grade-a { background-color: #28a745; }
        .grade-b { background-color: #17a2b8; }
        .grade-c { background-color: #ffc107; color: #212529; }
        .grade-d { background-color: #fd7e14; }
        .grade-f { background-color: #dc3545; }

        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }

        .card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }

        .card h3 {
            color: #666;
            margin-bottom: 8px;
            font-size: 0.95em;
        }

        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }

        .metric-value.positive { color: #28a745; }
        .metric-value.negative { color: #dc3545; }

        .status-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .status-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .status-card h3 {
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
        }

        .achievements .status-icon { background-color: #28a745; }
        .warnings .status-icon { background-color: #dc3545; }

        .status-list {
            list-style: none;
        }

        .status-list li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }

        .status-list li:last-child {
            border-bottom: none;
        }        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }

        .charts-grid.two-column {
            grid-template-columns: repeat(2, 1fr);
        }

        .charts-grid.enhanced-viz {
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
        }

        .chart-container.wide {
            grid-column: 1 / -1;
            min-height: 300px;
            max-height: 400px;
        }

        .chart-container {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-height: 350px;
        }

        .chart-container h3 {
            margin-bottom: 15px;
            color: #333;
            text-align: center;
            font-size: 1.1em;
        }

        .chart-container canvas {
            max-height: 280px !important;
        }

        .section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }

        .section h2 {
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 8px;
            font-size: 1.3em;
        }

        .upgrade-table, .profile-table, .format-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        /* Dashboard Controls */
        .dashboard-controls {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .controls-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .btn-toggle {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            transition: background-color 0.2s;
        }

        .btn-toggle:hover {
            background: #5a6fd8;
        }

        .btn-toggle.active {
            background: #28a745;
        }

        .filters-panel {
            display: none;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }

        .filters-panel.active {
            display: block;
        }

        .filter-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
        }

        .filter-group label {
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
        }

        .range-slider {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .range-display {
            text-align: center;
            font-weight: bold;
            color: #667eea;
            font-size: 0.9em;
        }

        .checkbox-group {
            max-height: 120px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 8px;
        }

        .checkbox-group label {
            font-weight: normal;
            margin: 5px 0;
            display: flex;
            align-items: center;
        }

        .checkbox-group input[type="checkbox"] {
            margin-right: 8px;
        }

        /* DataTables Styling */
        .dataTables_wrapper {
            margin-top: 20px;
        }

        .dataTables_filter {
            margin-bottom: 20px;
        }

        .dataTables_length {
            margin-bottom: 20px;
        }

        .filter-summary {
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.9em;
            color: #495057;
            border-left: 3px solid #667eea;
        }

        /* Enhanced button styling */
        .dt-buttons {
            margin-bottom: 15px;
        }

        .dt-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            padding: 6px 12px !important;
            border-radius: 4px !important;
            margin-right: 5px !important;
            font-size: 0.9em !important;
            transition: transform 0.2s !important;
        }

        .dt-button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        }

        /* Responsive enhancements */
        @media (max-width: 768px) {
            .filter-grid {
                grid-template-columns: 1fr;
            }
            
            .controls-header {
                flex-direction: column;
                gap: 10px;
            }
            
            .filter-summary {
                text-align: center;
                margin-top: 10px;
            }
        }

        .upgrade-table th, .upgrade-table td,
        .profile-table th, .profile-table td,
        .format-table th, .format-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        .upgrade-table th, .profile-table th, .format-table th {
            background-color: #f8f9fa;
            font-weight: 600;
        }

        .priority-1 { color: #dc3545; font-weight: bold; }
        .priority-2 { color: #fd7e14; font-weight: bold; }
        .priority-3 { color: #ffc107; }
        .priority-4 { color: #6c757d; }

        .effectiveness-excellent { color: #28a745; font-weight: bold; }
        .effectiveness-good { color: #17a2b8; }
        .effectiveness-fair { color: #ffc107; }
        .effectiveness-poor { color: #dc3545; }

        .impact-high { color: #28a745; font-weight: bold; }
        .impact-medium { color: #17a2b8; }
        .impact-low { color: #6c757d; }
        .impact-negative { color: #dc3545; font-weight: bold; }

        .recommendations-list {
            list-style-type: disc;
            margin-left: 20px;
        }

        .recommendations-list li {
            margin-bottom: 8px;
        }

        /* Upgrade Criteria Info Styling */
        .upgrade-criteria-info {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }

        .upgrade-criteria-info h4 {
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.1em;
        }

        .criteria-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }

        .criteria-item {
            background: white;
            padding: 12px 15px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            font-size: 0.9em;
            line-height: 1.4;
        }

        .criteria-item strong {
            color: #495057;
            display: block;
            margin-bottom: 4px;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #ddd;
            margin-top: 30px;
        }

        /* Phase 2: Enhanced Sections Styling */
        .categories-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .category-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .category-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
            border-color: #667eea;
        }

        .category-card:active {
            transform: translateY(-1px);
        }

        .category-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }

        .category-icon {
            font-size: 1.5em;
            margin-right: 10px;
        }

        .category-info {
            flex: 1;
        }

        .category-info h4 {
            margin: 0;
            color: #333;
            font-size: 1em;
        }

        .category-description {
            margin: 2px 0 0 0;
            color: #666;
            font-size: 0.85em;
        }

        .category-count {
            background: #667eea;
            color: white;
            border-radius: 10px;
            padding: 3px 7px;
            font-weight: bold;
            font-size: 0.85em;
            min-width: 20px;
            text-align: center;
        }

        .category-samples {
            font-size: 0.8em;
            color: #555;
            line-height: 1.3;
            margin-top: 8px;
        }

        .trend-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .metric-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border: 1px solid #dee2e6;
        }

        .metric-card h4 {
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 0.9em;
        }

        .metric-card .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }

        .metric-card .metric-label {
            color: #6c757d;
            font-size: 0.8em;
        }

        .trend-patterns, .trend-recommendations {
            margin: 20px 0;
        }

        .pattern-list, .trend-rec-list {
            list-style-type: none;
            padding-left: 0;
        }

        .pattern-list li, .trend-rec-list li {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 0 4px 4px 0;
        }

        /* Modal styling */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }

        .modal-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .modal-content {
            background: white;
            padding: 25px;
            border-radius: 10px;
            max-width: 90%;
            max-height: 85%;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transform: scale(0.7);
            transition: transform 0.3s ease;
            margin: auto;
        }

        .modal-overlay.active .modal-content {
            transform: scale(1);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #667eea;
        }

        .modal-header h3 {
            margin: 0;
            color: #333;
            font-size: 1.5em;
        }

        .modal-close {
            background: none;
            border: none;
            font-size: 1.5em;
            cursor: pointer;
            color: #666;
            padding: 5px 10px;
            border-radius: 5px;
            transition: background-color 0.2s;
        }

        .modal-close:hover {
            background-color: #f8f9fa;
            color: #333;
        }

        .file-list {
            display: grid;
            gap: 15px;
        }

        .file-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .file-item strong {
            display: block;
            color: #333;
            margin-bottom: 8px;
            font-size: 1.1em;
        }

        .file-item p {
            margin: 4px 0;
            color: #666;
            font-size: 0.9em;
        }

        /* Advanced sections collapsible */
        .advanced-toggle {
            text-align: center;
            margin: 30px 0;
        }

        .advanced-sections {
            overflow: hidden;
            transition: all 0.5s ease;
            max-height: 1000000px;
            opacity: 1;
        }

        .advanced-sections.collapsed {
            max-height: 0;
            opacity: 0;
            margin: 0;
            padding: 0;
        }

        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .chart-container {
                min-width: auto;
                max-height: 300px;
            }
            
            .chart-container canvas {
                max-height: 220px !important;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
            
            .report-meta {
                flex-direction: column;
                gap: 8px;
            }

            .categories-grid {
                grid-template-columns: 1fr;
            }

            .trend-metrics {
                grid-template-columns: 1fr;
            }
            
            .criteria-grid {
                grid-template-columns: 1fr;
            }
            
            .summary-cards {
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }
            
            .card {
                padding: 12px;
            }
            
            .metric-value {
                font-size: 1.5em;
            }        }
        """
    
    def _build_achievements_section(self, health_report: LibraryHealthReport) -> str:
        """Build achievements section."""
        if not health_report.achievements:
            return ""
        
        return f"""
        <div class="status-section">
            <div class="status-card achievements">
                <h3><span class="status-icon"></span>Achievements</h3>
                <ul class="status-list">
                    {self._build_status_list(health_report.achievements, "Working towards achievements...")}
                </ul>
            </div>
        </div>
        """
    
    def _build_status_list(self, items: List[str], empty_message: str) -> str:
        """Build HTML list from status items."""
        if not items:
            return f"<li>{empty_message}</li>"
        return "".join(f"<li>{item}</li>" for item in items)
    
    def _build_upgrade_candidates_section(self, health_report: LibraryHealthReport) -> str:
        """Build upgrade candidates section with pagination and enhanced information."""
        if not health_report.upgrade_candidates:
            return """
            <div class="section">
                <h2>Upgrade Candidates</h2>
                <p>No upgrade candidates identified. Your library is in excellent shape!</p>
            </div>
            """
        
        candidates_html = ""
        # Show more candidates by default with pagination
        for candidate in health_report.upgrade_candidates:  # Show all candidates with pagination
            priority_class = f"priority-{candidate.priority}"
            potential_gain = f"+{candidate.potential_score_gain}" if candidate.potential_score_gain else "N/A"
            
            # Add file size information
            file_size = "N/A"
            if candidate.media_file.size_bytes:
                size_gb = candidate.media_file.size_bytes / (1024**3)
                file_size = f"{size_gb:.1f} GB"
            
            # Add resolution/type information
            resolution_type = "Unknown"
            if candidate.media_file.resolution:
                resolution_type = str(candidate.media_file.resolution)
                # Add quality context
                if "2160p" in resolution_type or "4K" in resolution_type:
                    resolution_type += " (4K)"
                elif "1080p" in resolution_type:
                    resolution_type += " (HD)"
                elif "720p" in resolution_type:
                    resolution_type += " (SD)"
            
            candidates_html += f"""
                <tr>
                    <td>{candidate.media_file.display_name}</td>
                    <td class="{priority_class}">{'Critical' if candidate.priority == 1 else 'High' if candidate.priority == 2 else 'Medium' if candidate.priority == 3 else 'Low'}</td>
                    <td>{candidate.media_file.total_score}</td>
                    <td>{potential_gain}</td>
                    <td>{file_size}</td>
                    <td>{resolution_type}</td>
                    <td>{candidate.reason}</td>
                    <td>{candidate.recommendation or 'Review manually'}</td>
                </tr>
            """
        
        total_candidates = len(health_report.upgrade_candidates)
        return f"""
        <div class="section">
            <h2>Upgrade Candidates ({total_candidates} found)</h2>
            <p>Files that would benefit most from upgrades based on TRaSH Guides scoring. Use search and filtering to find specific files.</p>
            
            <div class="upgrade-criteria-info">
                <h4>What qualifies as an Upgrade Candidate?</h4>
                <div class="criteria-grid">
                    <div class="criteria-item">
                        <strong>Low Score Threshold:</strong> Files with TRaSH score ≤ {getattr(health_report, 'min_score_threshold', -50)}
                    </div>
                    <div class="criteria-item">
                        <strong>Below Library Average:</strong> Files scoring significantly below your library's average
                    </div>
                    <div class="criteria-item">
                        <strong>Negative Formats:</strong> Files with custom formats that reduce quality score
                    </div>
                    <div class="criteria-item">
                        <strong>Size vs Quality:</strong> Large files with poor quality scores (inefficient)
                    </div>
                    <div class="criteria-item">
                        <strong>Missing HDR:</strong> 4K files without HDR10 or Dolby Vision formats
                    </div>
                    <div class="criteria-item">
                        <strong>Priority Levels:</strong> Critical (1) > High (2) > Medium (3) > Low (4)
                    </div>
                </div>
            </div>
            <table id="upgradeTable" class="upgrade-table display">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Priority</th>
                        <th>Current Score</th>
                        <th>Potential Gain</th>
                        <th>File Size</th>
                        <th>Type/Resolution</th>
                        <th>Reason</th>
                        <th>Recommendation</th>
                    </tr>
                </thead>
                <tbody>
                    {candidates_html}
                </tbody>
            </table>
        </div>
        """
    
    def _build_quality_profile_analysis_section(self, health_report: LibraryHealthReport) -> str:
        """Build quality profile analysis section."""
        if not health_report.quality_profile_analysis:
            return ""
        
        profiles_html = ""
        for profile in health_report.quality_profile_analysis:
            effectiveness_class = f"effectiveness-{profile.effectiveness_rating}"
            
            profiles_html += f"""
                <tr>
                    <td>{profile.profile_name}</td>
                    <td>{profile.file_count:,}</td>
                    <td>{profile.avg_score:.1f}</td>
                    <td class="{effectiveness_class}">{profile.effectiveness_rating.title()}</td>
                    <td>{'; '.join(profile.common_issues) if profile.common_issues else 'None identified'}</td>
                </tr>
            """
        
        return f"""
        <div class="section">
            <h2>Quality Profile Analysis</h2>
            <table id="profileTable" class="profile-table display">
                <thead>
                    <tr>
                        <th>Profile Name</th>
                        <th>File Count</th>
                        <th>Avg Score</th>
                        <th>Effectiveness</th>
                        <th>Issues</th>
                    </tr>
                </thead>
                <tbody>
                    {profiles_html}
                </tbody>
            </table>
        </div>
        """
    
    def _build_format_analysis_section(self, health_report: LibraryHealthReport) -> str:
        """Build custom format analysis section."""
        if not health_report.format_effectiveness:
            return ""
        
        formats_html = ""
        for fmt in health_report.format_effectiveness[:15]:  # Top 15
            impact_class = f"impact-{fmt.impact_rating}"
            
            formats_html += f"""
                <tr>
                    <td>{fmt.format_name}</td>
                    <td>{fmt.usage_count:,}</td>
                    <td>{fmt.avg_score_contribution:.1f}</td>
                    <td class="{impact_class}">{fmt.impact_rating.title()}</td>
                    <td>{'; '.join(fmt.recommendations) if fmt.recommendations else 'Working well'}</td>
                </tr>
            """
        
        return f"""
        <div class="section">
            <h2>Custom Format Effectiveness (Top 15)</h2>
            <table id="formatTable" class="format-table display">
                <thead>
                    <tr>
                        <th>Format Name</th>
                        <th>Usage Count</th>
                        <th>Avg Score Impact</th>
                        <th>Impact Rating</th>
                        <th>Recommendations</th>
                    </tr>
                </thead>
                <tbody>
                    {formats_html}
                </tbody>
            </table>
        </div>
        """
    
    def _build_recommendations_section(self, health_report: LibraryHealthReport) -> str:
        """Build recommendations section."""
        if not health_report.recommendations:
            return ""
        
        recommendations_html = "".join(f"<li>{rec}</li>" for rec in health_report.recommendations)
        
        return f"""
        <div class="section">
            <h2>Recommendations</h2>
            <ul class="recommendations-list">
                {recommendations_html}
            </ul>
        </div>
        """
    
    def _build_intelligent_categories_section(self, health_report: LibraryHealthReport) -> str:
        """Build intelligent file categorization section."""
        if not hasattr(health_report, 'intelligent_categories') or health_report.intelligent_categories is None:
            return """
            <div class="section">
                <h2>📋 Smart File Categorization</h2>
                <p>Smart categorization data not available. Please run enhanced analysis to generate this report.</p>
            </div>
            """
        
        categories = health_report.intelligent_categories
        category_info = {
            'premium_quality': ('🏆', 'Premium Quality', 'Files with excellent scores and optimal formats'),
            'acceptable_quality': ('✅', 'Acceptable Quality', 'Files meeting quality standards'),
            'upgrade_worthy': ('⬆️', 'Upgrade Worthy', 'Files that would benefit from upgrades'),
            'priority_replacements': ('🚨', 'Priority Replacements', 'Files requiring immediate attention'),
            'large_low_quality': ('📦', 'Size/Quality Issues', 'Large files with poor quality scores'),
            'format_optimized': ('🎯', 'Format Optimized', 'Files with excellent format usage'),
            'legacy_content': ('📼', 'Legacy Content', 'Files using outdated/problematic formats'),
            'hdr_candidates': ('🌈', 'HDR Candidates', '4K files missing HDR formats'),
            'audio_upgrade_candidates': ('🔊', 'Audio Upgrades', 'Files with suboptimal audio formats'),
            'resolution_mismatches': ('📺', 'Resolution Issues', 'Files with quality/resolution mismatches')
        }
        
        # Filter categories with files
        active_categories = {k: v for k, v in categories.items() if v}
        
        if not active_categories:
            return """
            <div class="section">
                <h2>📋 Smart File Categorization</h2>
                <p>All files are properly categorized with no specific issues detected.</p>
            </div>
            """
        
        cards_html = ""
        for category, files in active_categories.items():
            if category in category_info:
                icon, title, description = category_info[category]
                count = len(files)
                
                # Get sample file names (first 3)
                sample_files = files[:3]
                sample_names = [f.display_name[:40] + '...' if len(f.display_name) > 40 else f.display_name 
                              for f in sample_files]
                  # Generate file data for modal
                file_data = []
                for f in files[:20]:  # Limit to 20 for performance
                    file_data.append({
                        'title': f.display_name,
                        'score': getattr(f, 'total_score', 'N/A'),
                        'reason': f'Categorized as {title.lower()}',
                        'recommendation': f'Review and consider upgrading if in {title.lower()} category'
                    })
                
                # Properly escape JSON for HTML attribute
                import html
                file_data_js = html.escape(json.dumps(file_data))
                cards_html += f"""
                <div class="category-card" data-category="{title}" data-files='{file_data_js}' onclick="showCategoryModal(this)">
                    <div class="category-header">
                        <span class="category-icon">{icon}</span>
                        <div class="category-info">
                            <h4>{title}</h4>
                            <p class="category-description">{description}</p>
                        </div>
                        <div class="category-count">{count}</div>
                    </div>
                    <div class="category-samples">
                        {'<br>'.join(sample_names)}
                        {f'<br><em>... and {count - 3} more (click to view all)</em>' if count > 3 else ''}
                    </div>
                </div>
                """
        
        return f"""
        <div class="section">
            <h2>📋 Smart File Categorization</h2>
            <p>Automated categorization based on scoring patterns, formats, and metadata analysis.</p>
            <div class="categories-grid">
                {cards_html}
            </div>
        </div>
        """
    
    def _build_historical_trends_section(self, health_report: LibraryHealthReport) -> str:
        """Build historical trends analysis section."""
        if not hasattr(health_report, 'historical_analysis') or health_report.historical_analysis is None:
            return """
            <div class="section">
                <h2>Historical Trend Analysis</h2>
                <p>Historical trend data not available. Please run enhanced analysis over time to generate this report.</p>
            </div>
            """
        
        analysis = health_report.historical_analysis
        
        # Velocity metrics
        velocity_html = f"""
        <div class="trend-metrics">
            <div class="metric-card">
                <h4>📈 Improvement Velocity</h4>
                <div class="metric-value">{analysis['improvement_velocity']:.1f}</div>
                <div class="metric-label">improvements/week</div>
            </div>
            <div class="metric-card">
                <h4>📉 Degradation Velocity</h4>
                <div class="metric-value">{analysis['degradation_velocity']:.1f}</div>
                <div class="metric-label">degradations/week</div>
            </div>
            <div class="metric-card">
                <h4>⚡ Net Velocity</h4>
                <div class="metric-value {'positive' if analysis['net_velocity'] >= 0 else 'negative'}">{analysis['net_velocity']:+.1f}</div>
                <div class="metric-label">net change/week</div>
            </div>
        </div>
        """
        
        # Patterns
        patterns_html = ""
        if analysis['patterns']:
            patterns_html = """
            <div class="trend-patterns">
                <h4>📊 Detected Patterns</h4>
                <ul class="pattern-list">
            """
            for pattern in analysis['patterns']:
                patterns_html += f"<li>{pattern}</li>"
            patterns_html += "</ul></div>"
        
        # Trend recommendations
        trend_recs_html = ""
        if analysis['recommendations']:
            trend_recs_html = """
            <div class="trend-recommendations">
                <h4>💡 Trend-Based Recommendations</h4>
                <ul class="trend-rec-list">
            """
            for rec in analysis['recommendations']:
                trend_recs_html += f"<li>{rec}</li>"
            trend_recs_html += "</ul></div>"
        
        return f"""
        <div class="section">
            <h2>Historical Trend Analysis</h2>
            <p>Advanced analytics tracking library quality changes over time with predictive insights.</p>
            {velocity_html}
            {patterns_html}
            {trend_recs_html}
        </div>
        """
    
    def _create_score_distribution_chart(self, stats: LibraryStats) -> str:
        """Create JavaScript for score distribution chart."""
        # Safely get score distribution data with defaults
        positive_scores = getattr(stats, 'files_with_positive_scores', 0) or 0
        zero_scores = getattr(stats, 'files_with_zero_scores', 0) or 0
        negative_scores = getattr(stats, 'files_with_negative_scores', 0) or 0
        
        # Check if we have any data
        total_files = positive_scores + zero_scores + negative_scores
        if total_files == 0:
            return """
            const scoreDistCtx = document.getElementById('scoreDistChart').getContext('2d');
            if (scoreDistCtx) {
                scoreDistCtx.font = '16px Arial';
                scoreDistCtx.fillStyle = '#666';
                scoreDistCtx.textAlign = 'center';
                scoreDistCtx.fillText('No score distribution data available', scoreDistCtx.canvas.width/2, scoreDistCtx.canvas.height/2);
                scoreDistCtx.fillText('Run analysis to generate score data', scoreDistCtx.canvas.width/2, scoreDistCtx.canvas.height/2 + 25);
            }
            """
        
        return f"""
        try {{
            const scoreDistCtx = document.getElementById('scoreDistChart').getContext('2d');
            if (!scoreDistCtx) {{
                console.warn('Score distribution chart canvas not found');
            }} else {{
            
            new Chart(scoreDistCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Positive Scores', 'Zero Scores', 'Negative Scores'],
                    datasets: [{{
                        data: [{positive_scores}, {zero_scores}, {negative_scores}],
                        backgroundColor: ['#28a745', '#6c757d', '#dc3545'],
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
            }}
        }} catch (error) {{
            console.error('Error rendering score distribution chart:', error);
            const scoreDistCtx = document.getElementById('scoreDistChart').getContext('2d');
            if (scoreDistCtx) {{
                scoreDistCtx.font = '16px Arial';
                scoreDistCtx.fillStyle = '#dc3545';
                scoreDistCtx.textAlign = 'center';
                scoreDistCtx.fillText('Error rendering score distribution', scoreDistCtx.canvas.width/2, scoreDistCtx.canvas.height/2);
            }}
        }}
        """
    
    
    def _create_format_effectiveness_chart(self, health_report: LibraryHealthReport) -> str:
        """Create JavaScript for format effectiveness chart."""
        # Safely get format effectiveness data
        format_effectiveness = getattr(health_report, 'format_effectiveness', None)
        
        if not format_effectiveness:
            return """
            const formatEffCtx = document.getElementById('formatEffectivenessChart').getContext('2d');
            if (formatEffCtx) {
                formatEffCtx.font = '16px Arial';
                formatEffCtx.fillStyle = '#666';
                formatEffCtx.textAlign = 'center';
                formatEffCtx.fillText('No custom format data available', formatEffCtx.canvas.width/2, formatEffCtx.canvas.height/2);
                formatEffCtx.fillText('Run analysis on a library with custom formats', formatEffCtx.canvas.width/2, formatEffCtx.canvas.height/2 + 25);
            }
            """
        
        try:
            formats = format_effectiveness[:10]  # Top 10
            
            # Safely extract data with validation
            labels = []
            scores = []
            for fmt in formats:
                try:
                    name = getattr(fmt, 'format_name', 'Unknown Format') or 'Unknown Format'
                    score = getattr(fmt, 'avg_score_contribution', 0) or 0
                    
                    # Validate and sanitize
                    if isinstance(score, (int, float)) and not (isinstance(score, float) and (score != score)):  # Check for NaN
                        labels.append(str(name)[:50])  # Limit length
                        scores.append(float(score))
                except (AttributeError, TypeError, ValueError):
                    continue
            
            if not labels or not scores:
                return """
                const formatEffCtx = document.getElementById('formatEffectivenessChart').getContext('2d');
                if (formatEffCtx) {
                    formatEffCtx.font = '16px Arial';
                    formatEffCtx.fillStyle = '#666';
                    formatEffCtx.textAlign = 'center';
                    formatEffCtx.fillText('No valid format effectiveness data', formatEffCtx.canvas.width/2, formatEffCtx.canvas.height/2);
                }
                """
            
            # Generate colors safely
            colors = []
            for s in scores:
                try:
                    if s > 20:
                        colors.append('#28a745')
                    elif s > 0:
                        colors.append('#17a2b8')
                    else:
                        colors.append('#dc3545')
                except (TypeError, ValueError):
                    colors.append('#6c757d')  # Gray for invalid data
                    
        except (AttributeError, TypeError, IndexError):
            return """
            const formatEffCtx = document.getElementById('formatEffectivenessChart').getContext('2d');
            if (formatEffCtx) {
                formatEffCtx.font = '16px Arial';
                formatEffCtx.fillStyle = '#dc3545';
                formatEffCtx.textAlign = 'center';
                formatEffCtx.fillText('Error processing format effectiveness data', formatEffCtx.canvas.width/2, formatEffCtx.canvas.height/2);
            }
            """
        
        return f"""
        try {{
            const formatEffCtx = document.getElementById('formatEffectivenessChart').getContext('2d');
            if (!formatEffCtx) {{
                console.warn('Format effectiveness chart canvas not found');
            }} else {{
            
            new Chart(formatEffCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(labels)},
                    datasets: [{{
                        label: 'Avg Score Impact',
                        data: {json.dumps(scores)},
                        backgroundColor: {json.dumps(colors)}
                    }}]
                }},
                options: {{
                    responsive: true,
                    indexAxis: 'y',
                    scales: {{
                        x: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
            }}
        }} catch (error) {{
            console.error('Error rendering format effectiveness chart:', error);
            const formatEffCtx = document.getElementById('formatEffectivenessChart').getContext('2d');
            if (formatEffCtx) {{
                formatEffCtx.font = '16px Arial';
                formatEffCtx.fillStyle = '#dc3545';
                formatEffCtx.textAlign = 'center';
                formatEffCtx.fillText('Error rendering format effectiveness chart', formatEffCtx.canvas.width/2, formatEffCtx.canvas.height/2);
            }}
        }}
        """
    
    
    def _build_dashboard_controls(self) -> str:
        """Build interactive dashboard controls section."""
        return """
        <div class="dashboard-controls">
            <div class="controls-header">
                <h3>Dashboard Controls</h3>
                <div>
                    <button class="btn-toggle" onclick="toggleFilters()">Filters</button>
                    <button class="btn-toggle" onclick="resetFilters()">Reset</button>
                    <button class="btn-toggle" onclick="exportData()">Export</button>
                </div>
            </div>
            
            <div id="filtersPanel" class="filters-panel">
                <div class="filter-grid">
                    <div class="filter-group">
                        <label>Score Range</label>
                        <div class="range-slider">
                            <input type="range" id="minScore" min="-200" max="200" value="-200" 
                                   oninput="updateScoreRange()">
                            <input type="range" id="maxScore" min="-200" max="200" value="200" 
                                   oninput="updateScoreRange()">
                            <div class="range-display">
                                <span id="minScoreDisplay">-200</span> to 
                                <span id="maxScoreDisplay">200</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="filter-group">
                        <label>Quality Profiles</label>
                        <div id="profileFilters" class="checkbox-group">
                            <!-- Dynamically populated -->
                        </div>
                    </div>
                    
                    <div class="filter-group">
                        <label>Priority Level</label>
                        <div id="priorityFilters" class="checkbox-group">
                            <label><input type="checkbox" name="priority" value="1" checked> Critical</label>
                            <label><input type="checkbox" name="priority" value="2" checked> High</label>
                            <label><input type="checkbox" name="priority" value="3" checked> Medium</label>
                            <label><input type="checkbox" name="priority" value="4" checked> Low</label>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_dashboard_data(self, health_report: LibraryHealthReport, 
                               library_stats: LibraryStats) -> str:
        """Generate JSON data structure for dashboard interactivity."""
        data = {
            'files': [
                {
                    'title': candidate.media_file.display_name,
                    'score': candidate.media_file.total_score,
                    'priority': candidate.priority,
                    'quality_profile': candidate.media_file.quality_profile_name,
                    'potential_gain': candidate.potential_score_gain,
                    'reason': candidate.reason,
                    'recommendation': candidate.recommendation
                }
                for candidate in health_report.upgrade_candidates
            ],
            'quality_profiles': list(library_stats.quality_profiles.keys()),
            'score_ranges': {
                'min': min([c.media_file.total_score for c in health_report.upgrade_candidates] + [0]),
                'max': max([c.media_file.total_score for c in health_report.upgrade_candidates] + [0])
            }
        }
        return json.dumps(data, indent=2)
    
    def _generate_datatables_js(self) -> str:
        """Generate JavaScript for DataTables initialization."""
        return """
        // Initialize DataTables
        $(document).ready(function() {
            // Upgrade Candidates Table with enhanced pagination
            $('#upgradeTable').DataTable({
                "pageLength": 10,  // Default page size for better readability
                "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],  // More pagination options
                "order": [[ 1, "asc" ], [ 2, "asc" ]], // Sort by priority, then score
                "columnDefs": [
                    { "orderable": false, "targets": [6, 7] }, // Disable sort on reason/recommendation (adjusted for new columns)
                    { "searchable": true, "targets": "_all" },
                    { "type": "num", "targets": [2, 3] }, // Ensure numeric sorting for scores
                    { "width": "15%", "targets": 0 }, // Title column width
                    { "width": "8%", "targets": [1, 2, 3, 4, 5] }, // Compact columns
                    { "width": "20%", "targets": 6 }, // Reason column
                    { "width": "15%", "targets": 7 }  // Recommendation column
                ],
                "dom": 'Blfrtip',  // Add length menu to DOM
                "buttons": [
                    {
                        extend: 'copy',
                        text: 'Copy'
                    },
                    {
                        extend: 'csv',
                        text: 'CSV'
                    },
                    {
                        extend: 'excel',
                        text: 'Excel'
                    }
                ],
                "responsive": true,
                "language": {
                    "search": "Search upgrade candidates:",
                    "lengthMenu": "Show _MENU_ candidates per page",
                    "info": "Showing _START_ to _END_ of _TOTAL_ upgrade candidates",
                    "infoFiltered": "(filtered from _MAX_ total candidates)"
                }
            });
            
            // Quality Profile Table
            $('#profileTable').DataTable({
                "pageLength": 10,
                "order": [[ 2, "desc" ]], // Sort by avg score
                "dom": 'Bfrtip',
                "buttons": [
                    {
                        extend: 'copy',
                        text: 'Copy'
                    },
                    {
                        extend: 'csv',
                        text: 'CSV'
                    }
                ],
                "responsive": true,
                "language": {
                    "search": "Search quality profiles:",
                    "lengthMenu": "Show _MENU_ profiles per page"
                }
            });
            
            // Format Effectiveness Table
            $('#formatTable').DataTable({
                "pageLength": 15,
                "order": [[ 2, "desc" ]], // Sort by score impact
                "dom": 'Bfrtip',
                "buttons": [
                    {
                        extend: 'copy',
                        text: 'Copy'
                    },
                    {
                        extend: 'csv',
                        text: 'CSV'
                    }
                ],
                "responsive": true,
                "language": {
                    "search": "Search custom formats:",
                    "lengthMenu": "Show _MENU_ formats per page"
                }
            });
            
            // Setup filter persistence and load saved filters
            setupFilterPersistence();
            
            // Load saved filters after a short delay to ensure DOM is ready
            setTimeout(function() {
                loadSavedFilters();
            }, 100);
        });
        """
    
    def _create_score_filesize_scatter(self, health_report: LibraryHealthReport, library_stats: LibraryStats) -> str:
        """Create JavaScript for score vs file size scatter plot."""
        # Generate scatter plot data from all files with size data
        scatter_data = []
        
        try:
            # First try to get files from database if available
            if self.db_manager:
                files_with_size = self.db_manager.get_files_with_size_data(
                    service_type=health_report.service_type, 
                    limit=100  # Limit for performance
                )
                
                for media_file in files_with_size:
                    try:
                        size_bytes = media_file.size_bytes
                        total_score = media_file.total_score
                        display_name = media_file.display_name
                        
                        if size_bytes and isinstance(size_bytes, (int, float)) and size_bytes > 0:
                            size_gb = size_bytes / (1024**3)
                            score = total_score if isinstance(total_score, (int, float)) else 0
                            
                            # Validate data ranges (expanded for TRaSH Guides scores)
                            if 0 < size_gb < 1000 and -1000 <= score <= 10000:  # Reasonable bounds for TRaSH scores
                                title = str(display_name)[:30] + '...' if len(str(display_name)) > 30 else str(display_name)
                                scatter_data.append({
                                    'x': round(size_gb, 2),
                                    'y': score,
                                    'title': title
                                })
                    except (AttributeError, TypeError, ValueError, ZeroDivisionError):
                        continue
            
            # Fallback: use upgrade candidates as before if no database access
            if not scatter_data:
                upgrade_candidates = getattr(health_report, 'upgrade_candidates', []) or []
                for candidate in upgrade_candidates[:50]:  # Limit for performance
                    try:
                        media_file = getattr(candidate, 'media_file', None)
                        if not media_file:
                            continue
                            
                        size_bytes = getattr(media_file, 'size_bytes', None)
                        total_score = getattr(media_file, 'total_score', None)
                        display_name = getattr(media_file, 'display_name', 'Unknown File')
                        
                        if size_bytes and isinstance(size_bytes, (int, float)) and size_bytes > 0:
                            size_gb = size_bytes / (1024**3)
                            score = total_score if isinstance(total_score, (int, float)) else 0
                            
                            # Validate data ranges (expanded for TRaSH Guides scores)
                            if 0 < size_gb < 1000 and -1000 <= score <= 10000:  # Reasonable bounds for TRaSH scores
                                title = str(display_name)[:30] + '...' if len(str(display_name)) > 30 else str(display_name)
                                scatter_data.append({
                                    'x': round(size_gb, 2),
                                    'y': score,
                                    'title': title
                                })
                    except (AttributeError, TypeError, ValueError, ZeroDivisionError):
                        continue
                        
        except (AttributeError, TypeError):
            pass
        
        # If no real size data available, show a message instead of synthetic data
        if not scatter_data:
            return """
            const scatterCtx = document.getElementById('scoreFileSizeScatter').getContext('2d');
            if (scatterCtx) {
                scatterCtx.font = '16px Arial';
                scatterCtx.fillStyle = '#666';
                scatterCtx.textAlign = 'center';
                scatterCtx.fillText('No file size data available', scatterCtx.canvas.width/2, scatterCtx.canvas.height/2 - 10);
                scatterCtx.fillText('Files may not have size information from', scatterCtx.canvas.width/2, scatterCtx.canvas.height/2 + 15);
                scatterCtx.fillText('the Radarr/Sonarr API', scatterCtx.canvas.width/2, scatterCtx.canvas.height/2 + 40);
            }
            """
        
        return f"""
        try {{
            const scatterCtx = document.getElementById('scoreFileSizeScatter').getContext('2d');
            if (!scatterCtx) {{
                console.warn('Score vs file size scatter chart canvas not found');
            }} else {{
            
            const chartData = {json.dumps(scatter_data)};
            
            new Chart(scatterCtx, {{
                type: 'scatter',
                data: {{
                    datasets: [{{
                        label: 'Files',
                        data: chartData,
                        backgroundColor: function(ctx) {{
                            try {{
                                const value = ctx.parsed ? ctx.parsed.y : 0;
                                if (value > 50) return 'rgba(40, 167, 69, 0.6)';
                                if (value > 0) return 'rgba(23, 162, 184, 0.6)';
                                if (value > -50) return 'rgba(255, 193, 7, 0.6)';
                                return 'rgba(220, 53, 69, 0.6)';
                            }} catch (e) {{
                                return 'rgba(128, 128, 128, 0.6)';
                            }}
                        }},
                        borderColor: function(ctx) {{
                            try {{
                                const value = ctx.parsed ? ctx.parsed.y : 0;
                                if (value > 50) return 'rgba(40, 167, 69, 1)';
                                if (value > 0) return 'rgba(23, 162, 184, 1)';
                                if (value > -50) return 'rgba(255, 193, 7, 1)';
                                return 'rgba(220, 53, 69, 1)';
                            }} catch (e) {{
                                return 'rgba(128, 128, 128, 1)';
                            }}
                        }},
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: 'File Size (GB)'
                            }},
                            beginAtZero: true
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: 'TRaSH Score'
                            }}
                        }}
                    }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                title: function(context) {{
                                    try {{
                                        return context[0] && context[0].raw ? context[0].raw.title : 'Unknown File';
                                    }} catch (e) {{
                                        return 'File';
                                    }}
                                }},
                                label: function(context) {{
                                    try {{
                                        const x = context.parsed ? context.parsed.x : 0;
                                        const y = context.parsed ? context.parsed.y : 0;
                                        return `Score: ${{y}}, Size: ${{x.toFixed(1)}} GB`;
                                    }} catch (e) {{
                                        return 'Data unavailable';
                                    }}
                                }}
                            }}
                        }},
                        legend: {{
                            display: false
                        }}
                    }}
                }}
            }});
            }}
        }} catch (error) {{
            console.error('Error rendering score vs file size scatter chart:', error);
            const scatterCtx = document.getElementById('scoreFileSizeScatter').getContext('2d');
            if (scatterCtx) {{
                scatterCtx.font = '16px Arial';
                scatterCtx.fillStyle = '#dc3545';
                scatterCtx.textAlign = 'center';
                scatterCtx.fillText('Error rendering scatter chart', scatterCtx.canvas.width/2, scatterCtx.canvas.height/2);
            }}
        }}
        """
    
    
    
    def _generate_dashboard_js(self) -> str:
        """Generate JavaScript for dashboard interactivity and filtering."""
        return """        // Modal functionality for category cards
        function showCategoryModal(cardElement) {
            try {
                const categoryType = cardElement.getAttribute('data-category');
                const filesData = cardElement.getAttribute('data-files');
                
                if (!filesData) {
                    console.error('No file data found for category:', categoryType);
                    alert('No file data available for this category.');
                    return;
                }
                
                // Parse the properly escaped JSON
                const files = JSON.parse(filesData);
                
                const modal = document.createElement('div');
                modal.className = 'modal-overlay';
                modal.onclick = (e) => {
                    if (e.target === modal) closeModal();
                };
                
                const fileListHTML = files.map(file => `
                    <div class="file-item">
                        <strong>${file.title}</strong>
                        <p><strong>Score:</strong> ${file.score}</p>
                        <p><strong>Reason:</strong> ${file.reason}</p>
                        <p><strong>Recommendation:</strong> ${file.recommendation}</p>
                    </div>
                `).join('');
                
                modal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>${categoryType} Files (${files.length})</h3>
                            <button class="modal-close" onclick="closeModal()">&times;</button>
                        </div>
                        <div class="file-list">
                            ${fileListHTML}
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                
                // Trigger animation
                setTimeout(() => {
                    modal.classList.add('active');
                }, 10);
            } catch (error) {
                console.error('Error showing category modal:', error);
                alert('Error displaying category details. Please check the console for more information.');
            }
        }
        
        function closeModal() {
            const modal = document.querySelector('.modal-overlay');
            if (modal) {
                modal.classList.remove('active');
                setTimeout(() => {
                    if (modal.parentNode) {
                        modal.parentNode.removeChild(modal);
                    }
                }, 300);
            }
        }
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
        });

        // Advanced sections toggle functionality
        function toggleAdvanced() {
            const sections = document.getElementById('advancedSections');
            const toggle = document.getElementById('advancedToggle');
            
            if (sections.classList.contains('collapsed')) {
                sections.classList.remove('collapsed');
                toggle.textContent = 'Hide Advanced Analysis';
                toggle.classList.add('active');
            } else {
                sections.classList.add('collapsed');
                toggle.textContent = 'Show Advanced Analysis';
                toggle.classList.remove('active');
            }
        }

        // Dashboard Controls
        function toggleFilters() {
            const panel = document.getElementById('filtersPanel');
            panel.classList.toggle('active');
            
            // Populate profile filters if not already done
            if (panel.classList.contains('active') && !panel.hasAttribute('data-populated')) {
                populateProfileFilters();
                panel.setAttribute('data-populated', 'true');
            }
        }
        
        function populateProfileFilters() {
            const container = document.getElementById('profileFilters');
            const profiles = window.dashboardData.quality_profiles;
            
            container.innerHTML = profiles.map(profile => 
                `<label><input type="checkbox" name="profile" value="${profile}" checked> ${profile}</label>`
            ).join('');
        }
        
        function updateScoreRange() {
            const minScore = document.getElementById('minScore').value;
            const maxScore = document.getElementById('maxScore').value;
            
            document.getElementById('minScoreDisplay').textContent = minScore;
            document.getElementById('maxScoreDisplay').textContent = maxScore;
            
            // Apply filter to DataTables
            applyFilters();
        }
        
        function applyFilters() {
            const minScore = parseInt(document.getElementById('minScore').value);
            const maxScore = parseInt(document.getElementById('maxScore').value);
            const selectedProfiles = Array.from(document.querySelectorAll('input[name="profile"]:checked')).map(cb => cb.value);
            const selectedPriorities = Array.from(document.querySelectorAll('input[name="priority"]:checked')).map(cb => cb.value);
            
            // Clear previous custom search functions
            $.fn.dataTable.ext.search = $.fn.dataTable.ext.search.filter(fn => !fn.isCustomFilter);
            
            // Apply custom search to upgrade table
            const upgradeTable = $('#upgradeTable').DataTable();
            const profileTable = $('#profileTable').DataTable();
            const formatTable = $('#formatTable').DataTable();
            
            // Custom filtering function for upgrade candidates
            const upgradeFilter = function(settings, data, dataIndex) {
                if (settings.nTable.id !== 'upgradeTable') return true;
                
                const score = parseInt(data[2]) || 0;
                const priority = data[1].toLowerCase();
                
                // Score range check
                if (score < minScore || score > maxScore) return false;
                
                // Priority check
                const priorityMap = {'critical': '1', 'high': '2', 'medium': '3', 'low': '4'};
                const priorityValue = priorityMap[priority];
                if (priorityValue && !selectedPriorities.includes(priorityValue)) return false;
                
                // Get file data for profile matching (adjust for new table structure with file size and resolution columns)
                const fileData = window.dashboardData.files.find(f => 
                    f.title === data[0] && f.score === score
                );
                if (fileData && fileData.quality_profile) {
                    if (selectedProfiles.length > 0 && !selectedProfiles.includes(fileData.quality_profile)) {
                        return false;
                    }
                }
                
                return true;
            };
            upgradeFilter.isCustomFilter = true;
            
            // Custom filtering for quality profiles
            const profileFilter = function(settings, data, dataIndex) {
                if (settings.nTable.id !== 'profileTable') return true;
                
                const profileName = data[0];
                if (selectedProfiles.length > 0 && !selectedProfiles.includes(profileName)) {
                    return false;
                }
                
                return true;
            };
            profileFilter.isCustomFilter = true;
            
            // Add filters
            $.fn.dataTable.ext.search.push(upgradeFilter);
            $.fn.dataTable.ext.search.push(profileFilter);
            
            // Redraw all tables
            upgradeTable.draw();
            profileTable.draw();
            
            // Update summary statistics
            updateFilteredSummary();
        }
        
        function updateFilteredSummary() {
            const upgradeTable = $('#upgradeTable').DataTable();
            const visibleRows = upgradeTable.rows({search: 'applied'}).data().length;
            const totalRows = upgradeTable.rows().data().length;
            
            // Update summary display if element exists
            const summaryElement = document.querySelector('.filter-summary');
            if (summaryElement) {
                summaryElement.textContent = `Showing ${visibleRows} of ${totalRows} upgrade candidates`;
            } else {
                // Create summary element if it doesn't exist
                const controlsHeader = document.querySelector('.controls-header');
                if (controlsHeader) {
                    const summary = document.createElement('div');
                    summary.className = 'filter-summary';
                    summary.textContent = `Showing ${visibleRows} of ${totalRows} upgrade candidates`;
                    controlsHeader.appendChild(summary);
                }
            }
        }
        
        function resetFilters() {
            document.getElementById('minScore').value = -200;
            document.getElementById('maxScore').value = 200;
            updateScoreRange();
            
            // Reset checkboxes
            document.querySelectorAll('input[name="profile"]').forEach(cb => cb.checked = true);
            document.querySelectorAll('input[name="priority"]').forEach(cb => cb.checked = true);
            
            // Clear all custom DataTables search functions
            $.fn.dataTable.ext.search = $.fn.dataTable.ext.search.filter(fn => !fn.isCustomFilter);
            
            // Redraw all tables
            $('#upgradeTable').DataTable().draw();
            $('#profileTable').DataTable().draw();
            $('#formatTable').DataTable().draw();
            
            // Update summary
            updateFilteredSummary();
            
            // Clear saved filters
            clearSavedFilters();
        }
        
        function saveFilters() {
            const filters = {
                minScore: document.getElementById('minScore').value,
                maxScore: document.getElementById('maxScore').value,
                profiles: Array.from(document.querySelectorAll('input[name="profile"]:checked')).map(cb => cb.value),
                priorities: Array.from(document.querySelectorAll('input[name="priority"]:checked')).map(cb => cb.value)
            };
            localStorage.setItem('arr-dashboard-filters', JSON.stringify(filters));
        }
        
        function loadSavedFilters() {
            const saved = localStorage.getItem('arr-dashboard-filters');
            if (saved) {
                try {
                    const filters = JSON.parse(saved);
                    
                    document.getElementById('minScore').value = filters.minScore || -200;
                    document.getElementById('maxScore').value = filters.maxScore || 200;
                    updateScoreRange();
                    
                    // Restore profile filters
                    document.querySelectorAll('input[name="profile"]').forEach(cb => {
                        cb.checked = filters.profiles ? filters.profiles.includes(cb.value) : true;
                    });
                    
                    // Restore priority filters
                    document.querySelectorAll('input[name="priority"]').forEach(cb => {
                        cb.checked = filters.priorities ? filters.priorities.includes(cb.value) : true;
                    });
                    
                    applyFilters();
                } catch (e) {
                    console.warn('Failed to load saved filters:', e);
                }
            }
        }
        
        function clearSavedFilters() {
            localStorage.removeItem('arr-dashboard-filters');
        }
        
        // Auto-save filters when they change
        function setupFilterPersistence() {
            document.getElementById('minScore').addEventListener('change', saveFilters);
            document.getElementById('maxScore').addEventListener('change', saveFilters);
            
            // Use event delegation for dynamically created checkboxes
            document.addEventListener('change', function(e) {
                if (e.target.matches('input[name="profile"], input[name="priority"]')) {
                    saveFilters();
                }
            });
        }
        
        function exportData() {
            // Trigger CSV export for the currently visible data
            $('#upgradeTable').DataTable().button('.buttons-csv').trigger();
        }
        """