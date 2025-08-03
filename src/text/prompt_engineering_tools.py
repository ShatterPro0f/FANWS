"""
Prompt Engineering Tools Module
Priority 5.2: Advanced prompt management and optimization system
Created: July 12, 2025
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import sqlite3
from pathlib import Path
import statistics
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class PromptType(Enum):
    """Types of prompts in the system."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TEMPLATE = "template"

class PromptCategory(Enum):
    """Categories for prompt organization."""
    CREATIVE_WRITING = "creative_writing"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    CONVERSATION = "conversation"
    INSTRUCTION = "instruction"
    QUESTION_ANSWERING = "question_answering"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"

@dataclass
class PromptMetrics:
    """Metrics for prompt performance evaluation."""
    response_time: float = 0.0
    token_count: int = 0
    completion_length: int = 0
    quality_score: float = 0.0
    user_rating: Optional[int] = None
    success_rate: float = 1.0
    usage_count: int = 0
    error_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PromptTemplate:
    """A reusable prompt template with variables."""
    id: str
    name: str
    content: str
    category: PromptCategory
    prompt_type: PromptType
    variables: List[str] = field(default_factory=list)
    description: str = ""
    tags: List[str] = field(default_factory=list)
    version: str = "1.0"
    author: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metrics: PromptMetrics = field(default_factory=PromptMetrics)
    is_active: bool = True

    def render(self, **kwargs) -> str:
        """Render the template with provided variables."""
        rendered = self.content
        for var in self.variables:
            if var in kwargs:
                placeholder = f"{{{var}}}"
                rendered = rendered.replace(placeholder, str(kwargs[var]))
        return rendered

    def get_missing_variables(self, **kwargs) -> List[str]:
        """Get list of variables that weren't provided."""
        return [var for var in self.variables if var not in kwargs]

    def validate_variables(self, **kwargs) -> bool:
        """Check if all required variables are provided."""
        return len(self.get_missing_variables(**kwargs)) == 0

@dataclass
class PromptExperiment:
    """A/B testing experiment for prompt optimization."""
    id: str
    name: str
    description: str
    variants: List[PromptTemplate]
    control_variant_id: str
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    is_active: bool = True
    min_samples: int = 30
    confidence_level: float = 0.95
    results: Dict[str, PromptMetrics] = field(default_factory=dict)

class PromptDatabase:
    """SQLite database for storing prompts and metrics."""

    def __init__(self, db_path: str = "prompt_engineering.db"):
        self.db_path = Path(db_path)
        self._init_database()

    def _init_database(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Prompt templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    prompt_type TEXT NOT NULL,
                    variables TEXT,
                    description TEXT,
                    tags TEXT,
                    version TEXT,
                    author TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    is_active BOOLEAN,
                    usage_count INTEGER DEFAULT 0,
                    avg_quality_score REAL DEFAULT 0.0,
                    avg_response_time REAL DEFAULT 0.0
                )
            """)

            # Prompt metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id TEXT,
                    response_time REAL,
                    token_count INTEGER,
                    completion_length INTEGER,
                    quality_score REAL,
                    user_rating INTEGER,
                    success_rate REAL,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (prompt_id) REFERENCES prompt_templates (id)
                )
            """)

            # Experiments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_experiments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    control_variant_id TEXT,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    is_active BOOLEAN,
                    min_samples INTEGER,
                    confidence_level REAL
                )
            """)

            conn.commit()

    def save_template(self, template: PromptTemplate):
        """Save a prompt template to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO prompt_templates
                (id, name, content, category, prompt_type, variables, description,
                 tags, version, author, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template.id, template.name, template.content,
                template.category.value, template.prompt_type.value,
                json.dumps(template.variables), template.description,
                json.dumps(template.tags), template.version, template.author,
                template.created_at.isoformat(), template.updated_at.isoformat(),
                template.is_active
            ))
            conn.commit()

    def load_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Load a prompt template from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM prompt_templates WHERE id = ?
            """, (template_id,))
            row = cursor.fetchone()

            if row:
                return PromptTemplate(
                    id=row[0], name=row[1], content=row[2],
                    category=PromptCategory(row[3]),
                    prompt_type=PromptType(row[4]),
                    variables=json.loads(row[5] or "[]"),
                    description=row[6] or "",
                    tags=json.loads(row[7] or "[]"),
                    version=row[8], author=row[9],
                    created_at=datetime.fromisoformat(row[10]),
                    updated_at=datetime.fromisoformat(row[11]),
                    is_active=bool(row[12])
                )
        return None

    def record_metrics(self, prompt_id: str, metrics: PromptMetrics):
        """Record performance metrics for a prompt."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO prompt_metrics
                (prompt_id, response_time, token_count, completion_length,
                 quality_score, user_rating, success_rate, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt_id, metrics.response_time, metrics.token_count,
                metrics.completion_length, metrics.quality_score,
                metrics.user_rating, metrics.success_rate,
                metrics.timestamp.isoformat()
            ))

            # Update template statistics
            cursor.execute("""
                UPDATE prompt_templates
                SET usage_count = usage_count + 1,
                    avg_quality_score = (
                        SELECT AVG(quality_score) FROM prompt_metrics
                        WHERE prompt_id = ?
                    ),
                    avg_response_time = (
                        SELECT AVG(response_time) FROM prompt_metrics
                        WHERE prompt_id = ?
                    )
                WHERE id = ?
            """, (prompt_id, prompt_id, prompt_id))

            conn.commit()

class PromptOptimizer:
    """Advanced prompt optimization and analysis tools."""

    def __init__(self, database: PromptDatabase):
        self.database = database

    def analyze_prompt_performance(self, prompt_id: str,
                                 days_back: int = 30) -> Dict[str, Any]:
        """Analyze performance metrics for a prompt."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        with sqlite3.connect(self.database.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT response_time, token_count, completion_length,
                       quality_score, user_rating, success_rate
                FROM prompt_metrics
                WHERE prompt_id = ? AND timestamp >= ? AND timestamp <= ?
            """, (prompt_id, start_date.isoformat(), end_date.isoformat()))

            rows = cursor.fetchall()

            if not rows:
                return {"error": "No data found for the specified period"}

            response_times = [r[0] for r in rows if r[0] is not None]
            token_counts = [r[1] for r in rows if r[1] is not None]
            completion_lengths = [r[2] for r in rows if r[2] is not None]
            quality_scores = [r[3] for r in rows if r[3] is not None]
            user_ratings = [r[4] for r in rows if r[4] is not None]
            success_rates = [r[5] for r in rows if r[5] is not None]

            return {
                "total_uses": len(rows),
                "response_time": {
                    "avg": statistics.mean(response_times) if response_times else 0,
                    "median": statistics.median(response_times) if response_times else 0,
                    "std": statistics.stdev(response_times) if len(response_times) > 1 else 0
                },
                "token_efficiency": {
                    "avg_tokens": statistics.mean(token_counts) if token_counts else 0,
                    "avg_completion": statistics.mean(completion_lengths) if completion_lengths else 0,
                    "efficiency_ratio": (
                        statistics.mean(completion_lengths) / statistics.mean(token_counts)
                        if token_counts and completion_lengths else 0
                    )
                },
                "quality": {
                    "avg_score": statistics.mean(quality_scores) if quality_scores else 0,
                    "avg_rating": statistics.mean(user_ratings) if user_ratings else 0,
                    "success_rate": statistics.mean(success_rates) if success_rates else 0
                }
            }

    def suggest_optimizations(self, prompt_id: str) -> List[str]:
        """Suggest optimizations based on performance analysis."""
        analysis = self.analyze_prompt_performance(prompt_id)
        suggestions = []

        if "error" in analysis:
            return ["No data available for optimization suggestions"]

        # Response time optimization
        if analysis["response_time"]["avg"] > 5.0:
            suggestions.append("Consider reducing prompt length to improve response time")

        # Token efficiency optimization
        if analysis["token_efficiency"]["efficiency_ratio"] < 0.5:
            suggestions.append("Prompt may be too verbose - consider condensing")

        # Quality optimization
        if analysis["quality"]["avg_score"] < 7.0:
            suggestions.append("Quality scores are low - consider revising prompt clarity")

        if analysis["quality"]["success_rate"] < 0.8:
            suggestions.append("High failure rate - review prompt instructions")

        # Usage-based suggestions
        if analysis["total_uses"] < 10:
            suggestions.append("Limited usage data - consider A/B testing")

        return suggestions if suggestions else ["Prompt performance is optimal"]

class PromptEngineeringManager:
    """Main manager for prompt engineering tools."""

    def __init__(self, db_path: str = "prompt_engineering.db"):
        self.database = PromptDatabase(db_path)
        self.optimizer = PromptOptimizer(self.database)
        self.active_experiments: Dict[str, PromptExperiment] = {}

        # Built-in template library
        self._init_template_library()

    def _init_template_library(self):
        """Initialize the built-in template library."""
        templates = [
            PromptTemplate(
                id="creative_story_start",
                name="Creative Story Starter",
                content="Write a compelling opening paragraph for a {genre} story about {main_character} who {conflict}. Set it in {setting} and establish {mood} tone.",
                category=PromptCategory.CREATIVE_WRITING,
                prompt_type=PromptType.USER,
                variables=["genre", "main_character", "conflict", "setting", "mood"],
                description="Template for generating story openings",
                tags=["creative", "story", "opening"],
                author="system"
            ),
            PromptTemplate(
                id="code_explanation",
                name="Code Explanation",
                content="Explain the following {language} code in simple terms. Focus on what it does, how it works, and any important concepts:\n\n```{language}\n{code}\n```",
                category=PromptCategory.CODE_GENERATION,
                prompt_type=PromptType.USER,
                variables=["language", "code"],
                description="Template for explaining code snippets",
                tags=["code", "explanation", "tutorial"],
                author="system"
            ),
            PromptTemplate(
                id="text_analysis",
                name="Text Analysis",
                content="Analyze the following text for {analysis_type}. Provide specific examples and explain your reasoning:\n\n\"{text}\"",
                category=PromptCategory.ANALYSIS,
                prompt_type=PromptType.USER,
                variables=["analysis_type", "text"],
                description="Template for text analysis tasks",
                tags=["analysis", "text", "reasoning"],
                author="system"
            )
        ]

        for template in templates:
            try:
                existing = self.database.load_template(template.id)
                if not existing:
                    self.database.save_template(template)
                    logger.info(f"Added template: {template.name}")
            except Exception as e:
                logger.error(f"Failed to add template {template.id}: {e}")

    def create_template(self, name: str, content: str, category: PromptCategory,
                       prompt_type: PromptType = PromptType.USER,
                       variables: List[str] = None, description: str = "",
                       tags: List[str] = None) -> PromptTemplate:
        """Create a new prompt template."""
        template_id = hashlib.md5(f"{name}_{content}".encode()).hexdigest()

        template = PromptTemplate(
            id=template_id,
            name=name,
            content=content,
            category=category,
            prompt_type=prompt_type,
            variables=variables or [],
            description=description,
            tags=tags or []
        )

        self.database.save_template(template)
        logger.info(f"Created template: {name} ({template_id})")
        return template

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Retrieve a prompt template."""
        return self.database.load_template(template_id)

    def list_templates(self, category: Optional[PromptCategory] = None,
                      tags: List[str] = None) -> List[PromptTemplate]:
        """List available templates with optional filtering."""
        with sqlite3.connect(self.database.db_path) as conn:
            cursor = conn.cursor()

            query = "SELECT id FROM prompt_templates WHERE is_active = 1"
            params = []

            if category:
                query += " AND category = ?"
                params.append(category.value)

            cursor.execute(query, params)
            template_ids = [row[0] for row in cursor.fetchall()]

            templates = []
            for template_id in template_ids:
                template = self.database.load_template(template_id)
                if template:
                    # Filter by tags if specified
                    if tags and not any(tag in template.tags for tag in tags):
                        continue
                    templates.append(template)

            return templates

    def render_template(self, template_id: str, **kwargs) -> Optional[str]:
        """Render a template with provided variables."""
        template = self.get_template(template_id)
        if not template:
            return None

        missing_vars = template.get_missing_variables(**kwargs)
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        return template.render(**kwargs)

    def record_usage(self, template_id: str, response_time: float = 0.0,
                    token_count: int = 0, completion_length: int = 0,
                    quality_score: float = 0.0, user_rating: Optional[int] = None,
                    success: bool = True):
        """Record usage metrics for a template."""
        metrics = PromptMetrics(
            response_time=response_time,
            token_count=token_count,
            completion_length=completion_length,
            quality_score=quality_score,
            user_rating=user_rating,
            success_rate=1.0 if success else 0.0,
            usage_count=1
        )

        self.database.record_metrics(template_id, metrics)

    def analyze_template(self, template_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Analyze template performance."""
        return self.optimizer.analyze_prompt_performance(template_id, days_back)

    def get_optimization_suggestions(self, template_id: str) -> List[str]:
        """Get optimization suggestions for a template."""
        return self.optimizer.suggest_optimizations(template_id)

    def start_ab_test(self, experiment_name: str, description: str,
                     control_template: PromptTemplate,
                     variant_templates: List[PromptTemplate],
                     min_samples: int = 30) -> PromptExperiment:
        """Start an A/B test experiment."""
        experiment_id = hashlib.md5(f"{experiment_name}_{time.time()}".encode()).hexdigest()

        all_variants = [control_template] + variant_templates

        experiment = PromptExperiment(
            id=experiment_id,
            name=experiment_name,
            description=description,
            variants=all_variants,
            control_variant_id=control_template.id,
            min_samples=min_samples
        )

        self.active_experiments[experiment_id] = experiment
        logger.info(f"Started A/B test: {experiment_name} ({experiment_id})")
        return experiment

    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get results from an A/B test experiment."""
        if experiment_id not in self.active_experiments:
            return {"error": "Experiment not found"}

        experiment = self.active_experiments[experiment_id]
        results = {}

        for variant in experiment.variants:
            analysis = self.analyze_template(variant.id)
            results[variant.id] = {
                "name": variant.name,
                "analysis": analysis,
                "is_control": variant.id == experiment.control_variant_id
            }

        return {
            "experiment": experiment.name,
            "status": "active" if experiment.is_active else "completed",
            "variants": results
        }

    def get_template_recommendations(self, task_description: str,
                                   limit: int = 5) -> List[PromptTemplate]:
        """Get template recommendations based on task description."""
        # Simple keyword-based matching for now
        keywords = task_description.lower().split()
        templates = self.list_templates()

        scored_templates = []
        for template in templates:
            score = 0
            # Check name, description, and tags for keyword matches
            text_to_search = f"{template.name} {template.description} {' '.join(template.tags)}".lower()

            for keyword in keywords:
                if keyword in text_to_search:
                    score += 1

            if score > 0:
                scored_templates.append((score, template))

        # Sort by score and return top results
        scored_templates.sort(key=lambda x: x[0], reverse=True)
        return [template for _, template in scored_templates[:limit]]
