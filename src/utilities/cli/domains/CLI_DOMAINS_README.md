# Domain Management CLI

Command-line interface for managing HyperSync domains.

## Commands

### 1. List Domains

```bash
python3 list.py <tier> [--type TYPE] [--status STATUS] [--metadata] [--json]
```

**Examples:**
```bash
# List all domains for PRO tier
python3 list.py PRO

# List only hyperbolic domains
python3 list.py PRO --type hyperbolic

# List with metadata
python3 list.py Advanced --metadata

# Output as JSON
python3 list.py PRO --json
```

---

### 2. Get Domain Info

```bash
python3 info.py <domain_id> <tier> [--metrics] [--config] [--json]
```

**Examples:**
```bash
# Get basic domain info
python3 info.py domain-001 PRO

# Include metrics and configuration
python3 info.py domain-001 PRO --metrics --config

# Output as JSON
python3 info.py domain-001 PRO --json
```

---

### 3. Create Domain

```bash
python3 create.py <name> <type> <dimension> <tier> [--description DESC] [--config JSON] [--json]
```

**Examples:**
```bash
# Create a 3D Euclidean domain
python3 create.py my-euclidean euclidean 3 PRO

# Create with description
python3 create.py my-space hyperbolic 2 PRO --description "Custom Poincaré disk"

# Create with custom configuration
python3 create.py my-space hyperbolic 2 PRO --config '{"boundary_epsilon": 1e-7}'
```

---

### 4. Update Domain

```bash
python3 update.py <domain_id> <tier> [--name NAME] [--description DESC] [--status STATUS] [--config JSON] [--json]
```

**Examples:**
```bash
# Update description
python3 update.py domain-001 PRO --description "Updated description"

# Change status
python3 update.py domain-001 PRO --status maintenance

# Update configuration
python3 update.py domain-001 PRO --config '{"precision": "float128"}'
```

---

### 5. Delete Domain

```bash
python3 delete.py <domain_id> <tier> [--force] [--yes] [--json]
```

**Examples:**
```bash
# Delete with confirmation
python3 delete.py domain-001 PRO

# Delete without confirmation
python3 delete.py domain-001 PRO --yes

# Force delete even with active operations
python3 delete.py domain-001 PRO --force --yes
```

---

### 6. Validate Domain Configuration

```bash
python3 validate.py <type> <dimension> <tier> --config JSON [--json]
```

**Examples:**
```bash
# Validate configuration
python3 validate.py hyperbolic 2 PRO --config '{"boundary_epsilon": 1e-6}'

# Validate with JSON output
python3 validate.py lorentzian 4 Advanced --config '{"signature": "(-,+,+,+)"}' --json
```

---

## Common Options

- `--json`: Output results as JSON instead of formatted text
- `--help`: Show help for any command

## Service Tiers

- **CORE**: 5 domains max, dimensions ≤ 3
- **Basic**: 10 domains max, dimensions ≤ 5
- **PRO**: 25 domains max, dimensions ≤ 10
- **Advanced**: Unlimited domains and dimensions
- **QM Venture/Campaign/Imperium**: All features unlocked

## Domain Types

- `euclidean`: Standard Euclidean space
- `hyperbolic`: Hyperbolic space (Poincaré model)
- `spherical`: Spherical space (n-sphere)
- `lorentzian`: Lorentzian manifold (spacetime)
- `product`: Product of multiple domains

## Exit Codes

- `0`: Success
- `1`: Error (check stderr for details)
