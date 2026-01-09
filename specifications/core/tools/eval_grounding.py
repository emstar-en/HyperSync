import json, argparse

def eval_file(path):
    total = 0; prec_num=0; prec_den=0; rec_num=0; rec_den=0
    for line in open(path,'r',encoding='utf-8'):
        if not line.strip(): continue
        ex = json.loads(line)
        total += 1
        cits = set(ex['output'].get('citations', []))
        addrs = set(ex['meta'].get('addresses', []))
        if not addrs:
            continue
        # precision: cited addresses that are actually in addresses
        prec_num += len(cits & addrs)
        prec_den += len(cits) if cits else 1
        # recall: among the top-1 selected, we recall at least one
        rec_num += 1 if (cits & addrs) else 0
        rec_den += 1
    prec = (prec_num/prec_den) if prec_den else 0.0
    rec = (rec_num/rec_den) if rec_den else 0.0
    return {'total': total, 'citation_precision': round(prec,4), 'citation_recall': round(rec,4)}

def main():
    ap = argparse.ArgumentParser()
    add_common_args(ap)
; ap.add_argument('--infile', required=True)
    args = ap.parse_args()
    
    _envelope_op = load_envelope_op(args)
print(json.dumps(eval_file(args.infile)))

if __name__ == '__main__':
    main()
