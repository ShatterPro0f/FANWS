# FANWS Metadata Database Schema Guide

## Overview
The FANWS metadata system uses SQLite databases to store template information, user preferences, and version control data.

## Database Structure

### template_collections.db

#### template_collections Table
- `collection_id` (TEXT, PRIMARY KEY) - Unique identifier
- `name` (TEXT) - Display name of the collection
- `description` (TEXT) - Detailed description
- `author` (TEXT) - Creator of the collection
- `created_at` (TEXT) - ISO timestamp of creation
- `is_public` (INTEGER) - Whether publicly available (1/0)
- `download_count` (INTEGER) - Number of times downloaded

#### templates Table
- `id` (INTEGER, PRIMARY KEY) - Auto-incrementing template ID
- `collection_id` (INTEGER) - References template collection
- `name` (TEXT) - Template name
- `template_type` (TEXT) - Type (character, plot, world_building, etc.)
- `content` (TEXT) - Template content/description
- `variables` (TEXT) - JSON string of variables
- `usage_count` (INTEGER) - Number of times used
- `created_date` (TEXT) - Creation timestamp
- `updated_date` (TEXT) - Last update timestamp

#### collection_templates Table
- `collection_id` (TEXT, PRIMARY KEY) - Collection identifier
- `template_id` (TEXT, PRIMARY KEY) - Template identifier
- `order_index` (INTEGER) - Display order within collection

#### template_tags Table
- `id` (INTEGER, PRIMARY KEY) - Tag ID
- `template_id` (INTEGER) - Associated template
- `tag` (TEXT) - Tag text

### template_recommendations.db

#### user_profiles Table
- `user_id` (TEXT, PRIMARY KEY) - User identifier
- `preferred_categories` (TEXT) - Comma-separated category preferences
- `skill_level` (TEXT) - User's writing experience level
- `project_history` (TEXT) - Past writing projects
- `template_usage` (TEXT) - Usage history
- `ratings` (TEXT) - Template ratings given
- `created_templates` (TEXT) - User-created templates
- `last_activity` (TEXT) - Last activity timestamp

#### template_analytics Table
- `template_id` (TEXT, PRIMARY KEY) - Template identifier
- `metric_name` (TEXT, PRIMARY KEY) - Metric being tracked
- `metric_value` (REAL) - Numeric value of metric
- `recorded_at` (TEXT, PRIMARY KEY) - Recording timestamp

#### collaboration_data Table
- `user_id` (TEXT) - User identifier
- `template_id` (TEXT) - Template identifier
- `interaction_type` (TEXT) - Type of interaction
- `timestamp` (TEXT) - When interaction occurred
- `details` (TEXT) - Additional details

### template_versions.db

#### template_versions Table
- `template_id` (TEXT, PRIMARY KEY) - Template identifier
- `version` (TEXT, PRIMARY KEY) - Version number
- `release_date` (TEXT) - Version release date
- `changes` (TEXT) - Description of changes
- `compatibility` (TEXT) - Compatibility information
- `download_url` (TEXT) - Download location
- `is_stable` (INTEGER) - Whether version is stable (1/0)
- `predecessor_version` (TEXT) - Previous version

#### version_dependencies Table
- `template_id` (TEXT) - Template identifier
- `version` (TEXT) - Version requiring dependency
- `dependency_name` (TEXT) - Name of required dependency
- `dependency_version` (TEXT) - Required version
- `is_required` (INTEGER) - Whether dependency is required (1/0)

## Usage Examples

### Finding Popular Templates
```sql
SELECT name, usage_count FROM templates ORDER BY usage_count DESC LIMIT 10;
```

### Getting User Recommendations
```sql
SELECT template_id, metric_value FROM template_analytics 
WHERE metric_name = 'average_rating' AND metric_value >= 4.0;
```

### Version History
```sql
SELECT version, release_date, changes FROM template_versions 
WHERE template_id = '1' ORDER BY release_date DESC;
```

For technical support, consult the development team.
