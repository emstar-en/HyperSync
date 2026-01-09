import json, sys

def loadj(p):
    with open(p,'r',encoding='utf-8') as f: return json.load(f)

def ensure(cond, msg):
    if not cond:
        print(json.dumps({'ok': False, 'error': msg})); sys.exit(1)

def main():
    pol = loadj(sys.argv[1]) if len(sys.argv) > 1 else {
      'typed_fields_only': True,
      'dp_epsilon': 1.0,
      'rate_limits': {'max_events_per_min': 600},
      'volume_caps': {'max_bytes_per_window': 10_000_000, 'window_minutes': 10}
    }
    ensure(pol['typed_fields_only'] is True, 'typed_fields_only must be True')
    ensure(0.1 <= float(pol['dp_epsilon']) <= 10, 'dp_epsilon out of bounds')
    rl = pol['rate_limits']['max_events_per_min']
    ensure(isinstance(rl, int) and rl >= 1, 'rate limit invalid')
    vc = pol['volume_caps']
    ensure(vc['max_bytes_per_window'] >= 1024, 'volume cap too low')
    ensure(1 <= vc['window_minutes'] <= 1440, 'window window invalid')
    print(json.dumps({'ok': True, 'checked': ['typed_fields_only','dp_epsilon','rate_limits','volume_caps']}))

if __name__ == '__main__':
    main()
