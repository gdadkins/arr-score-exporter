"""
HTML section builders for report generation.

This module contains methods for building various HTML sections,
extracted from html_reporter.py for better modularity.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from ..analysis import LibraryHealthReport, UpgradeCandidate
from ..models import DatabaseManager


class HTMLSectionBuilder:
    """Build individual HTML sections for the report."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize section builder with optional database manager."""
        self.db_manager = db_manager
    
    @staticmethod
    def build_achievements_section(health_report: LibraryHealthReport) -> str:
        """Build achievements section."""
        if not health_report.achievements:
            return ""
        
        return f"""
        <div class="status-card">
            <div class="status-header achievements">
                <span class="status-icon">🏆</span>
                <h3>Achievements</h3>
            </div>
            <div class="status-content">
                <ul class="achievement-list">
                    {HTMLSectionBuilder._build_status_list(health_report.achievements, "Working towards achievements...")}
                </ul>
            </div>
        </div>
        """
    
    @staticmethod
    def _build_status_list(items: List[str], empty_message: str) -> str:
        """Build HTML list from items."""
        if not items:
            return f'<li class="empty-message">{empty_message}</li>'
        return '\n'.join(f'<li>{item}</li>' for item in items)
    
    @staticmethod
    def build_upgrade_candidates_section(health_report: LibraryHealthReport) -> str:
        """Build upgrade candidates table section."""
        if not health_report.upgrade_candidates:
            return """
            <div class="section">
                <h2>Upgrade Opportunities</h2>
                <p class="empty-message">No upgrade candidates identified. Your library is well-optimized!</p>
            </div>
            """
        
        # Generate rows for ALL candidates, JavaScript will handle display limit
        rows = []
        for candidate in health_report.upgrade_candidates:
            current_formats = ', '.join([cf.name for cf in candidate.media_file.custom_formats]) if candidate.media_file.custom_formats else 'None'
            
            # Escape HTML in title
            import html
            escaped_title = html.escape(candidate.media_file.title)
            
            # Map priority number to text
            priority_text = {1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low'}.get(candidate.priority, 'Low')
            priority_class = priority_text.lower()
            
            # Create recommendation text
            recommendation_text = candidate.recommendation if candidate.recommendation else 'Consider upgrading to higher quality release'
            
            rows.append(f"""
                <tr>
                    <td>{escaped_title}</td>
                    <td class="score-cell {'negative' if candidate.media_file.total_score < 0 else 'positive'}">{candidate.media_file.total_score}</td>
                    <td>{current_formats}</td>
                    <td>{html.escape(candidate.reason)}</td>
                    <td>{html.escape(recommendation_text)}</td>
                    <td class="priority-{priority_class}">{priority_text}</td>
                </tr>
            """)
        
        return f"""
        <div class="section">
            <h2>Upgrade Opportunities</h2>
            <div class="upgrade-controls">
                <label for="upgradeLimit">Show:</label>
                <select id="upgradeLimit" class="limit-select" onchange="updateUpgradeTable()">
                    <option value="10" selected>10 items</option>
                    <option value="20">20 items</option>
                    <option value="50">50 items</option>
                    <option value="100">100 items</option>
                    <option value="all">All {len(health_report.upgrade_candidates)} items</option>
                </select>
            </div>
            <div class="table-responsive">
                <table class="upgrade-table data-table" id="upgradeTable">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Current Score</th>
                            <th>Current Formats</th>
                            <th>Reason</th>
                            <th>Recommendation</th>
                            <th>Priority</th>
                        </tr>
                    </thead>
                    <tbody id="upgradeTableBody">
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    @staticmethod
    def build_quality_profile_analysis_section(health_report: LibraryHealthReport) -> str:
        """Build quality profile analysis section."""
        if not hasattr(health_report, 'quality_profile_analysis') or not health_report.quality_profile_analysis:
            return ""
        
        rows = []
        for profile_analysis in health_report.quality_profile_analysis:
            import html
            escaped_profile = html.escape(profile_analysis.profile_name)
            
            # Create score distribution text
            score_dist_items = []
            for range_name, count in profile_analysis.score_distribution.items():
                if count > 0:
                    score_dist_items.append(f"{range_name}: {count}")
            score_dist_text = ", ".join(score_dist_items[:3]) if score_dist_items else "N/A"
            
            rows.append(f"""
                <tr>
                    <td>{escaped_profile}</td>
                    <td>{profile_analysis.file_count:,}</td>
                    <td class="{'positive' if profile_analysis.avg_score > 0 else 'negative'}">{profile_analysis.avg_score:.1f}</td>
                    <td>{score_dist_text}</td>
                    <td class="effectiveness-{profile_analysis.effectiveness_rating}">{profile_analysis.effectiveness_rating.title()}</td>
                </tr>
            """)
        
        return f"""
        <div class="section">
            <h2>Quality Profile Analysis</h2>
            <div class="table-responsive">
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>Quality Profile</th>
                            <th>Files</th>
                            <th>Avg Score</th>
                            <th>Score Distribution</th>
                            <th>Effectiveness</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    @staticmethod
    def build_format_analysis_section(health_report: LibraryHealthReport) -> str:
        """Build custom format analysis section."""
        if not health_report.format_effectiveness:
            return ""
        
        # Convert format_effectiveness list to dict format
        format_data = {}
        for fmt_eff in health_report.format_effectiveness:
            format_data[fmt_eff.format_name] = {
                'count': fmt_eff.usage_count,
                'avg_score': fmt_eff.avg_score_contribution,
                'total_size_gb': 0  # We don't have this data in the new structure
            }
        
        # Sort formats by file count
        sorted_formats = sorted(
            format_data.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:15]  # Top 15 formats
        
        rows = []
        for fmt, stats in sorted_formats:
            import html
            escaped_format = html.escape(fmt)
            rows.append(f"""
                <tr>
                    <td>{escaped_format}</td>
                    <td>{stats['count']:,}</td>
                    <td class="{'positive' if stats['avg_score'] > 0 else 'negative'}">{stats['avg_score']:.1f}</td>
                    <td>{stats.get('total_size_gb', 0):.1f} GB</td>
                </tr>
            """)
        
        return f"""
        <div class="section">
            <h2>Custom Format Analysis</h2>
            <div class="table-responsive">
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>Format</th>
                            <th>File Count</th>
                            <th>Avg Score</th>
                            <th>Total Size</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    @staticmethod
    def build_recommendations_section(health_report: LibraryHealthReport) -> str:
        """Build recommendations section."""
        if not health_report.recommendations:
            return ""
        
        recommendations_html = HTMLSectionBuilder._build_status_list(
            health_report.recommendations,
            "Analysis complete. No specific recommendations at this time."
        )
        
        return f"""
        <div class="section">
            <h2>Recommendations</h2>
            <ul class="recommendations-list">
                {recommendations_html}
            </ul>
        </div>
        """
    
    @staticmethod
    def build_intelligent_categories_section(health_report: LibraryHealthReport) -> str:
        """Build intelligent file categories section with modal functionality."""
        import json
        
        if not hasattr(health_report, 'intelligent_categories') or not health_report.intelligent_categories:
            return ""
        
        categories_mapping = [
            ('premium_quality', '🏆 Premium Quality', 'Files with exceptional quality scores', 'premium'),
            ('upgrade_worthy', '📈 Upgrade Worthy', 'Files that would benefit from quality improvements', 'upgrade'), 
            ('priority_replacements', '⚠️ Priority Replacements', 'Files with quality issues that need immediate attention', 'warning'),
            ('large_low_quality', '💾 Large Low Quality', 'Large files with poor quality scores', 'warning'),
            ('hdr_candidates', '🎬 HDR Candidates', '4K files missing HDR formats', 'info'),
            ('audio_upgrade_candidates', '🔊 Audio Upgrades', 'Files with poor audio formats', 'info'),
            ('legacy_content', '📼 Legacy Content', 'Files with outdated formats', 'info')
        ]
        
        sections = []
        for category_key, title, desc, css_class in categories_mapping:
            files = health_report.intelligent_categories.get(category_key, [])
            if not files:
                continue
            
            # Prepare files data for modal
            files_data = []
            for media_file in files[:100]:  # Limit to 100 files per category
                import html
                file_info = {
                    'title': html.escape(media_file.title),
                    'score': media_file.total_score,
                    'size': (media_file.size_bytes / (1024 * 1024)) if media_file.size_bytes else 0,
                    'formats': html.escape(', '.join([cf.name for cf in media_file.custom_formats]) if media_file.custom_formats else 'None')
                }
                files_data.append(file_info)
            
            sections.append(f"""
                <div class="category-card {css_class}" onclick="showCategoryModal('{category_key}', {html.escape(json.dumps(files_data))})">
                    <div class="category-header">
                        <span class="category-icon">{title.split()[0]}</span>
                        <h3>{' '.join(title.split()[1:])}</h3>
                    </div>
                    <div class="category-stats">
                        <div class="stat-value">{len(files):,}</div>
                        <div class="stat-label">Files</div>
                    </div>
                    <p class="category-desc">{desc}</p>
                    <div class="view-details">Click to view details →</div>
                </div>
            """)
        
        if not sections:
            return ""
        
        return f"""
        <div class="section">
            <h2>Intelligent File Categories</h2>
            <div class="categories-grid">
                {''.join(sections)}
            </div>
            
            <!-- Category Modal -->
            <div id="categoryModal" class="modal">
                <div class="modal-content">
                    <span class="close" onclick="closeCategoryModal()">&times;</span>
                    <h2 id="modalTitle"></h2>
                    <div id="modalContent"></div>
                </div>
            </div>
            
            <div class="analysis-criteria">
                <h3>Analysis Criteria</h3>
                <div class="criteria-grid">
                    <div class="criteria-item">
                        <strong>Premium Quality:</strong> TRaSH score &gt;= 100 (exceptional releases)
                    </div>
                    <div class="criteria-item">
                        <strong>Low Score Threshold:</strong> Files with TRaSH score &lt;= {getattr(health_report, 'min_score_threshold', -50)}
                    </div>
                    <div class="criteria-item">
                        <strong>Below Library Average:</strong> Files scoring significantly below your library's average
                    </div>
                    <div class="criteria-item">
                        <strong>Size Anomalies:</strong> Files unusually large or small for their quality score
                    </div>
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def build_historical_trends_section(health_report: LibraryHealthReport) -> str:
        """Build historical trends section if available."""
        if not hasattr(health_report, 'historical_analysis') or not health_report.historical_analysis:
            return ""
        
        trends = health_report.historical_analysis
        
        # Build trend cards
        trend_cards = []
        
        # Show improvement/degradation velocity
        if 'improvement_velocity' in trends and 'degradation_velocity' in trends:
            net_velocity = trends.get('net_velocity', 0)
            trend_class = 'positive' if net_velocity > 0 else 'negative' if net_velocity < 0 else 'neutral'
            trend_cards.append(f"""
                <div class="trend-card {trend_class}">
                    <h4>Weekly Change Rate</h4>
                    <div class="trend-value">{net_velocity:+.1f}</div>
                    <div class="trend-period">Files/week (net)</div>
                </div>
            """)
            
            trend_cards.append(f"""
                <div class="trend-card positive">
                    <h4>Improvements</h4>
                    <div class="trend-value">{trends.get('improvement_velocity', 0):.1f}</div>
                    <div class="trend-period">Files/week</div>
                </div>
            """)
            
            trend_cards.append(f"""
                <div class="trend-card negative">
                    <h4>Degradations</h4>
                    <div class="trend-value">{trends.get('degradation_velocity', 0):.1f}</div>
                    <div class="trend-period">Files/week</div>
                </div>
            """)
        
        # Build patterns list
        patterns = trends.get('patterns', [])
        patterns_html = HTMLSectionBuilder._build_status_list(
            patterns[:5],  # Show top 5 patterns
            "No significant patterns detected yet."
        )
        
        # Build recommendations
        recommendations = trends.get('recommendations', [])
        recommendations_html = HTMLSectionBuilder._build_status_list(
            recommendations[:5],  # Show top 5 recommendations
            "Continue monitoring for trend-based insights."
        )
        
        return f"""
        <div class="section">
            <h2>Historical Trends</h2>
            
            <div class="trend-cards">
                {''.join(trend_cards)}
            </div>
            
            <div class="trend-analysis">
                <div class="trend-patterns">
                    <h3>Detected Patterns</h3>
                    <ul class="pattern-list">
                        {patterns_html}
                    </ul>
                </div>
                
                <div class="trend-recommendations">
                    <h3>Trend-Based Recommendations</h3>
                    <ul class="trend-rec-list">
                        {recommendations_html}
                    </ul>
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def build_dashboard_controls() -> str:
        """Build dashboard filter controls."""
        return """
        <div class="dashboard-controls">
            <div class="control-group">
                <label for="scoreFilter">Score Range:</label>
                <select id="scoreFilter" class="filter-select">
                    <option value="all">All Scores</option>
                    <option value="premium">Premium (&gt;=100)</option>
                    <option value="good">Good (0-99)</option>
                    <option value="poor">Poor (< 0)</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="formatFilter">Format:</label>
                <input type="text" id="formatFilter" class="filter-input" placeholder="Filter by format...">
            </div>
            
            <div class="control-group">
                <label for="sizeFilter">Size Range:</label>
                <select id="sizeFilter" class="filter-select">
                    <option value="all">All Sizes</option>
                    <option value="small">< 1 GB</option>
                    <option value="medium">1-5 GB</option>
                    <option value="large">5-10 GB</option>
                    <option value="xlarge">> 10 GB</option>
                </select>
            </div>
            
            <button class="btn-reset" onclick="resetFilters()">Reset Filters</button>
        </div>
        """
    

    def build_zero_scores_table_section(self, health_report: LibraryHealthReport, library_stats) -> str:
        """Build clickable zero scores table section that appears below charts."""
        # Get zero score files from database if available
        zero_score_files = []
        if self.db_manager:
            zero_score_files = self.db_manager.get_zero_score_files(
                service_type=library_stats.service_type,
                limit=100  # Limit for performance
            )
        
        if not zero_score_files:
            return ""
        
        # Create table rows for individual files
        rows = []
        for media_file in zero_score_files:
            import html
            escaped_title = html.escape(media_file.title)
            
            # Get file formats
            formats = ', '.join([cf.name for cf in media_file.custom_formats]) if media_file.custom_formats else 'No formats'
            escaped_formats = html.escape(formats)
            
            # Get file size in GB
            size_gb = (media_file.size_bytes / (1024**3)) if media_file.size_bytes else 0
            size_display = f"{size_gb:.2f} GB" if size_gb > 0 else "N/A"
            
            # Get quality profile if available
            quality = html.escape(getattr(media_file, 'quality_profile', 'N/A'))
            
            rows.append(f"""
                <tr>
                    <td>{escaped_title}</td>
                    <td class="score-cell zero-score">0</td>
                    <td>{escaped_formats}</td>
                    <td>{size_display}</td>
                    <td>{quality}</td>
                </tr>
            """)
        
        return f"""
        <div id="zeroScoresTableSection" class="section" style="display: none;">
            <div class="section-header">
                <h2>Zero Score Files Details</h2>
                <button id="zeroScoresToggleBtn" class="toggle-btn" onclick="toggleZeroScoresTable()">Hide Zero Scores Details</button>
            </div>
            <div class="alert alert-info">
                <strong>Click on the grey "Zero Scores" area in the pie chart above to toggle this table.</strong><br>
                Showing {len(zero_score_files):,} files with zero TRaSH scores. These files don't match any custom format definitions that contribute to scoring.
            </div>
            
            <div class="table-responsive">
                <table class="zero-scores-table data-table">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Score</th>
                            <th>Current Formats</th>
                            <th>File Size</th>
                            <th>Quality Profile</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
            
            <div class="recommendations-box">
                <h4>Why These Files Have Zero Scores:</h4>
                <ul>
                    <li><strong>No Matching Formats:</strong> Files don't match any TRaSH custom format definitions</li>
                    <li><strong>Basic Releases:</strong> Standard releases without premium quality indicators</li>
                    <li><strong>Missing Metadata:</strong> Format information may not be properly parsed</li>
                    <li><strong>Configuration Gap:</strong> Your custom formats may need adjustment to catch these files</li>
                </ul>
                
                <h4>Recommended Actions:</h4>
                <ul>
                    <li>Review TRaSH Guides for additional custom format definitions</li>
                    <li>Check if these files meet your quality standards</li>
                    <li>Consider adding custom formats for common release groups in your collection</li>
                    <li>Verify that your {health_report.service_type.title()} custom format configuration is complete</li>
                </ul>
            </div>
        </div>
        """