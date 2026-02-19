# Experimental Component Template

This is a template for creating new experimental components in HyperSync.

## Quick Start

1. Copy this template directory to create a new component:
   ```bash
   cp -r components/experimental/_template components/experimental/your-component-name
   ```

2. Update `meta.json` with your component details

3. Add specifications to `specs/`

4. Create reference implementations in `reference/`

5. Document your approach in `docs/`

## Directory Structure

- `specs/` - Component specifications (STUNIR input)
- `reference/` - Reference implementations (examples for STUNIR, NOT generated code)
- `analysis/` - Performance analysis and feedback
- `docs/` - Component documentation
- `meta.json` - Component metadata

## Promotion Criteria

To promote from experimental → stable:
- ✅ Has complete specs
- ✅ Has reference implementations
- ✅ Initial analysis shows promise
- ✅ Documentation exists

## Notes

- Reference code in `reference/` is for examples only
- These are NOT generated files
- STUNIR uses these as inspiration for actual code generation
