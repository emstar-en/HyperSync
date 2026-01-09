#!/usr/bin/env python3
"""Audit CLI"""
import sys, json, argparse
sys.path.insert(0, '../../')
from api.audit.get_logs import api_get_audit_logs

def main():
    parser = argparse.ArgumentParser(description='Get audit logs')
    parser.add_argument('tier', help='Service tier')
    parser.add_argument('--range', default='24h', help='Time range')
    parser.add_argument('--action', help='Filter by action')
    parser.add_argument('--user', help='Filter by user')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    result = api_get_audit_logs(args.tier, args.range, args.action, args.user)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nAudit Logs ({result['count']}):")
        for log in result['logs']:
            print(f"  [{log['timestamp']}] {log['user']}: {log['action']} - {log['status']}")

if __name__ == '__main__':
    main()
