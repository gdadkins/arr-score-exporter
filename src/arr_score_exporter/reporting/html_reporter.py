"""
Rich HTML reporting system for Arr Score Exporter.

Generates beautiful, interactive HTML reports with charts, tables, and insights
to help users understand their library quality and identify optimization opportunities.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import base64
from io import BytesIO

from ..analysis import LibraryHealthReport, UpgradeCandidate
from ..models import LibraryStats


class HTMLReporter:
    """Generates rich HTML reports with charts and interactive elements."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize HTML reporter."""
        if output_dir is None:
            output_dir = Path.cwd() / "reports"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
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
        quality_profile_chart = self._create_quality_profile_chart(library_stats)
        format_effectiveness_chart = self._create_format_effectiveness_chart(health_report)
        trend_chart = self._create_trend_chart(health_report)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{health_report.service_type.title()} Library Health Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        </div>

        {self._build_achievements_warnings_section(health_report)}

        <div class="charts-grid">
            <div class="chart-container">
                <h3>Score Distribution</h3>
                <canvas id="scoreDistChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Quality Profile Performance</h3>
                <canvas id="qualityProfileChart"></canvas>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <h3>Custom Format Effectiveness</h3>
                <canvas id="formatEffectivenessChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Score Trends (30 Days)</h3>
                <canvas id="trendChart"></canvas>
            </div>
        </div>

        {self._build_upgrade_candidates_section(health_report)}
        {self._build_quality_profile_analysis_section(health_report)}
        {self._build_format_analysis_section(health_report)}
        {self._build_recommendations_section(health_report)}

        <footer class="footer">
            <p>Generated by Arr Score Exporter - TRaSH Guides Custom Format Analysis Tool</p>
        </footer>
    </div>

    <script>
        {score_distribution_chart}
        {quality_profile_chart}
        {format_effectiveness_chart}
        {trend_chart}
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }

        .card h3 {
            color: #666;
            margin-bottom: 10px;
            font-size: 1.1em;
        }

        .metric-value {
            font-size: 2.5em;
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
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }

        .chart-container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .chart-container h3 {
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }

        .section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .section h2 {
            color: #333;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .upgrade-table, .profile-table, .format-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
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

        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #ddd;
            margin-top: 30px;
        }

        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .chart-container {
                min-width: auto;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .report-meta {
                flex-direction: column;
                gap: 10px;
            }
        }
        """
    
    def _build_achievements_warnings_section(self, health_report: LibraryHealthReport) -> str:
        """Build achievements and warnings section."""
        return f"""
        <div class="status-section">
            <div class="status-card achievements">
                <h3><span class="status-icon"></span>Achievements</h3>
                <ul class="status-list">
                    {self._build_status_list(health_report.achievements, "No achievements recorded")}
                </ul>
            </div>
            <div class="status-card warnings">
                <h3><span class="status-icon"></span>Warnings</h3>
                <ul class="status-list">
                    {self._build_status_list(health_report.warnings, "No warnings - library is healthy!")}
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
        """Build upgrade candidates section."""
        if not health_report.upgrade_candidates:
            return """
            <div class="section">
                <h2>🎯 Upgrade Candidates</h2>
                <p>No upgrade candidates identified. Your library is in excellent shape!</p>
            </div>
            """
        
        candidates_html = ""
        for candidate in health_report.upgrade_candidates[:10]:  # Top 10
            priority_class = f"priority-{candidate.priority}"
            potential_gain = f"+{candidate.potential_score_gain}" if candidate.potential_score_gain else "N/A"
            
            candidates_html += f"""
                <tr>
                    <td>{candidate.media_file.display_name}</td>
                    <td class="{priority_class}">{'Critical' if candidate.priority == 1 else 'High' if candidate.priority == 2 else 'Medium' if candidate.priority == 3 else 'Low'}</td>
                    <td>{candidate.media_file.total_score}</td>
                    <td>{potential_gain}</td>
                    <td>{candidate.reason}</td>
                    <td>{candidate.recommendation or 'Review manually'}</td>
                </tr>
            """
        
        return f"""
        <div class="section">
            <h2>🎯 Upgrade Candidates (Top 10)</h2>
            <p>Files that would benefit most from upgrades based on TRaSH Guides scoring.</p>
            <table class="upgrade-table">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Priority</th>
                        <th>Current Score</th>
                        <th>Potential Gain</th>
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
            <h2>📊 Quality Profile Analysis</h2>
            <table class="profile-table">
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
            <h2>🏷️ Custom Format Effectiveness (Top 15)</h2>
            <table class="format-table">
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
            <h2>💡 Recommendations</h2>
            <ul class="recommendations-list">
                {recommendations_html}
            </ul>
        </div>
        """
    
    def _create_score_distribution_chart(self, stats: LibraryStats) -> str:
        """Create JavaScript for score distribution chart."""
        return f"""
        const scoreDistCtx = document.getElementById('scoreDistChart').getContext('2d');
        new Chart(scoreDistCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Positive Scores', 'Zero Scores', 'Negative Scores'],
                datasets: [{{
                    data: [{stats.files_with_positive_scores}, {stats.files_with_zero_scores}, {stats.files_with_negative_scores}],
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
        """
    
    def _create_quality_profile_chart(self, stats: LibraryStats) -> str:
        """Create JavaScript for quality profile chart."""
        labels = list(stats.quality_profiles.keys())[:8]  # Top 8 profiles
        data = [stats.quality_profiles[label] for label in labels]
        
        return f"""
        const qualityProfileCtx = document.getElementById('qualityProfileChart').getContext('2d');
        new Chart(qualityProfileCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'File Count',
                    data: {json.dumps(data)},
                    backgroundColor: '#667eea',
                    borderColor: '#5a6fd8',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        """
    
    def _create_format_effectiveness_chart(self, health_report: LibraryHealthReport) -> str:
        """Create JavaScript for format effectiveness chart."""
        formats = health_report.format_effectiveness[:10]  # Top 10
        labels = [f.format_name for f in formats]
        scores = [f.avg_score_contribution for f in formats]
        colors = ['#28a745' if s > 20 else '#17a2b8' if s > 0 else '#dc3545' for s in scores]
        
        return f"""
        const formatEffCtx = document.getElementById('formatEffectivenessChart').getContext('2d');
        new Chart(formatEffCtx, {{
            type: 'horizontalBar',
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
                scales: {{
                    x: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        """
    
    def _create_trend_chart(self, health_report: LibraryHealthReport) -> str:
        """Create JavaScript for trends chart."""
        trends = health_report.score_trends
        
        return f"""
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {{
            type: 'bar',
            data: {{
                labels: ['Improvements', 'Degradations'],
                datasets: [{{
                    label: 'Count',
                    data: [{trends.get('improvements_last_30_days', 0)}, {trends.get('degradations_last_30_days', 0)}],
                    backgroundColor: ['#28a745', '#dc3545']
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        """