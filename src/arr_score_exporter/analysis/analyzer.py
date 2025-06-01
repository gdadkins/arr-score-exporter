"""
Intelligent analysis engine for Arr Score Exporter.

Provides advanced analytics, upgrade candidate identification, trend analysis,
and library optimization recommendations based on TRaSH Guides scoring data.
"""

import statistics
import sqlite3
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from ..models import MediaFile, LibraryStats, DatabaseManager, ScoreChangeType


@dataclass
class UpgradeCandidate:
    """Represents a file that's a candidate for upgrade."""
    media_file: MediaFile
    reason: str
    priority: int  # 1=critical, 2=high, 3=medium, 4=low
    potential_score_gain: Optional[int] = None
    recommendation: Optional[str] = None


@dataclass
class QualityProfileAnalysis:
    """Analysis of a quality profile's performance."""
    profile_name: str
    file_count: int
    avg_score: float
    score_distribution: Dict[str, int]  # range -> count
    common_issues: List[str]
    recommendations: List[str]
    effectiveness_rating: str  # excellent/good/fair/poor


@dataclass
class CustomFormatEffectiveness:
    """Analysis of custom format effectiveness."""
    format_name: str
    usage_count: int
    avg_score_contribution: float
    files_with_format: int
    impact_rating: str  # high/medium/low/negative
    recommendations: List[str]


@dataclass
class LibraryHealthReport:
    """Comprehensive library health analysis."""
    service_type: str
    generated_at: datetime
    
    # Overall health
    health_score: float  # 0-100
    health_grade: str    # A/B/C/D/F
    
    # Key metrics
    total_files: int
    upgrade_candidates: List[UpgradeCandidate]
    quality_profile_analysis: List[QualityProfileAnalysis]
    format_effectiveness: List[CustomFormatEffectiveness]
    
    # Trends and insights
    score_trends: Dict[str, Any]
    recommendations: List[str]
    achievements: List[str]
    warnings: List[str]
    
    # Phase 2: Enhanced Analytics
    historical_analysis: Optional[Dict[str, Any]] = None
    intelligent_categories: Optional[Dict[str, List[MediaFile]]] = None


class IntelligentAnalyzer:
    """Advanced analytics engine for library optimization."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def identify_upgrade_candidates(self, service_type: str, 
                                  min_score_threshold: int = -50) -> List[UpgradeCandidate]:
        """
        Intelligently identify files that are candidates for upgrade.
        
        Uses multiple criteria beyond just low scores to identify the best
        upgrade candidates with highest impact potential.
        """
        candidates = []
        
        # Get files with low scores
        low_score_files = self.db.get_upgrade_candidates(min_score_threshold, service_type)
        
        # Get library stats for context
        stats = self.db.calculate_library_stats(service_type)
        avg_score = stats.avg_score
        
        for file in low_score_files:
            reasons = []
            priority = 4  # default low priority
            potential_gain = None
            recommendation = None
            
            # Analyze score relative to library average
            score_gap = avg_score - file.total_score
            if score_gap > 100:
                reasons.append(f"Score {score_gap:.0f} points below library average")
                priority = min(priority, 1)  # critical
                potential_gain = int(score_gap * 0.7)  # conservative estimate
            elif score_gap > 50:
                reasons.append(f"Score {score_gap:.0f} points below library average")
                priority = min(priority, 2)  # high
                potential_gain = int(score_gap * 0.5)
            elif score_gap > 20:
                reasons.append("Score below library average")
                priority = min(priority, 3)  # medium
            
            # Check for specific problematic formats
            negative_formats = [cf for cf in file.custom_formats if cf.score < 0]
            if negative_formats:
                reasons.append(f"Has {len(negative_formats)} negative-scoring format(s)")
                if any(cf.score < -50 for cf in negative_formats):
                    priority = min(priority, 1)  # critical for very negative formats
                elif any(cf.score < -20 for cf in negative_formats):
                    priority = min(priority, 2)  # high
                    
                # Generate specific recommendation
                worst_format = min(negative_formats, key=lambda cf: cf.score)
                recommendation = f"Replace release to avoid '{worst_format.name}' format (score: {worst_format.score})"
            
            # Check file size efficiency (if available)
            if file.size_bytes and stats.avg_file_size_gb > 0:
                file_size_gb = file.size_bytes / (1024**3)
                if file_size_gb > stats.avg_file_size_gb * 2 and file.total_score < 0:
                    reasons.append("Large file with poor quality score")
                    priority = min(priority, 2)
                    recommendation = "Consider replacing with higher quality, smaller release"
            
            # Check for missing beneficial formats
            missing_hdr = not any("HDR" in cf.name.upper() for cf in file.custom_formats)
            missing_dv = not any("DOLBY" in cf.name.upper() and "VISION" in cf.name.upper() 
                               for cf in file.custom_formats)
            
            if file.resolution and "2160p" in file.resolution and missing_hdr:
                reasons.append("4K file missing HDR formats")
                priority = min(priority, 3)
                if not recommendation:
                    recommendation = "Look for HDR10 or Dolby Vision release"
            
            if reasons:
                candidates.append(UpgradeCandidate(
                    media_file=file,
                    reason="; ".join(reasons),
                    priority=priority,
                    potential_score_gain=potential_gain,
                    recommendation=recommendation
                ))
        
        # Sort by priority, then by potential score gain
        candidates.sort(key=lambda c: (c.priority, -(c.potential_score_gain or 0)))
        
        return candidates
    
    def analyze_quality_profiles(self, service_type: str) -> List[QualityProfileAnalysis]:
        """Analyze effectiveness of quality profiles."""
        analyses = []
        stats = self.db.calculate_library_stats(service_type)
        
        for profile_name, file_count in stats.quality_profiles.items():
            if file_count == 0:
                continue
                
            # Get files for this profile
            with self.db._get_connection() as conn:
                rows = conn.execute("""
                    SELECT total_score FROM media_files 
                    WHERE service_type = ? AND quality_profile_name = ?
                """, (service_type, profile_name)).fetchall()
            
            scores = [row[0] for row in rows]
            avg_score = statistics.mean(scores)
            
            # Score distribution
            distribution = {
                "excellent (>100)": sum(1 for s in scores if s > 100),
                "good (50-100)": sum(1 for s in scores if 50 <= s <= 100),
                "average (0-50)": sum(1 for s in scores if 0 <= s < 50),
                "poor (-50-0)": sum(1 for s in scores if -50 <= s < 0),
                "terrible (<-50)": sum(1 for s in scores if s < -50)
            }
            
            # Identify issues and recommendations
            issues = []
            recommendations = []
            
            poor_percentage = (distribution["poor (-50-0)"] + distribution["terrible (<-50)"]) / file_count
            if poor_percentage > 0.3:
                issues.append(f"{poor_percentage:.1%} of files have poor scores")
                recommendations.append("Review custom format priorities and scoring")
            
            if avg_score < stats.avg_score - 20:
                issues.append("Below library average performance")
                recommendations.append("Consider adjusting format weights or cutoffs")
            
            # Effectiveness rating
            if avg_score > 75:
                effectiveness = "excellent"
            elif avg_score > 25:
                effectiveness = "good"
            elif avg_score > -10:
                effectiveness = "fair"
            else:
                effectiveness = "poor"
            
            analyses.append(QualityProfileAnalysis(
                profile_name=profile_name,
                file_count=file_count,
                avg_score=avg_score,
                score_distribution=distribution,
                common_issues=issues,
                recommendations=recommendations,
                effectiveness_rating=effectiveness
            ))
        
        return sorted(analyses, key=lambda a: a.avg_score, reverse=True)
    
    def analyze_custom_format_effectiveness(self, service_type: str) -> List[CustomFormatEffectiveness]:
        """Analyze which custom formats are most/least effective."""
        format_stats = defaultdict(lambda: {"count": 0, "total_score": 0, "files": set()})
        
        # Get all files and their formats
        with self.db._get_connection() as conn:
            rows = conn.execute("""
                SELECT custom_formats_json, total_score, unique_identifier
                FROM media_files WHERE service_type = ? AND custom_formats_json IS NOT NULL
            """, (service_type,)).fetchall()
        
        for row in rows:
            try:
                import json
                formats = json.loads(row[0])
                file_score = row[1]
                file_id = row[2]
                
                for cf in formats:
                    name = cf.get("name", "Unknown")
                    
                    format_stats[name]["count"] += 1
                    format_stats[name]["total_score"] += file_score  # Use file's total score
                    format_stats[name]["files"].add(file_id)
            except (json.JSONDecodeError, TypeError):
                continue
        
        effectiveness_list = []
        for format_name, stats in format_stats.items():
            if stats["count"] == 0:
                continue
                
            avg_contribution = stats["total_score"] / stats["count"]
            usage_count = stats["count"]
            files_with_format = len(stats["files"])
            
            # Determine impact rating
            if avg_contribution > 50:
                impact = "high"
            elif avg_contribution > 10:
                impact = "medium"
            elif avg_contribution >= 0:
                impact = "low"
            else:
                impact = "negative"
            
            # Generate recommendations
            recommendations = []
            if avg_contribution < -20:
                recommendations.append("Consider removing or reducing score weight")
            elif avg_contribution > 100 and usage_count < 10:
                recommendations.append("Highly effective but underutilized - promote this format")
            elif usage_count > 100 and abs(avg_contribution) < 5:
                recommendations.append("High usage but low impact - review necessity")
            
            effectiveness_list.append(CustomFormatEffectiveness(
                format_name=format_name,
                usage_count=usage_count,
                avg_score_contribution=avg_contribution,
                files_with_format=files_with_format,
                impact_rating=impact,
                recommendations=recommendations
            ))
        
        return sorted(effectiveness_list, key=lambda e: e.avg_score_contribution, reverse=True)
    
    def analyze_historical_trends(self, service_type: str, days: int = 90) -> Dict[str, Any]:
        """Analyze historical trends and patterns in library health over time."""
        trends = self.db.get_score_trends(days, service_type)
        
        # Group trends by time periods
        from collections import defaultdict
        import datetime
        
        weekly_data = defaultdict(lambda: {'improvements': 0, 'degradations': 0})
        monthly_data = defaultdict(lambda: {'improvements': 0, 'degradations': 0})
        
        for trend in trends:
            timestamp = datetime.datetime.fromisoformat(trend['timestamp'])
            week_key = timestamp.strftime('%Y-W%U')
            month_key = timestamp.strftime('%Y-%m')
            
            if trend['change_type'] == 'improved':
                weekly_data[week_key]['improvements'] += 1
                monthly_data[month_key]['improvements'] += 1
            elif trend['change_type'] == 'degraded':
                weekly_data[week_key]['degradations'] += 1
                monthly_data[month_key]['degradations'] += 1
        
        # Calculate velocity metrics
        recent_weeks = sorted(weekly_data.keys())[-4:]  # Last 4 weeks
        recent_improvements = sum(weekly_data[week]['improvements'] for week in recent_weeks)
        recent_degradations = sum(weekly_data[week]['degradations'] for week in recent_weeks)
        
        improvement_velocity = recent_improvements / 4 if recent_weeks else 0
        degradation_velocity = recent_degradations / 4 if recent_weeks else 0
        
        # Identify patterns
        patterns = []
        if improvement_velocity > degradation_velocity * 2:
            patterns.append("Strong positive trend - library improving rapidly")
        elif degradation_velocity > improvement_velocity * 2:
            patterns.append("Concerning trend - library quality declining")
        elif improvement_velocity > 0 and degradation_velocity == 0:
            patterns.append("Perfect optimization - only improvements detected")
        elif abs(improvement_velocity - degradation_velocity) < 0.5:
            patterns.append("Stable library - minimal quality changes")
        
        # Generate recommendations based on trends
        trend_recommendations = []
        if degradation_velocity > improvement_velocity:
            trend_recommendations.append("Focus on preventing quality degradation")
            trend_recommendations.append("Review recent releases that scored lower")
        elif improvement_velocity > 2:
            trend_recommendations.append("Excellent progress! Consider documenting successful practices")
        elif improvement_velocity == 0 and degradation_velocity == 0:
            trend_recommendations.append("Consider proactive library optimization")
        
        return {
            'weekly_data': dict(weekly_data),
            'monthly_data': dict(monthly_data),
            'improvement_velocity': improvement_velocity,
            'degradation_velocity': degradation_velocity,
            'net_velocity': improvement_velocity - degradation_velocity,
            'patterns': patterns,
            'recommendations': trend_recommendations,
            'total_changes': len(trends)
        }
    
    def categorize_files_intelligently(self, service_type: str) -> Dict[str, List[MediaFile]]:
        """Intelligently categorize files based on patterns, scores, and metadata."""
        # Get all files for the service
        with self.db._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM media_files 
                WHERE service_type = ?
                ORDER BY total_score DESC
            """, (service_type,)).fetchall()
        
        files = [self.db._row_to_media_file(row) for row in rows]
        
        categories = {
            'premium_quality': [],      # High score, good formats
            'acceptable_quality': [],   # Mid-range scores
            'upgrade_worthy': [],       # Low scores but salvageable
            'priority_replacements': [], # Very poor quality
            'large_low_quality': [],    # Size/quality mismatch
            'format_optimized': [],     # Good format usage
            'legacy_content': [],       # Old/problematic formats
            'hdr_candidates': [],       # 4K files missing HDR
            'audio_upgrade_candidates': [], # Files with poor audio
            'resolution_mismatches': []  # Quality/resolution issues
        }
        
        stats = self.db.calculate_library_stats(service_type)
        avg_score = stats.avg_score
        
        for file in files:
            # Premium quality: High scores with good formats
            if file.total_score > max(75, avg_score + 30):
                categories['premium_quality'].append(file)
            
            # Acceptable quality: Around average or better
            elif file.total_score >= max(0, avg_score - 10):
                categories['acceptable_quality'].append(file)
            
            # Priority replacements: Very poor scores
            elif file.total_score < -50:
                categories['priority_replacements'].append(file)
            
            # Upgrade worthy: Poor but not terrible
            elif file.total_score < avg_score - 20:
                categories['upgrade_worthy'].append(file)
            
            # Size/quality analysis
            if file.size_bytes and stats.avg_file_size_gb > 0:
                file_size_gb = file.size_bytes / (1024**3)
                if file_size_gb > stats.avg_file_size_gb * 1.5 and file.total_score < 0:
                    categories['large_low_quality'].append(file)
            
            # Format analysis
            format_names = [cf.name.upper() for cf in file.custom_formats]
            
            # HDR candidates (4K without HDR)
            if (file.resolution and "2160" in file.resolution and 
                not any("HDR" in name or "DOLBY" in name for name in format_names)):
                categories['hdr_candidates'].append(file)
            
            # Audio upgrade candidates
            poor_audio_formats = ["AAC", "MP3", "OPUS"]
            if any(audio in name for name in format_names for audio in poor_audio_formats):
                categories['audio_upgrade_candidates'].append(file)
            
            # Legacy content detection
            legacy_formats = ["XVID", "DIVX", "YIFY", "RARBG", "AXXO"]
            if any(legacy in name for name in format_names for legacy in legacy_formats):
                categories['legacy_content'].append(file)
            
            # Format optimized (good format usage)
            premium_formats = ["REMUX", "BLURAY", "UHD", "ATMOS", "DTS-HD", "TRUEHD"]
            if (any(premium in name for name in format_names for premium in premium_formats) 
                and file.total_score > 50):
                categories['format_optimized'].append(file)
            
            # Resolution mismatches
            if (file.resolution and file.quality and 
                (("1080p" in str(file.resolution) and "720p" in str(file.quality)) or
                ("2160p" in str(file.resolution) and "1080p" in str(file.quality)))):
                categories['resolution_mismatches'].append(file)
        
        # Remove files from multiple categories (prioritize more specific categories)
        priority_order = [
            'priority_replacements', 'large_low_quality', 'hdr_candidates',
            'audio_upgrade_candidates', 'legacy_content', 'resolution_mismatches',
            'upgrade_worthy', 'format_optimized', 'premium_quality', 'acceptable_quality'
        ]
        
        assigned_files = set()
        cleaned_categories = {}
        
        for category in priority_order:
            cleaned_categories[category] = [
                f for f in categories[category] 
                if f.unique_identifier not in assigned_files
            ]
            assigned_files.update(f.unique_identifier for f in cleaned_categories[category])
        
        return cleaned_categories
    
    def generate_library_health_report(self, service_type: str, min_score_threshold: int = -50) -> LibraryHealthReport:
        """Generate comprehensive library health report."""
        stats = self.db.calculate_library_stats(service_type)
        candidates = self.identify_upgrade_candidates(service_type, min_score_threshold)
        profile_analysis = self.analyze_quality_profiles(service_type)
        format_effectiveness = self.analyze_custom_format_effectiveness(service_type)
        
        # Calculate health score (0-100)
        health_factors = []
        
        # Factor 1: Average score relative to good practices
        if stats.avg_score > 50:
            health_factors.append(100)
        elif stats.avg_score > 0:
            health_factors.append(75 + (stats.avg_score / 50) * 25)
        elif stats.avg_score > -50:
            health_factors.append(50 + ((stats.avg_score + 50) / 50) * 25)
        else:
            health_factors.append(max(0, 25 + ((stats.avg_score + 100) / 50) * 25))
        
        # Factor 2: Percentage of files with positive scores
        positive_percentage = stats.files_with_positive_scores / max(stats.total_files, 1)
        health_factors.append(positive_percentage * 100)
        
        # Factor 3: Upgrade candidates ratio (fewer is better)
        upgrade_ratio = len(candidates) / max(stats.total_files, 1)
        health_factors.append(max(0, 100 - (upgrade_ratio * 200)))
        
        health_score = statistics.mean(health_factors)
        
        # Health grade
        if health_score >= 90:
            health_grade = "A"
        elif health_score >= 80:
            health_grade = "B"
        elif health_score >= 70:
            health_grade = "C"
        elif health_score >= 60:
            health_grade = "D"
        else:
            health_grade = "F"
        
        # Generate recommendations
        recommendations = []
        achievements = []
        warnings = []
        
        if stats.avg_score > 50:
            achievements.append("Excellent average library score")
        elif stats.avg_score < -20:
            warnings.append("Poor average library score needs attention")
            recommendations.append("Review and optimize quality profile scoring")
        
        if positive_percentage > 0.8:
            achievements.append("Most files have positive quality scores")
        elif positive_percentage < 0.5:
            warnings.append("Many files have negative scores")
            recommendations.append("Focus on upgrading files with negative scores first")
        
        critical_candidates = [c for c in candidates if c.priority == 1]
        if critical_candidates:
            warnings.append(f"{len(critical_candidates)} files need immediate attention")
            recommendations.append("Prioritize upgrading critical files with very low scores")
        
        # Get score trends
        trends = self.db.get_score_trends(30, service_type)
        improvements = [t for t in trends if t['change_type'] == 'improved']
        degradations = [t for t in trends if t['change_type'] == 'degraded']
        
        score_trends = {
            "improvements_last_30_days": len(improvements),
            "degradations_last_30_days": len(degradations),
            "net_change": len(improvements) - len(degradations)
        }
        
        if score_trends["net_change"] > 0:
            achievements.append(f"Library quality improving: {score_trends['net_change']} net improvements")
        elif score_trends["net_change"] < -5:
            warnings.append("Library quality declining")
            recommendations.append("Investigate why scores are degrading")
        
        # Phase 2: Generate enhanced analytics
        historical_analysis = self.analyze_historical_trends(service_type)
        intelligent_categories = self.categorize_files_intelligently(service_type)
        
        # Add insights from historical analysis
        if historical_analysis['patterns']:
            for pattern in historical_analysis['patterns']:
                if 'positive' in pattern.lower():
                    achievements.append(pattern)
                elif 'concerning' in pattern.lower() or 'declining' in pattern.lower():
                    warnings.append(pattern)
        
        # Add insights from intelligent categorization
        category_insights = []
        if intelligent_categories['premium_quality']:
            category_insights.append(f"{len(intelligent_categories['premium_quality'])} files are premium quality")
        if intelligent_categories['priority_replacements']:
            category_insights.append(f"{len(intelligent_categories['priority_replacements'])} files need immediate replacement")
        if intelligent_categories['hdr_candidates']:
            category_insights.append(f"{len(intelligent_categories['hdr_candidates'])} 4K files missing HDR")
        
        if len(intelligent_categories['premium_quality']) > len(intelligent_categories['priority_replacements']) * 2:
            achievements.append("Library has strong quality distribution")
        
        # Store the threshold used for transparency
        report = LibraryHealthReport(
            service_type=service_type,
            generated_at=datetime.now(),
            health_score=health_score,
            health_grade=health_grade,
            total_files=stats.total_files,
            upgrade_candidates=candidates,  # All candidates (pagination handled in UI)
            quality_profile_analysis=profile_analysis,
            format_effectiveness=format_effectiveness[:15],  # Top 15 formats
            score_trends=score_trends,
            recommendations=recommendations,
            achievements=achievements,
            warnings=warnings,
            historical_analysis=historical_analysis,
            intelligent_categories=intelligent_categories
        )
        
        # Add threshold info for display (store as custom attribute)
        report.min_score_threshold = min_score_threshold
        return report