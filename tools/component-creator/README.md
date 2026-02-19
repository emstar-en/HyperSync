# Component Creator Tool

Scaffolding tool for creating new HyperSync components.

## Usage

### Windows
```batch
cd tools\component-creator
create-component.bat --name <component-name> --stage <stage> [OPTIONS]
```

### Linux/Mac
```bash
cd tools/component-creator
./create-component.sh --name <component-name> --stage <stage> [OPTIONS]
```

## Required Arguments

- `--name NAME` - Component name (lowercase, hyphen-separated, e.g., `geometric-quantum`)
- `--stage STAGE` - Lifecycle stage: `experimental`, `stable`, or `production`

## Optional Arguments

- `--derived-from PARENT` - Parent component this derives from (e.g., `agua`)
- `--type TYPE` - Component type: `foundation`, `runtime`, `extension`, or `tool` (default: `extension`)
- `--domain DOMAINS` - Comma-separated domain keywords (e.g., `geometry,manifolds`)

## Examples

### Create experimental component
```bash
./create-component.sh \
  --name geometric-quantum \
  --stage experimental \
  --derived-from agua \
  --type extension \
  --domain "geometry,quantum"
```

### Create stable component
```bash
./create-component.sh \
  --name workflow-optimizer \
  --stage stable \
  --type tool \
  --domain "optimization,workflow"
```

## What Gets Created

```
components/<stage>/<component-name>/
├── specs/              # STUNIR specifications
│   └── README.md
├── reference/          # Reference implementations (NOT generated)
│   └── README.md
├── generated/          # STUNIR output (auto-generated)
├── analysis/           # Performance & usage analysis
│   ├── benchmarks/
│   ├── usage-patterns/
│   ├── feedback/
│   └── README.md
├── docs/               # Component documentation
│   └── README.md
├── tests/              # Test suites
├── examples/           # Usage examples
├── meta.json           # Component metadata
└── README.md           # Component overview
```

## Component Metadata

The tool creates `meta.json` with:
- Component identification (name, version, status)
- Lifecycle tracking (stage, promotion history)
- Classification (type, layer, domain)
- Relationships (dependencies, derivations)
- File organization (specs, reference, generated, etc.)
- AI metadata (keywords, functions, use cases)
- Development info (contributors, milestones)
- STUNIR configuration

## After Creation

1. **Update `meta.json`** - Fill in component details, keywords, and functions
2. **Add specifications** - Create STUNIR specs in `specs/`
3. **Create references** - Add example implementations in `reference/`
4. **Document** - Write documentation in `docs/`
5. **Test** - Add tests in `tests/`

## Component Lifecycle

- **experimental** → **stable** → **production**

Promotion criteria:
- experimental → stable: Complete specs, reference implementations, documentation
- stable → production: Validated specs, tested implementations, complete docs
