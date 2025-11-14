# AI Integration Architecture - FANWS Novel Writing System

## Overview

FANWS (Fiction AI Novel Writing Suite) uses a sophisticated AI integration system to generate complete novels automatically. This document describes the architecture, workflow, and integration points.

## Architecture Components

### 1. API Manager (`src/system/api_manager.py`)

**Purpose**: Centralized AI API management with caching, rate limiting, and threading support.

**Key Features**:
- Singleton pattern via `get_api_manager()`
- OpenAI GPT integration
- SQLite-based caching with LZ4 compression
- Rate limiting and request queueing
- Project context awareness
- Thread-safe async operations

**Main Methods**:
```python
generate_text_openai(prompt, max_tokens, temperature, api_key)
set_api_key(provider, key)
make_request_async(api_name, endpoint, method, data, headers)
```

### 2. Automated Novel Workflow (`src/workflow/automated_novel_workflow.py`)

**Purpose**: Background thread that orchestrates the complete novel generation process.

**Workflow Steps**:
1. **Initialization** - Project setup and file creation
2. **Synopsis Generation** - AI-generated 500-1000 word synopsis
3. **Structural Planning** - Outline, characters, world-building
4. **Timeline Synchronization** - Chronological consistency
5. **Iterative Writing** - Section-by-section content generation
6. **Completion** - Final consistency checks and export

**AI Integration Points**:
```python
# Synopsis with AI
synopsis = generate_synopsis_with_ai()
# Fallback: synopsis = simulate_synopsis_generation()

# Outline with AI  
outline = generate_outline_with_ai()

# Characters with AI
characters = generate_characters_with_ai()

# World-building with AI
world = generate_world_with_ai()

# Section content with AI (context-aware)
content = generate_section_with_ai(chapter, section, feedback)
```

### 3. Content Generator (`src/ai/content_generator.py`)

**Purpose**: Core AI content generation with consistency checking.

**Key Classes**:
- `ContentGenerator` - Main content generation engine
- `DraftManager` - Manages multiple draft versions
- `ConsistencyChecker` - Validates narrative consistency
- `WorkflowContext` - Maintains generation context

**Generation Methods**:
```python
generate_synopsis(prompt, max_tokens, api_key)
generate_outline(prompt, max_tokens, api_key)
generate_character_profiles(prompt, max_tokens, api_key)
generate_world_building(prompt, max_tokens, api_key)
generate_chapter(prompt, word_count, api_key)
```

### 4. Workflow Steps (`src/workflow/steps/`)

**Purpose**: 11-step modular workflow system with AI integration.

**Step 6 - Iterative Writing** (Key AI Step):
- 4-stage writing process:
  1. **Drafting** - AI-generated initial content
  2. **Polishing** - AI-enhanced grammar and flow
  3. **Enhancement** - AI-added literary devices
  4. **Vocabulary** - AI-refined word choice

**AI Methods in Steps**:
```python
# Step 6 methods
generate_ai_draft(context)
generate_ai_polish(context)
generate_ai_enhancement(context)
apply_vocabulary_refinement(context)
```

### 5. Workflow Coordinator (`src/workflow/coordinator.py`)

**Purpose**: Coordinates step execution and manages workflow state.

**Key Features**:
- Signal-based progress updates
- Step execution management
- Plugin system integration
- Legacy compatibility layer

## Data Flow

```
User Input (Idea, Tone, Target Words)
    ↓
API Manager (initialize)
    ↓
Automated Workflow Thread (start)
    ↓
┌─────────────────────────────────┐
│ Step 2: Synopsis Generation     │
│ - Call API with idea/tone       │
│ - Wait for approval              │
│ - Refine with feedback (if any) │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Step 4: Structural Planning     │
│ - Generate outline (25 chapters)│
│ - Generate character profiles   │
│ - Generate world-building       │
│ - Wait for approval each        │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Step 6-9: Iterative Writing     │
│ For each chapter (1-25):        │
│   For each section (1-5):       │
│     - Get story context         │
│     - Generate 800-1200 words   │
│     - Wait for approval         │
│     - Append to story           │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ Step 11: Completion & Export    │
│ - Final consistency check       │
│ - Quality assessment            │
│ - Export to formats             │
└─────────────────────────────────┘
    ↓
Complete Novel (200,000-300,000 words)
```

## Context Management

### Story Context Awareness

The AI system maintains context throughout generation:

**Previous Content Context**:
```python
def get_story_context(chapter, section):
    # Get last 500 words for continuity
    story = read_file("story.txt")
    words = story.split()
    return " ".join(words[-500:]) if len(words) > 500 else story
```

**Chapter Outline Context**:
```python
def get_chapter_outline(chapter):
    # Extract relevant chapter from full outline
    lines = self.outline.split('\n')
    chapter_lines = extract_chapter_lines(lines, chapter)
    return "\n".join(chapter_lines)
```

**Prompt Enhancement**:
```python
prompt = f"""Write section {section} of chapter {chapter}:

Synopsis: {self.synopsis}
Outline: {get_chapter_outline(chapter)}
Characters: {json.dumps(self.characters)}
World: {json.dumps(self.world)}
Previous content: {get_story_context(chapter, section)}

Write 800-1200 words in a {self.tone} tone..."""
```

## Error Handling & Fallbacks

### Graceful Degradation

```python
# Primary: Use AI if available
if self.api_manager:
    content = self.generate_section_with_ai(chapter, section)
else:
    # Fallback: Use simulation
    content = self.simulate_section_generation(chapter, section)
```

### Error Recovery

```python
try:
    response = self.api_manager.generate_text_openai(prompt, ...)
    if response and 'choices' in response:
        return response['choices'][0]['message']['content']
    else:
        return self.simulate_generation()  # Empty response fallback
except Exception as e:
    self.log(f"Error: {str(e)}")
    return self.simulate_generation()  # Exception fallback
```

## Configuration

### API Keys

Set via API Manager:
```python
api_manager = get_api_manager()
api_manager.set_api_key('openai', 'sk-...')
```

### Generation Parameters

```python
# Synopsis
max_tokens = 1500
temperature = 0.7  # Balanced creativity

# Section writing
max_tokens = 2000
temperature = 0.8  # Higher for creative prose
```

## Testing

### Validation Test Suite

Run `test_ai_integration.py` to validate:
1. API Manager availability
2. Automated workflow integration
3. Workflow steps AI methods
4. Content generator integration
5. Workflow coordinator compatibility

**Expected Result**: 5/5 tests passing (100%)

## Performance Considerations

### Caching

- **Memory Cache**: Fast lookup for recent requests
- **SQLite Cache**: Persistent cache with compression
- **Cache Key**: MD5 hash of `(api, endpoint, data, context)`

### Rate Limiting

- Default: 100 requests per hour
- Configurable via `RateLimiter(max_requests, time_window)`
- Automatic backoff when limit reached

### Async Operations

- QThread-based background processing
- Non-blocking UI during generation
- Signal-based progress updates

## Future Enhancements

1. **Multi-Provider Support**
   - Anthropic Claude integration
   - Local LLM support (Llama, etc.)
   - Provider failover and load balancing

2. **Enhanced Context**
   - Vector database for semantic search
   - Character relationship graphs
   - Timeline visualization

3. **Quality Improvements**
   - Style consistency checking
   - Tone analysis and adjustment
   - Automated proofreading

4. **Collaboration**
   - Real-time co-writing
   - Version control integration
   - Team feedback system

## Troubleshooting

### Common Issues

**1. API Integration Not Working**
- Check: `api_manager is not None`
- Verify: API key is set correctly
- Test: Run `test_ai_integration.py`

**2. Empty or Poor Quality Content**
- Increase `max_tokens` (e.g., 2000-3000)
- Adjust `temperature` (0.7-0.9 for creative writing)
- Enhance prompt with more context

**3. Workflow Hanging**
- Check: Approval signals are connected
- Verify: No infinite loops in wait states
- Monitor: Background thread status

## References

- API Manager: `src/system/api_manager.py`
- Automated Workflow: `src/workflow/automated_novel_workflow.py`
- Content Generator: `src/ai/content_generator.py`
- Workflow Steps: `src/workflow/steps/`
- Test Suite: `test_ai_integration.py`
- Main Application: `fanws.py`

---

*Last Updated: 2024*
*Version: 1.0*
