import json, sys

def loadj(p):
    with open(p,'r',encoding='utf-8') as f: return json.load(f)

def ensure(cond, msg):
    if not cond:
        print(json.dumps({'ok': False, 'error': msg})); sys.exit(1)

def main():
    cap = loadj(sys.argv[1]) if len(sys.argv) > 1 else {
      'id': 'cap-test',
      'purpose': 'regulatory_audit',
      'selectors': {'domains': ['law'], 'time_window': {'start':'2025-10-28T00:00:00Z','end':'2025-10-30T00:00:00Z'}},
      'capture': {'include':['prompt','response'], 'exclude':['raw_distances'], 'redaction':{'pii':'mask'}, 'max_snippet_chars': 2048},
      'retention': {'days': 7, 'worm': True},
      'crypto': {'encryption':'xchacha20-poly1305', 'key_scheme':'t-of-n-threshold', 'escrow_signers':['ciso','counsel'], 't':2, 'n':2},
      'approvals': [{'role':'ciso','sig':'sig1'},{'role':'counsel','sig':'sig2'}],
      'enclave_measurement': 'MRENCLAVE:deadbeef',
      'auditability': {'log_to_ledger': True, 'emit_nhr': True}
    }
    ensure(len(cap.get('approvals',[])) >= 2, 'need >=2 approvals (multi-sig)')
    ensure(set(cap['capture']['exclude']).issuperset({'raw_distances'}), 'raw_distances must be excluded')
    ensure(cap['capture']['max_snippet_chars'] <= 20000, 'snippet size too large')
    print(json.dumps({'ok': True, 'checked': ['approvals','exclusions','snippet_limit']}))

if __name__ == '__main__':
    main()
