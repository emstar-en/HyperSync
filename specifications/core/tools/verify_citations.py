import json, sys

def verify_citations(answer: str, citations, passages, addresses):
    # Simple heuristic: require every citation to reference an address we know
    # and that at least one passage shares a 10-char overlap with the answer
    addr_set = set(addresses)
    if not citations: return False
    for c in citations:
        if c not in addr_set:
            return False
    if not passages:
        return False
    ok_overlap = any(any(tok in answer for tok in [p[:10]]) for p in passages)
    return ok_overlap

def main():
    ex = json.loads(sys.stdin.read())
    ok = verify_citations(ex['output']['answer'], ex['output']['citations'], ex['input']['passages'], ex['meta'].get('addresses', []))
    print(json.dumps({'ok': bool(ok)}))

if __name__ == '__main__':
    main()
