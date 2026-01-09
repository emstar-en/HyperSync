import json
import os
import glob
from agents.policy_governance.agent import PolicyGovernanceAgent

def run_conformance_tests():
    agent = PolicyGovernanceAgent()

    # Path to vectors (adjust as needed for the environment)
    # Updated to reflect new structure
    vector_path = "tests/conformance/vectors/**/*.json"
    vectors = glob.glob(vector_path, recursive=True)

    print(f"Found {len(vectors)} conformance vectors.")

    passed = 0
    failed = 0

    for v_path in vectors:
        try:
            with open(v_path, "r") as f:
                vector = json.load(f)

            result = agent.evaluate_vector(vector)

            if result["gate_outcome"] == result["expected"]:
                # print(f"[PASS] {result['vector_id']}")
                passed += 1
            else:
                # print(f"[FAIL] {result['vector_id']} - Expected {result['expected']}, got {result['gate_outcome']}")
                failed += 1
        except Exception as e:
            print(f"Error processing {v_path}: {e}")

    print(f"\nConformance Test Results:")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if passed + failed > 0:
        print(f"Success Rate: {passed / (passed + failed) * 100:.2f}%")
    else:
        print("No tests run.")

if __name__ == "__main__":
    run_conformance_tests()
