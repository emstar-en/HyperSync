# Attestation Management CLI

Command-line interface for managing HyperSync attestation policies.

## Commands

### 1. List Policies
```bash
python3 list.py <tier> [--type TYPE] [--status STATUS] [--json]
```

### 2. Get Policy Info
```bash
python3 info.py <policy_id> <tier> [--rules] [--json]
```

### 3. Create Policy
```bash
python3 create.py <name> <type> <tier> [--description DESC] [--requirements REQ1,REQ2] [--json]
```

### 4. Update Policy
```bash
python3 update.py <policy_id> <tier> [--name NAME] [--description DESC] [--status STATUS] [--json]
```

### 5. Delete Policy
```bash
python3 delete.py <policy_id> <tier> [--force] [--yes] [--json]
```

### 6. Validate Attestation
```bash
python3 validate.py <policy_id> <tier> --data JSON [--json]
```

## Examples

```bash
# List all policies
python3 list.py PRO

# Create strict policy
python3 create.py my-strict-policy strict PRO --description "Production policy"

# Validate attestation
python3 validate.py policy-001 PRO --data '{"signature": "...", "tpm": "..."}'
```
