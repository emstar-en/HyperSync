#!/bin/bash
# Component Creator Tool for HyperSync
# Usage: ./create-component.sh --name <component-name> --stage <experimental|stable|production> [--derived-from <parent>] [--type <type>]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

show_usage() {
    echo "Usage: $0 --name <component-name> --stage <experimental|stable|production> [OPTIONS]"
    echo ""
    echo "Required:"
    echo "  --name NAME           Component name (lowercase, hyphen-separated)"
    echo "  --stage STAGE         Lifecycle stage: experimental, stable, or production"
    echo ""
    echo "Optional:"
    echo "  --derived-from PARENT Component this derives from"
    echo "  --type TYPE          Component type: foundation, runtime, extension, tool"
    echo "  --domain DOMAINS     Comma-separated domain keywords"
    echo "  --help              Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --name geometric-quantum --stage experimental --derived-from agua --type extension"
}

COMPONENT_NAME=""
STAGE=""
DERIVED_FROM=""
TYPE="extension"
DOMAIN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            COMPONENT_NAME="$2"
            shift 2
            ;;
        --stage)
            STAGE="$2"
            shift 2
            ;;
        --derived-from)
            DERIVED_FROM="$2"
            shift 2
            ;;
        --type)
            TYPE="$2"
            shift 2
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

if [ -z "$COMPONENT_NAME" ] || [ -z "$STAGE" ]; then
    echo "Error: --name and --stage are required"
    show_usage
    exit 1
fi

if [[ ! "$STAGE" =~ ^(experimental|stable|production)$ ]]; then
    echo "Error: --stage must be experimental, stable, or production"
    exit 1
fi

COMPONENT_PATH="$PROJECT_ROOT/components/$STAGE/$COMPONENT_NAME"

if [ -d "$COMPONENT_PATH" ]; then
    echo "Error: Component already exists at $COMPONENT_PATH"
    exit 1
fi

echo "Creating component: $COMPONENT_NAME"
echo "Stage: $STAGE"
echo "Type: $TYPE"
[ -n "$DERIVED_FROM" ] && echo "Derived from: $DERIVED_FROM"

mkdir -p "$COMPONENT_PATH"/{specs,reference,generated,analysis,docs,tests,examples}
mkdir -p "$COMPONENT_PATH/analysis"/{benchmarks,usage-patterns,feedback}

echo "Created directory structure"

cat > "$COMPONENT_PATH/meta.json" <<EOF
{
  "component": {
    "name": "$COMPONENT_NAME",
    "full_name": "Component Full Name",
    "version": "0.1.0",
    "status": "$STAGE",
    "maturity": "exploratory",
    "created": "$(date +%Y-%m-%d)",
    "last_updated": "$(date +%Y-%m-%d)"
  },
  
  "lifecycle": {
    "stage": "$STAGE",
    "promotion_history": [],
    "next_review": "TBD"
  },
  
  "classification": {
    "type": "$TYPE",
    "layer": "component-layer",
    "domain": [${DOMAIN:+"\"$(echo $DOMAIN | sed 's/,/\", \"/g')\""}]
  },
  
  "relationships": {
    "depends_on": [],
    "used_by": [],
    "integrates_with": [],
    "derived_from": ${DERIVED_FROM:+"\"$DERIVED_FROM\""}${DERIVED_FROM:-null},
    "derives": []
  },
  
  "files": {
    "specs": {
      "location": "./specs",
      "count": 0,
      "format": ["json"],
      "index": "./specs/index.json"
    },
    "reference": {
      "location": "./reference",
      "languages": [],
      "purpose": "Examples for STUNIR process",
      "note": "NOT generated code - reference implementations",
      "index": "./reference/index.json"
    },
    "generated": {
      "location": "./generated",
      "targets": [],
      "auto_generated": true,
      "do_not_edit": true
    },
    "analysis": {
      "location": "./analysis",
      "types": ["performance", "usage", "feedback"],
      "updated": "$(date +%Y-%m-%d)"
    }
  },
  
  "ai_metadata": {
    "keywords": [],
    "primary_functions": [],
    "use_cases": [],
    "complexity": "medium",
    "learning_curve": "moderate",
    "documentation_quality": "incomplete"
  },
  
  "development": {
    "active_work": true,
    "contributors": [],
    "issues_open": 0,
    "next_milestone": ""
  },
  
  "stunir": {
    "uses_stunir": false,
    "spec_to_ir": false,
    "ir_to_code": false,
    "targets": [],
    "last_generation": null
  }
}
EOF

echo "Created meta.json"

cat > "$COMPONENT_PATH/README.md" <<EOF
# $COMPONENT_NAME

**Stage**: $STAGE  
**Type**: $TYPE  
${DERIVED_FROM:+**Derived from**: $DERIVED_FROM}

## Overview

Brief description of what this component does.

## Status

This component is currently in **$STAGE** stage.

## Directory Structure

- \`specs/\` - Component specifications (STUNIR input)
- \`reference/\` - Reference implementations (examples for STUNIR)
- \`generated/\` - STUNIR-generated code (when applicable)
- \`analysis/\` - Performance analysis and feedback
- \`docs/\` - Component documentation
- \`tests/\` - Test suites
- \`examples/\` - Usage examples
- \`meta.json\` - Component metadata

## Development

To work on this component:

1. Add specifications to \`specs/\`
2. Create reference implementations in \`reference/\`
3. Document your approach in \`docs/\`
4. Add tests in \`tests/\`

## Reference vs Generated Code

- **reference/**: Hand-written examples for STUNIR (NOT generated)
- **generated/**: STUNIR output (auto-generated, DO NOT EDIT)
EOF

cp "$SCRIPT_DIR/templates/_template/specs/README.md" "$COMPONENT_PATH/specs/README.md" 2>/dev/null || echo "# Specifications" > "$COMPONENT_PATH/specs/README.md"
cp "$SCRIPT_DIR/templates/_template/reference/README.md" "$COMPONENT_PATH/reference/README.md" 2>/dev/null || echo "# Reference Implementations" > "$COMPONENT_PATH/reference/README.md"
cp "$SCRIPT_DIR/templates/_template/analysis/README.md" "$COMPONENT_PATH/analysis/README.md" 2>/dev/null || echo "# Analysis" > "$COMPONENT_PATH/analysis/README.md"
cp "$SCRIPT_DIR/templates/_template/docs/README.md" "$COMPONENT_PATH/docs/README.md" 2>/dev/null || echo "# Documentation" > "$COMPONENT_PATH/docs/README.md"

echo ""
echo "✅ Component created successfully at:"
echo "   $COMPONENT_PATH"
echo ""
echo "Next steps:"
echo "1. Update meta.json with component details"
echo "2. Add specifications to specs/"
echo "3. Create reference implementations in reference/"
echo "4. Document in docs/"
