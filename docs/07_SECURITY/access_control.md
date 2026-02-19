# HyperSync Access Control

## Authentication

### Supported Methods

#### 1. API Keys
- Static API keys for service accounts
- Keys stored securely (hashed)
- Key rotation supported
- Revocation supported

#### 2. OAuth 2.0
- Integration with OAuth providers
- Token-based authentication
- Refresh token support
- Standard OAuth flows

#### 3. Mutual TLS
- Certificate-based authentication
- Client certificates required
- Certificate validation
- Certificate revocation checking

### Authentication Flow
```
1. Client presents credentials
2. System validates credentials
3. If valid: Generate session token
4. If invalid: Return 401 Unauthorized
5. Log authentication attempt
```

## Authorization

### Role-Based Access Control (RBAC)

#### Roles
- **Admin**: Full system access
- **Operator**: Execute operations, read receipts
- **Viewer**: Read-only access
- **Service**: Programmatic access for services

#### Permissions
- `operator:execute` - Execute operators
- `operator:read` - Read operator definitions
- `policy:read` - Read policies
- `policy:write` - Modify policies
- `receipt:read` - Read receipts
- `config:read` - Read configuration
- `config:write` - Modify configuration
- `admin:*` - All administrative actions

### Authorization Flow
```
1. Authenticate user
2. Identify requested resource and action
3. Check user roles
4. Check role permissions
5. If authorized: Allow
6. If not authorized: Return 403 Forbidden
7. Log authorization decision
```

## Access Control Lists (ACLs)

### Resource-Level ACLs
- Per-operator access control
- Per-policy access control
- Per-agent access control

### ACL Format
```json
{
  "resource": "operator:op_123",
  "acl": [
    {"principal": "user:alice", "permissions": ["execute", "read"]},
    {"principal": "role:operator", "permissions": ["execute"]},
    {"principal": "role:viewer", "permissions": ["read"]}
  ]
}
```

## Session Management

### Session Lifecycle
1. **Creation**: After successful authentication
2. **Validation**: On each request
3. **Renewal**: Before expiration
4. **Expiration**: After timeout or logout
5. **Revocation**: On logout or security event

### Session Security
- Secure session tokens (cryptographically random)
- Short expiration times (configurable)
- Automatic renewal
- Revocation on suspicious activity

## Audit Logging

All access control events are logged:
- Authentication attempts (success and failure)
- Authorization decisions
- Permission changes
- Role assignments
- Session creation/expiration
- Access denials
