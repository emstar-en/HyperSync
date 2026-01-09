# Policy Template

## Policy Information

**Policy ID**: POL-{id} 
**Policy Name**: {name} 
**Version**: {version} 
**Effective Date**: {date}

## Scope

**Applies To**: {scope} 
**Namespaces**: {namespaces} 
**Resource Types**: {resource_types}

## Policy Rules

### Resource Limits

```yaml
resources:
 cpu:
 min: {cpu_min}
 max: {cpu_max}
 memory:
 min: {memory_min}
 max: {memory_max}
 tokens:
 max: {token_max}
```

### Governance

```yaml
governance:
 require_approval: {require_approval}
 approvers: {approvers}
 timeout: {timeout}
```

### Budget

```yaml
budget:
 token_limit: {token_limit}
 cost_limit: {cost_limit}
 enforcement: {enforcement}
```

## Exceptions

{exceptions}

## Enforcement

**Enforcement Mode**: {mode} 
**Violation Action**: {action}

## Review Schedule

**Review Frequency**: {frequency} 
**Next Review**: {next_review}
