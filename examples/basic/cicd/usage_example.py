"""
Example: Using HyperSync CI/CD Pipeline System
"""

from hypersync.cicd import (
    PipelineManager,
    GoldSampleManager,
    PipelineExecutor
)
import json

# Initialize managers
pipeline_manager = PipelineManager()
gold_sample_manager = GoldSampleManager()
executor = PipelineExecutor(pipeline_manager, gold_sample_manager)

# 1. Create a pipeline
print("Creating pipeline...")
with open('simple_pipeline.json', 'r') as f:
    pipeline_def = json.load(f)

pipeline_id = pipeline_manager.create_pipeline(pipeline_def)
print(f"Created pipeline: {pipeline_id}")

# 2. Create a gold sample
print("\nCreating gold sample...")
with open('gold_sample_example.json', 'r') as f:
    sample_data = json.load(f)

sample_id = gold_sample_manager.create_sample(
    pipeline_id=pipeline_id,
    stage="test",
    data=sample_data,
    version="1.0.0"
)
print(f"Created gold sample: {sample_id}")

# 3. Execute the pipeline
print("\nExecuting pipeline...")
result = executor.execute_pipeline(
    pipeline_id,
    trigger_type="manual",
    trigger_source="example_script"
)

print(f"Pipeline status: {result['status']}")
print(f"Run ID: {result['run_id']}")
print(f"Stages completed: {len(result['stages'])}")

# 4. Validate against gold sample
print("\nValidating against gold sample...")
test_data = {
    "inputs": sample_data["inputs"],
    "outputs": {
        "response": "Paris is the capital of France.",
        "tokens_used": 13,
        "latency_ms": 150,
        "embedding": [0.125, -0.450, 0.785, 0.230, -0.570]
    },
    "metrics": {
        "accuracy": 0.97,
        "coherence": 0.94,
        "relevance": 0.96,
        "safety_score": 0.98
    }
}

passed, score, differences = gold_sample_manager.validate_against_sample(
    sample_id=sample_id,
    test_data=test_data,
    comparison_method="metric_based",
    threshold=0.90
)

print(f"Validation: {'PASSED' if passed else 'FAILED'}")
print(f"Similarity score: {score:.3f}")
if differences:
    print(f"Differences found: {len(differences)}")
    for key, diff in list(differences.items())[:3]:
        print(f"  - {key}: {diff}")

# 5. List all pipelines
print("\nListing all pipelines...")
pipelines = pipeline_manager.list_pipelines()
for p in pipelines:
    print(f"  - {p['name']} (v{p['version']})")

# 6. List all gold samples
print("\nListing gold samples...")
samples = gold_sample_manager.list_samples(pipeline_id=pipeline_id)
for s in samples:
    print(f"  - {s['sample_id'][:8]}... ({s['stage']})")

# 7. Get validation history
print("\nValidation history...")
history = gold_sample_manager.get_validation_history(sample_id)
for v in history[:5]:
    status = "✅" if v['passed'] else "❌"
    print(f"  {status} {v['timestamp']}: score={v['similarity_score']:.3f}")

print("\n✅ Example completed successfully!")
