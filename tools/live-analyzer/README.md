# Live Analyzer Tool

Performance and usage tracking for HyperSync live development cycle.

## Purpose

The Live Analyzer supports the iterative development workflow:
**Build** → **Assemble** → **Use** → **Analyze** → **Iterate**

## Features

- **Usage Tracking**: Monitor function calls and execution times
- **Performance Analysis**: Collect and analyze performance metrics
- **Feedback Collection**: Gather AI model observations and suggestions
- **Report Generation**: Create comprehensive analysis reports

## Usage

### Track Component Usage

```bash
python analyze.py track \
  --component agua \
  --function geodesic_computation \
  --duration 15.3
```

### Collect Feedback

```bash
python analyze.py feedback \
  --component agua \
  --type issue \
  --message "Memory spike in high-dimensional cases"

python analyze.py feedback \
  --component agua \
  --type suggestion \
  --message "Consider caching geodesic paths"
```

### Analyze a Build

```bash
python analyze.py analyze \
  --build build-123 \
  --component agua
```

### Generate Component Report

```bash
python analyze.py report --component agua
```

## Data Storage

Analysis data is stored in each component's `analysis/` directory:

```
components/<stage>/<component>/analysis/
├── benchmarks/                # Performance benchmarks
├── usage-patterns/            # Usage logs
│   └── usage_log.jsonl       # Function call tracking
├── feedback/                  # AI feedback
│   ├── issue_feedback.jsonl  # Issues discovered
│   └── suggestion_feedback.jsonl  # Improvement suggestions
└── report_*.json              # Generated reports
```

## Output Format

### Usage Log Entry
```json
{
  "timestamp": "2026-02-19T22:30:00",
  "function": "geodesic_computation",
  "duration_ms": 15.3
}
```

### Feedback Entry
```json
{
  "timestamp": "2026-02-19T22:30:00",
  "type": "issue",
  "message": "Memory spike in high-dimensional cases"
}
```

### Analysis Report
```json
{
  "component": "agua",
  "generated": "2026-02-19T22:30:00",
  "performance": {
    "status": "analyzed",
    "metrics": {}
  },
  "usage": {
    "status": "analyzed",
    "total_calls": 150,
    "most_called": [
      ["geodesic_computation", 45],
      ["parallel_transport", 30]
    ]
  },
  "feedback": {
    "status": "analyzed",
    "issues_count": 2,
    "suggestions_count": 5,
    "recent_issues": ["..."],
    "recent_suggestions": ["..."]
  },
  "recommendations": [
    "Review and address feedback"
  ]
}
```

## Integration with Live Development

### 1. Build Phase
Create or modify component in `workspace/active/`

### 2. Assemble Phase
Integrate components in `workspace/assembly/build-NNN/`

### 3. Use Phase
Execute and track usage:
```python
start = time.time()
result = component.function()
duration = (time.time() - start) * 1000
analyzer.track_usage("component", "function", duration)
```

### 4. Analyze Phase
```bash
python analyze.py report --component component-name
```

### 5. Iterate Phase
Review report, apply improvements, create new iteration

## Extending the Analyzer

Add custom analyzers in `analyze.py`:

```python
def _analyze_custom_metric(self, component_path: Path) -> Dict[str, Any]:
    # Custom analysis logic
    return {"metric": "value"}
```

## Requirements

- Python 3.7+
- No external dependencies (uses stdlib only)
