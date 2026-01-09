# ECC tools that prefer existing backends if available
try:
    from ecc_backend import validate_contract as _validate_contract
except Exception:
    _validate_contract = None

try:
    from ecc_backend import contract_digest as _contract_digest
except Exception:
    _contract_digest = None


def validate_contract(contract):
    if _validate_contract is None:
        raise NotImplementedError('ecc_backend.validate_contract not available')
    return _validate_contract(contract)


def contract_digest(contract):
    if _contract_digest is None:
        raise NotImplementedError('ecc_backend.contract_digest not available')
    return _contract_digest(contract)
