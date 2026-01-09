import argparse, json, pathlib, time, hashlib, os
try:
    from cli_common import add_common_args, load_envelope_op
except Exception:
    def add_common_args(ap):
        return ap
    def load_envelope_op(args):
        return None


    def h(s: bytes) -> str:
        return hashlib.sha256(s).hexdigest()

    def now_iso():
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def loadj(p): return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))

    def redact(text: str, mode: str) -> str:
        if mode == "mask":
            return "".join("*" if c.isalnum() else c for c in text)
        if mode in ("hash","drop"):
            return f"hash:{h(text.encode())}" if mode=="hash" else ""
        return text

    def main():
        ap = argparse.ArgumentParser()
        ap.add_argument("--capsule", required=True)
        ap.add_argument("--policy", required=True)
        ap.add_argument("--inflight", required=True)
        ap.add_argument("--out_vault", required=True)
        args = ap.parse_args()

        cap = loadj(args.capsule)
        pol = loadj(args.policy)
        out = pathlib.Path(args.out_vault)
        out.mkdir(parents=True, exist_ok=True)

        include = set(cap["capture"]["include"])
        red = cap["capture"]["redaction"]
        max_chars = cap["capture"]["max_snippet_chars"]

        kept = 0
        with open(args.inflight, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                ev = json.loads(line)
                ts = ev.get("ts")
                dom = ev.get("domain_id")
                if dom not in cap["selectors"]["domains"]:
                    continue
                rec = {
                    "ts": ts,
                    "domain_id": dom,
                    "actor": ev.get("actor_pseudonym",""),
                    "policy_predicates": ev.get("policy_predicates",[]) if "policy_predicates" in include else [],
                    "tool_invocations": ev.get("tool_invocations",[]) if "tool_invocations" in include else []
                }
                if "prompt" in include:
                    rec["prompt"] = redact(ev.get("prompt","")[:max_chars], red.get("pii","mask"))
                if "response" in include:
                    rec["response"] = redact(ev.get("response","")[:max_chars], red.get("pii","mask"))
                if "citations" in include:
                    rec["citations"] = ev.get("citations", [])[:3]
                rid = h(json.dumps(rec, sort_keys=True, separators=(",",":")).encode())
                (out / f"rec-{rid}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2)+"
", encoding='utf-8')
                kept += 1

        receipt = {
            "capsule_id": cap["id"],
            "purpose": cap["purpose"],
            "time": now_iso(),
            "kept_records": kept,
            "selectors_hash": h(json.dumps(cap["selectors"], sort_keys=True).encode()),
            "policy_hash": h(json.dumps(pol, sort_keys=True).encode()),
            "enclave_measurement": cap["enclave_measurement"],
            "bundle_hash": h(("".join(sorted(os.listdir(out)))).encode())
        }
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2)+"
", encoding='utf-8')
        print(json.dumps({"kept": kept, "receipt": str(out / "receipt.json")}))

    if __name__ == "__main__":
        main()
