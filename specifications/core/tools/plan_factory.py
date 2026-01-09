import json, hashlib, argparse, pathlib, time

        def sha256_bytes(b: bytes) -> str:
            return hashlib.sha256(b).hexdigest()

        def load(p):
            return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))

        def main():
            ap = argparse.ArgumentParser()
            
            add_common_args(ap)
ap.add_argument("--model", required=True)
            ap.add_argument("--spec", required=True)
            ap.add_argument("--out", required=True)
            args = ap.parse_args()

            
            _envelope_op = load_envelope_op(args)
out_dir = pathlib.Path(args.out)
            out_dir.mkdir(parents=True, exist_ok=True)

            model = load(args.model)
            spec = load(args.spec)
            latency = model.get("latency_ms_budget", 250)
            mm = spec["memory"]["micro_mem_array"]
            kv = spec["memory"]["kv_policy"]
            if latency <= 200:
                mm["quantization"] = "int8"
                kv["caps"]["summary"] = min(3, kv["caps"].get("summary", 3))
                kv["ttl_ms"]["summary"] = min(900000, kv["ttl_ms"].get("summary", 1800000))

            bundle = {
                "id": "promotion_bundle",
                "version": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "model_profile": model,
                "factory_spec": spec,
                "router": {
                    "domains": spec["manifold"]["domains"],
                    "canonical": spec["manifold"]["canonical"],
                    "numeric_policy_version": "v1",
                    "kpi_profile": "B_performance_gated"
                },
                "memory_plan": {"kv_policy": kv, "micro_mem_array": mm},
                "storage_plan": spec["storage"],
                "policy": spec["policy"],
                "observability": spec["observability"]
            }

            b = json.dumps(bundle, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            rid = sha256_bytes(b)

            (out_dir/"promotion_bundle.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False)+"
", encoding="utf-8")
            (out_dir/"receipt.json").write_text(json.dumps({
                "receipt_id": rid,
                "hash": f"sha256:{rid}",
                "numeric_policy_version": "v1",
                "state_version": "factory-v1",
                "logical_time": int(time.time()*1000)
            }, indent=2)+"
", encoding="utf-8")
            print(rid)

        if __name__ == "__main__":
            main()
