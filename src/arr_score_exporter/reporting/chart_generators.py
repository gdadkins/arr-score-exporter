"""
Chart generation module for HTML reports.

This module contains all chart creation methods extracted from html_reporter.py
to maintain separation of concerns and improve maintainability.
"""

import json
from typing import Dict, Any, List, Optional
from ..analysis import LibraryHealthReport
from ..models import LibraryStats, DatabaseManager


class ChartGenerator:
    """Generate Chart.js configurations for various visualizations."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize chart generator with optional database manager."""
        self.db_manager = db_manager
    
    def create_score_distribution_chart(self, stats: LibraryStats) -> str:
        """Create score distribution pie chart configuration."""
        # Simple categorization: Positive, Zero, Negative scores
        categories = {
            'Positive Scores': stats.files_with_positive_scores,
            'Zero Scores': stats.files_with_zero_scores,
            'Negative Scores': stats.files_with_negative_scores
        }
        
        # For more accurate data, query the database if available
        if self.db_manager:
            with self.db_manager._get_connection() as conn:
                rows = conn.execute("""
                    SELECT 
                        SUM(CASE WHEN total_score > 0 THEN 1 ELSE 0 END) as positive,
                        SUM(CASE WHEN total_score = 0 THEN 1 ELSE 0 END) as zero,
                        SUM(CASE WHEN total_score < 0 THEN 1 ELSE 0 END) as negative
                    FROM media_files
                    WHERE service_type = ?
                """, (stats.service_type,)).fetchone()
                
                if rows:
                    categories['Positive Scores'] = rows[0] or 0
                    categories['Zero Scores'] = rows[1] or 0
                    categories['Negative Scores'] = rows[2] or 0
        
        chart_config = {
            'type': 'pie',
            'data': {
                'labels': list(categories.keys()),
                'datasets': [{
                    'data': list(categories.values()),
                    'backgroundColor': [
                        'rgba(40, 167, 69, 0.8)',   # Green for Positive
                        'rgba(108, 117, 125, 0.8)', # Grey for Zero
                        'rgba(220, 53, 69, 0.8)'    # Red for Negative
                    ],
                    'borderColor': [
                        'rgba(40, 167, 69, 1)',
                        'rgba(108, 117, 125, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Score Distribution',
                        'font': {'size': 16}
                    },
                    'legend': {
                        'display': True,
                        'position': 'bottom'
                    },
                    'tooltip': {
                        'callbacks': {
                            'label': 'function(context) { return context.label + ": " + context.parsed.toLocaleString() + " files"; }'
                        }
                    }
                }
            }
        }
        
        return json.dumps(chart_config, indent=2)
    
    def create_format_effectiveness_chart(self, health_report: LibraryHealthReport) -> str:
        """Create format effectiveness horizontal bar chart configuration."""
        if not health_report.format_effectiveness:
            return "null"
        
        # Convert format_effectiveness list to the expected format
        format_data = {}
        for fmt_eff in health_report.format_effectiveness:
            format_data[fmt_eff.format_name] = {
                'avg_score': fmt_eff.avg_score_contribution,
                'count': fmt_eff.usage_count
            }
        
        # Sort formats by average score
        sorted_formats = sorted(
            format_data.items(),
            key=lambda x: x[1]['avg_score'],
            reverse=True
        )[:10]  # Top 10 formats
        
        labels = []
        avg_scores = []
        file_counts = []
        colors = []
        
        for fmt, data in sorted_formats:
            labels.append(fmt)
            avg_scores.append(round(data['avg_score'], 1))
            file_counts.append(data['count'])
            
            # Color based on score
            if data['avg_score'] >= 50:
                colors.append('rgba(40, 167, 69, 0.8)')
            elif data['avg_score'] >= 0:
                colors.append('rgba(255, 193, 7, 0.8)')
            else:
                colors.append('rgba(220, 53, 69, 0.8)')
        
        chart_config = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Average Score',
                    'data': avg_scores,
                    'backgroundColor': colors,
                    'borderColor': [c.replace('0.8', '1') for c in colors],
                    'borderWidth': 1
                }]
            },
            'options': {
                'indexAxis': 'y',
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Top 10 Formats by Average Score',
                        'font': {'size': 16}
                    },
                    'tooltip': {
                        'callbacks': {}
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Average TRaSH Score'
                        }
                    }
                }
            }
        }
        
        return json.dumps(chart_config, indent=2)
    
