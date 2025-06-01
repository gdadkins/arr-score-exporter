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
    
    def _get_format_size_data(self, service_type: str) -> Dict[str, float]:
        """Get total size data for each custom format from database."""
        format_sizes = {}
        if not self.db_manager:
            return format_sizes
        
        try:
            with self.db_manager._get_connection() as conn:
                rows = conn.execute("""
                    SELECT custom_formats_json, size_bytes
                    FROM media_files 
                    WHERE service_type = ? AND custom_formats_json IS NOT NULL AND size_bytes IS NOT NULL
                """, (service_type,)).fetchall()
            
            for row in rows:
                try:
                    import json
                    formats = json.loads(row[0])
                    file_size_gb = row[1] / (1024**3) if row[1] else 0
                    
                    for cf in formats:
                        format_name = cf.get("name", "Unknown")
                        if format_name not in format_sizes:
                            format_sizes[format_name] = 0.0
                        format_sizes[format_name] += file_size_gb
                        
                except (json.JSONDecodeError, TypeError):
                    continue
                    
        except Exception as e:
            # Gracefully handle any database errors
            print(f"Warning: Could not retrieve format size data: {e}")
            
        return format_sizes
    
    def _get_accurate_format_stats(self, service_type: str) -> Dict[str, Dict[str, float]]:
        """Get accurate format statistics with correct file counts and size data."""
        format_stats = {}
        if not self.db_manager:
            return format_stats
        
        try:
            with self.db_manager._get_connection() as conn:
                rows = conn.execute("""
                    SELECT custom_formats_json, total_score, size_bytes, unique_identifier
                    FROM media_files 
                    WHERE service_type = ? AND custom_formats_json IS NOT NULL
                """, (service_type,)).fetchall()
            
            # Track unique files per format to get accurate counts
            format_data = {}
            
            for row in rows:
                try:
                    import json
                    formats = json.loads(row[0])
                    total_score = row[1]
                    file_size_gb = (row[2] / (1024**3)) if row[2] else 0
                    file_id = row[3]
                    
                    for cf in formats:
                        format_name = cf.get("name", "Unknown")
                        
                        if format_name not in format_data:
                            format_data[format_name] = {
                                'unique_files': set(),
                                'total_score_sum': 0,
                                'total_size_gb': 0
                            }
                        
                        # Add this file to the unique set for this format
                        format_data[format_name]['unique_files'].add(file_id)
                        format_data[format_name]['total_score_sum'] += total_score
                        format_data[format_name]['total_size_gb'] += file_size_gb
                        
                except (json.JSONDecodeError, TypeError):
                    continue
            
            # Convert to final format stats
            for format_name, data in format_data.items():
                file_count = len(data['unique_files'])
                if file_count > 0:
                    format_stats[format_name] = {
                        'file_count': file_count,
                        'avg_score': data['total_score_sum'] / file_count,
                        'total_size_gb': data['total_size_gb']
                    }
                    
        except Exception as e:
            # Gracefully handle any database errors
            print(f"Warning: Could not retrieve accurate format statistics: {e}")
            
        return format_stats
    
    @staticmethod
    def _format_size_display(size_gb: float) -> str:
        """Format size for display, converting to TB when appropriate."""
        if size_gb >= 1024:  # Convert to TB when >= 1024 GB
            size_tb = size_gb / 1024
            return f"{size_tb:.1f} TB"
        else:
            return f"{size_gb:.1f} GB"
    
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
    
    def build_format_analysis_section(self, health_report: LibraryHealthReport) -> str:
        """Build custom format analysis section."""
        if not health_report.format_effectiveness:
            return ""
        
        # Get accurate format statistics directly from database
        format_stats = {}
        if self.db_manager:
            format_stats = self._get_accurate_format_stats(health_report.service_type)
        
        # If database query failed, fall back to the health report data
        if not format_stats:
            for fmt_eff in health_report.format_effectiveness:
                format_stats[fmt_eff.format_name] = {
                    'file_count': fmt_eff.files_with_format,
                    'avg_score': fmt_eff.avg_score_contribution,
                    'total_size_gb': 0.0
                }
        
        # Sort formats by file count
        sorted_formats = sorted(
            format_stats.items(),
            key=lambda x: x[1]['file_count'],
            reverse=True
        )[:15]  # Top 15 formats
        
        rows = []
        for fmt, stats in sorted_formats:
            import html
            escaped_format = html.escape(fmt)
            size_display = self._format_size_display(stats.get('total_size_gb', 0))
            rows.append(f"""
                <tr>
                    <td>{escaped_format}</td>
                    <td>{stats['file_count']:,}</td>
                    <td class="{'positive' if stats['avg_score'] > 0 else 'negative'}">{stats['avg_score']:.1f}</td>
                    <td>{size_display}</td>
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
        """Build historical trends section with fallback for new installations."""
        # Check if we have historical analysis data
        has_trends = (hasattr(health_report, 'historical_analysis') and 
                     health_report.historical_analysis and 
                     health_report.historical_analysis.get('total_changes', 0) > 0)
        
        if has_trends:
            trends = health_report.historical_analysis
            
            # Build trend cards with actual data
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
                <div class="data-availability-notice">
                    <span class="availability-status available">✓ {trends.get('total_changes', 0)} score changes tracked</span>
                </div>
                
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
        else:
            # Show placeholder content when no historical data is available yet
            return f"""
            <div class="section">
                <h2>Historical Trends</h2>
                <div class="data-availability-notice">
                    <span class="availability-status pending">⏳ No historical data available yet</span>
                </div>
                
                <div class="historical-placeholder">
                    <div class="placeholder-icon">📈</div>
                    <h3>Building Your Library's History</h3>
                    <p>Historical trends will appear here once you've run exports multiple times over different days. 
                    This section tracks how your library's quality evolves over time.</p>
                    
                    <div class="what-youll-see">
                        <h4>What You'll See Here:</h4>
                        <ul>
                            <li><strong>Score Velocity:</strong> Weekly improvement/degradation rates</li>
                            <li><strong>Library Patterns:</strong> Trends in your collection quality</li>
                            <li><strong>Change Detection:</strong> Which files have been upgraded or downgraded</li>
                            <li><strong>Optimization Insights:</strong> Data-driven recommendations for library health</li>
                        </ul>
                    </div>
                    
                    <div class="how-it-works">
                        <h4>How Historical Tracking Works:</h4>
                        <ul>
                            <li>Each time you run <code>arr-export-enhanced</code>, file scores are recorded</li>
                            <li>When scores change (files upgraded/downgraded), it's tracked in the database</li>
                            <li>After a few weeks of data, patterns and trends emerge</li>
                            <li>The system identifies whether your library is improving or needs attention</li>
                        </ul>
                    </div>
                    
                    <div class="next-steps">
                        <div class="step-card">
                            <h4>📅 Schedule Regular Exports</h4>
                            <p>Run exports weekly to build meaningful trend data</p>
                        </div>
                        
                        <div class="step-card">
                            <h4>🔄 Upgrade Your Files</h4>
                            <p>When you upgrade files, the system will track the improvements</p>
                        </div>
                        
                        <div class="step-card">
                            <h4>📊 Check Back Later</h4>
                            <p>Return in a week to see your first trend data</p>
                        </div>
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