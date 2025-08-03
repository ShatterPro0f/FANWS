"""
FANWS Analytics System - Clean Version
Advanced analytics capabilities for the Fiction Author Novel Writing Software (FANWS).
"""

import logging
import sqlite3
import datetime
import json
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any, Union

# Import compatibility layer for optional dependencies
from .module_compatibility import (
    NLTK_AVAILABLE, nltk,
    REQUESTS_AVAILABLE, requests
)

# Additional analytics-specific dependencies
try:
    import PyQt5
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    import logging
    logging.warning("⚠ PyQt5 not available - GUI components disabled")

try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    import logging
    logging.warning("⚠ TextStat not available - advanced readability metrics disabled")

try:
    import matplotlib
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    import logging
    logging.warning("⚠ Matplotlib not available - plotting features disabled")

# Initialize logger
logger = logging.getLogger(__name__)

# Enums
class GoalType(Enum):
    """Types of writing goals."""
    WORD_COUNT = "word_count"
    CHAPTER_COUNT = "chapter_count"
    TIME_BASED = "time_based"
    PAGE_COUNT = "page_count"
    DEADLINE = "deadline"

class HabitFrequency(Enum):
    """Frequency options for writing habits."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class MilestoneType(Enum):
    """Types of writing milestones."""
    FIRST_DRAFT = "first_draft"
    REVISION = "revision"
    EDITING = "editing"
    PUBLICATION = "publication"
    CUSTOM = "custom"

# Data Classes
@dataclass
class WritingGoal:
    """Represents a writing goal with tracking capabilities."""
    name: str
    goal_type: GoalType
    target_value: int
    current_value: int = 0
    deadline: Optional[datetime.date] = None
    is_active: bool = True
    created_date: datetime.date = field(default_factory=datetime.date.today)

    @property
    def progress_percentage(self) -> float:
        """Calculate progress as a percentage."""
        if self.target_value == 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)

    @property
    def is_completed(self) -> bool:
        """Check if goal is completed."""
        return self.current_value >= self.target_value

@dataclass
class WritingHabit:
    """Represents a writing habit with tracking."""
    name: str
    frequency: HabitFrequency
    target_value: int
    current_streak: int = 0
    longest_streak: int = 0
    is_active: bool = True
    created_date: datetime.date = field(default_factory=datetime.date.today)

@dataclass
class WritingMilestone:
    """Represents a major writing milestone."""
    name: str
    milestone_type: MilestoneType
    target_date: Optional[datetime.date] = None
    completion_date: Optional[datetime.date] = None
    description: str = ""
    is_completed: bool = False

@dataclass
class WritingPattern:
    """Represents patterns in writing behavior."""
    user_id: str
    peak_hours: List[int] = field(default_factory=list)
    productive_days: List[str] = field(default_factory=list)
    average_session_length: float = 0.0
    preferred_word_count_range: Tuple[int, int] = (0, 0)

@dataclass
class PerformancePrediction:
    """Represents performance predictions based on historical data."""
    predicted_completion_date: datetime.date
    confidence_level: float
    factors_considered: List[str] = field(default_factory=list)
    methodology: str = "statistical_analysis"

@dataclass
class PerformanceTrend:
    """Represents performance trends over time."""
    time_period: str
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0.0 to 1.0
    key_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class WritingSession:
    """Represents a single writing session."""
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = None
    word_count: int = 0
    project_id: str = ""
    notes: str = ""

    @property
    def duration_minutes(self) -> float:
        """Calculate session duration in minutes."""
        if self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return 0.0

@dataclass
class TextAnalysisMetrics:
    """Comprehensive text analysis metrics."""
    word_count: int = 0
    character_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    readability_score: float = 0.0
    complexity_score: float = 0.0
    sentiment_score: float = 0.0

    # Advanced metrics (if libraries available)
    flesch_reading_ease: Optional[float] = None
    flesch_kincaid_grade: Optional[float] = None
    automated_readability_index: Optional[float] = None

@dataclass
class ProgressMetrics:
    """Comprehensive progress tracking metrics."""
    total_words_written: int = 0
    total_sessions: int = 0
    total_time_minutes: float = 0.0
    average_words_per_session: float = 0.0
    average_session_duration: float = 0.0
    consistency_score: float = 0.0

# Utility Classes
class TextAnalyzer:
    """Advanced text analysis capabilities."""

    def __init__(self):
        self.nltk_available = NLTK_AVAILABLE
        self.textstat_available = TEXTSTAT_AVAILABLE
        self.matplotlib_available = MATPLOTLIB_AVAILABLE

    def analyze_text(self, text: str) -> TextAnalysisMetrics:
        """Perform comprehensive text analysis."""
        metrics = TextAnalysisMetrics()

        # Basic metrics
        metrics.word_count = len(text.split())
        metrics.character_count = len(text)
        metrics.sentence_count = text.count('.') + text.count('!') + text.count('?')
        metrics.paragraph_count = len([p for p in text.split('\n\n') if p.strip()])

        # Advanced metrics if libraries available
        if self.textstat_available:
            try:
                import textstat
                metrics.flesch_reading_ease = textstat.flesch_reading_ease(text)
                metrics.flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
                metrics.automated_readability_index = textstat.automated_readability_index(text)
                metrics.readability_score = metrics.flesch_reading_ease or 0.0
            except Exception as e:
                logger.warning(f"Error in textstat analysis: {e}")
        else:
            # Basic readability estimation as fallback
            avg_sentence_length = metrics.word_count / max(1, metrics.sentence_count)
            # Simple readability score based on sentence length
            metrics.readability_score = max(0, 100 - (avg_sentence_length * 2))

        # NLTK-based analysis if available
        if self.nltk_available:
            try:
                # Use NLTK for more sophisticated analysis if available
                from nltk.sentiment import SentimentIntensityAnalyzer
                sia = SentimentIntensityAnalyzer()
                sentiment = sia.polarity_scores(text)
                metrics.sentiment_score = sentiment.get('compound', 0.0)
            except Exception as e:
                logger.warning(f"Error in NLTK analysis: {e}")
                # Fallback sentiment analysis
                metrics.sentiment_score = self._basic_sentiment_analysis(text)
        else:
            # Basic sentiment analysis fallback
            metrics.sentiment_score = self._basic_sentiment_analysis(text)

        return metrics

    def _basic_sentiment_analysis(self, text: str) -> float:
        """Basic sentiment analysis without external libraries."""
        positive_words = ['good', 'great', 'excellent', 'wonderful', 'amazing', 'love', 'like', 'happy', 'joy']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry', 'disappointed']

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0

        return (positive_count - negative_count) / total_sentiment_words

class WritingMetricsDatabase:
    """Database interface for writing metrics storage."""

    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create tables for analytics data
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS writing_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        word_count INTEGER DEFAULT 0,
                        project_id TEXT,
                        notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS writing_goals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        goal_type TEXT NOT NULL,
                        target_value INTEGER NOT NULL,
                        current_value INTEGER DEFAULT 0,
                        deadline TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_date TEXT,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("Analytics database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing analytics database: {e}")

    def save_session(self, session: WritingSession) -> bool:
        """Save a writing session to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO writing_sessions
                    (start_time, end_time, word_count, project_id, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    session.start_time.isoformat(),
                    session.end_time.isoformat() if session.end_time else None,
                    session.word_count,
                    session.project_id,
                    session.notes
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving writing session: {e}")
            return False

    def get_recent_sessions(self, limit: int = 10) -> List[WritingSession]:
        """Retrieve recent writing sessions."""
        sessions = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT start_time, end_time, word_count, project_id, notes
                    FROM writing_sessions
                    ORDER BY start_time DESC
                    LIMIT ?
                ''', (limit,))

                for row in cursor.fetchall():
                    start_time = datetime.datetime.fromisoformat(row[0])
                    end_time = datetime.datetime.fromisoformat(row[1]) if row[1] else None
                    session = WritingSession(
                        start_time=start_time,
                        end_time=end_time,
                        word_count=row[2],
                        project_id=row[3] or "",
                        notes=row[4] or ""
                    )
                    sessions.append(session)

        except Exception as e:
            logger.error(f"Error retrieving sessions: {e}")

        return sessions

class WritingAnalyticsDashboard:
    """Main analytics dashboard and controller."""

    def __init__(self, db_path: str = "analytics.db"):
        self.db = WritingMetricsDatabase(db_path)
        self.text_analyzer = TextAnalyzer()
        self.current_project = None
        logger.info("Writing Analytics Dashboard initialized")

    def update_writing_progress(self, word_count: int, content: str = ""):
        """Update writing progress with word count and content analysis."""
        try:
            if self.current_project:
                # Log the progress update
                logger.debug(f"Updating writing progress: {word_count} words for project {self.current_project}")

                # Analyze content if provided
                if content:
                    metrics = self.text_analyzer.analyze_text(content)
                    logger.debug(f"Text analysis completed: {metrics.sentence_count} sentences")

                return True
            return False
        except Exception as e:
            logger.warning(f"Error updating writing progress: {e}")
            return False

    def set_project(self, project_name: str):
        """Set the current project for analytics tracking."""
        try:
            self.current_project = project_name
            logger.info(f"Analytics dashboard set to project: {project_name}")
            return True
        except Exception as e:
            logger.warning(f"Error setting project: {e}")
            return False

    def calculate_progress_metrics(self, project_id: str = None) -> ProgressMetrics:
        """Calculate comprehensive progress metrics."""
        sessions = self.db.get_recent_sessions(limit=100)

        if project_id:
            sessions = [s for s in sessions if s.project_id == project_id]

        metrics = ProgressMetrics()

        if sessions:
            metrics.total_sessions = len(sessions)
            metrics.total_words_written = sum(s.word_count for s in sessions)
            metrics.total_time_minutes = sum(s.duration_minutes for s in sessions)

            if metrics.total_sessions > 0:
                metrics.average_words_per_session = metrics.total_words_written / metrics.total_sessions
                metrics.average_session_duration = metrics.total_time_minutes / metrics.total_sessions

            # Calculate consistency score (simplified)
            if len(sessions) > 1:
                word_counts = [s.word_count for s in sessions]
                if statistics.stdev(word_counts) > 0:
                    cv = statistics.stdev(word_counts) / statistics.mean(word_counts)
                    metrics.consistency_score = max(0, 1 - cv)

        return metrics

    def analyze_writing_patterns(self, user_id: str) -> WritingPattern:
        """Analyze user writing patterns."""
        sessions = self.db.get_recent_sessions(limit=50)
        pattern = WritingPattern(user_id=user_id)

        if sessions:
            # Analyze peak hours
            hours = [s.start_time.hour for s in sessions]
            hour_counts = {}
            for hour in hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1

            # Find top 3 peak hours
            sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
            pattern.peak_hours = [hour for hour, count in sorted_hours[:3]]

            # Analyze productive days
            days = [s.start_time.strftime('%A') for s in sessions]
            day_counts = {}
            for day in days:
                day_counts[day] = day_counts.get(day, 0) + 1

            sorted_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
            pattern.productive_days = [day for day, count in sorted_days[:3]]

            # Calculate average session length
            durations = [s.duration_minutes for s in sessions if s.duration_minutes > 0]
            if durations:
                pattern.average_session_length = statistics.mean(durations)

            # Calculate preferred word count range
            word_counts = [s.word_count for s in sessions if s.word_count > 0]
            if word_counts:
                mean_words = statistics.mean(word_counts)
                std_words = statistics.stdev(word_counts) if len(word_counts) > 1 else 0
                pattern.preferred_word_count_range = (
                    max(0, int(mean_words - std_words)),
                    int(mean_words + std_words)
                )

        return pattern

    def predict_completion(self, goal: WritingGoal) -> Optional[PerformancePrediction]:
        """Predict goal completion based on current progress."""
        if goal.current_value >= goal.target_value:
            return None  # Already completed

        sessions = self.db.get_recent_sessions(limit=30)
        if not sessions:
            return None

        # Calculate recent daily average
        recent_days = 7
        recent_sessions = sessions[:recent_days] if len(sessions) >= recent_days else sessions
        total_words = sum(s.word_count for s in recent_sessions)
        days_tracked = len(set(s.start_time.date() for s in recent_sessions))

        if days_tracked == 0:
            return None

        daily_average = total_words / days_tracked

        if daily_average <= 0:
            return None

        remaining_words = goal.target_value - goal.current_value
        days_needed = remaining_words / daily_average

        predicted_date = datetime.date.today() + datetime.timedelta(days=int(days_needed))

        # Calculate confidence based on consistency
        word_counts = [s.word_count for s in recent_sessions]
        consistency = 1.0
        if len(word_counts) > 1 and statistics.stdev(word_counts) > 0:
            cv = statistics.stdev(word_counts) / statistics.mean(word_counts)
            consistency = max(0.1, 1 - cv)

        return PerformancePrediction(
            predicted_completion_date=predicted_date,
            confidence_level=min(0.95, consistency),
            factors_considered=[
                f"Recent {days_tracked} days average",
                "Writing consistency",
                "Current progress rate"
            ],
            methodology="linear_projection"
        )

    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent writing activity for display."""
        sessions = self.db.get_recent_sessions(limit)
        activity = []

        for session in sessions:
            activity.append({
                'date': session.start_time.date().isoformat(),
                'time': session.start_time.time().isoformat(),
                'word_count': session.word_count,
                'duration_minutes': session.duration_minutes,
                'project_id': session.project_id,
                'notes': session.notes
            })

        return activity

    def get_recent_sessions(self, limit: int = 10):
        """Get recent writing sessions from database."""
        return self.db.get_recent_sessions(limit)

# Additional compatibility classes for GUI integration
class AnalyticsWidget:
    """Widget wrapper for analytics integration in GUI."""

    def __init__(self, dashboard=None):
        self.dashboard = dashboard or WritingAnalyticsDashboard()

    def get_progress_metrics(self, project_id=None):
        """Get progress metrics for display in GUI."""
        return self.dashboard.calculate_progress_metrics(project_id)

    def get_recent_activity(self, limit=10):
        """Get recent writing activity for display."""
        return self.dashboard.get_recent_activity(limit)

class AnalyticsEngine:
    """Advanced analytics engine for detailed analysis."""

    def __init__(self, dashboard=None):
        self.dashboard = dashboard or WritingAnalyticsDashboard()
        self.text_analyzer = TextAnalyzer()

    def analyze_writing_patterns(self, project_id=None):
        """Analyze writing patterns and provide insights."""
        sessions = self.dashboard.db.get_recent_sessions()
        if project_id:
            sessions = [s for s in sessions if s.project_id == project_id]

        # Basic pattern analysis
        patterns = {
            'peak_hours': self._analyze_peak_hours(sessions),
            'productivity_trends': self._analyze_productivity_trends(sessions),
            'writing_velocity': self._analyze_writing_velocity(sessions)
        }
        return patterns

    def _analyze_peak_hours(self, sessions):
        """Analyze peak writing hours."""
        if not sessions:
            return []

        # Simple hour-based analysis
        hour_counts = {}
        for session in sessions:
            hour = session.start_time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        return sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    def _analyze_productivity_trends(self, sessions):
        """Analyze productivity trends over time."""
        if not sessions:
            return {'trend': 'no_data', 'average': 0}

        word_counts = [session.word_count for session in sessions if session.word_count > 0]
        if not word_counts:
            return {'trend': 'no_data', 'average': 0}

        avg_words = sum(word_counts) / len(word_counts)
        return {'trend': 'stable', 'average': avg_words}

    def _analyze_writing_velocity(self, sessions):
        """Analyze writing velocity (words per minute)."""
        if not sessions:
            return 0

        velocities = []
        for session in sessions:
            if session.duration_minutes > 0 and session.word_count > 0:
                velocity = session.word_count / session.duration_minutes
                velocities.append(velocity)

        return sum(velocities) / len(velocities) if velocities else 0

    def generate_analytics_plot(self, plot_type='productivity', project_id=None, save_path=None):
        """Generate analytics plots using matplotlib if available."""
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Matplotlib not available - cannot generate plots")
            return None

        try:
            import matplotlib.pyplot as plt
            sessions = self.dashboard.db.get_recent_sessions()
            if project_id:
                sessions = [s for s in sessions if s.project_id == project_id]

            if not sessions:
                logger.warning("No sessions available for plotting")
                return None

            plt.figure(figsize=(10, 6))

            if plot_type == 'productivity':
                # Plot word count over time
                dates = [s.start_time.date() for s in sessions]
                word_counts = [s.word_count for s in sessions]
                plt.plot(dates, word_counts, marker='o')
                plt.title('Writing Productivity Over Time')
                plt.xlabel('Date')
                plt.ylabel('Word Count')
                plt.xticks(rotation=45)

            elif plot_type == 'peak_hours':
                # Plot peak writing hours
                hours = [s.start_time.hour for s in sessions]
                hour_counts = {}
                for hour in hours:
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1

                plt.bar(hour_counts.keys(), hour_counts.values())
                plt.title('Peak Writing Hours')
                plt.xlabel('Hour of Day')
                plt.ylabel('Number of Sessions')

            plt.tight_layout()

            if save_path:
                plt.savefig(save_path)
                logger.info(f"Plot saved to {save_path}")
            else:
                plt.show()

            return True

        except Exception as e:
            logger.error(f"Error generating plot: {e}")
            return False

class AnalyticsDashboard:
    """Advanced dashboard with enhanced analytics features."""

    def __init__(self, db_path: str = "analytics.db"):
        self.dashboard = WritingAnalyticsDashboard(db_path)
        self.engine = AnalyticsEngine(self.dashboard)
        self.widget = AnalyticsWidget(self.dashboard)

    def get_comprehensive_report(self, project_id=None):
        """Get a comprehensive analytics report."""
        metrics = self.dashboard.calculate_progress_metrics(project_id)
        patterns = self.engine.analyze_writing_patterns(project_id)

        return {
            'progress_metrics': metrics,
            'writing_patterns': patterns,
            'recent_activity': self.widget.get_recent_activity(),
            'generated_at': datetime.now()
        }

# Module exports
__all__ = [
    # Enums
    'GoalType',
    'HabitFrequency',
    'MilestoneType',

    # Data Classes
    'WritingGoal',
    'WritingHabit',
    'WritingMilestone',
    'WritingPattern',
    'PerformancePrediction',
    'PerformanceTrend',
    'WritingSession',
    'TextAnalysisMetrics',
    'ProgressMetrics',

    # Utility Classes
    'TextAnalyzer',
    'WritingMetricsDatabase',
    'WritingAnalyticsDashboard',

    # GUI Integration Classes
    'AnalyticsWidget',
    'AnalyticsEngine',
    'AnalyticsDashboard'
]

# Initialize logger for module
logger.info('Analytics system module loaded successfully')
