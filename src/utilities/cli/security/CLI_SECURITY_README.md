# Security Policy CLI

Command-line interface for managing security policies.

## Commands

```bash
python3 list.py <tier> [--category CAT] [--status STATUS]
python3 info.py <policy_id> <tier> [--config]
python3 create.py <name> <category> <tier> [--description DESC] [--level LEVEL]
python3 update.py <policy_id> <tier> [--name NAME] [--status STATUS]
python3 delete.py <policy_id> <tier> [--force] [--yes]
```
