# Grant tools that prefer existing backends if available
try:
    from grant_backend import issue_grant as _issue_grant
except Exception:
    _issue_grant = None

try:
    from grant_backend import verify_grant as _verify_grant
except Exception:
    _verify_grant = None


def issue_grant(contract, subject, ttl=None):
    if _issue_grant is None:
        raise NotImplementedError('grant_backend.issue_grant not available')
    return _issue_grant(contract, subject, ttl=ttl)


def verify_grant(grant):
    if _verify_grant is None:
        raise NotImplementedError('grant_backend.verify_grant not available')
    return _verify_grant(grant)
