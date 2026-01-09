"""
Tuning Stable Usage Examples

Demonstrates various ways to use the tuning stable system.
"""

from hypersync.tuning import TuningStableManager, TrainingExecutor
from hypersync.cicd import GoldSampleManager, PipelineManager
from hypersync.nvm import ModelCatalogueManager


def example_1_basic_stable():
    """Example 1: Create and manage a basic tuning stable"""
    print("=== Example 1: Basic Tuning Stable ===\n")

    manager = TuningStableManager()

    # Create stable
    stable = manager.create_stable(
        name="llama-qa-basic",
        base_model={
            "model_id": "llama-3-8b-base",
            "catalogue_entry": "llama-3-8b-base"
        },
        description="Basic QA tuning example",
        tags=["example", "qa", "llama"]
    )

    print(f"Created stable: {stable.stable_id}")
    print(f"Name: {stable.name}")
    print(f"Status: {stable.status}\n")

    # Start run
    run = manager.start_run(stable.stable_id)
    print(f"Started run: {run.run_id}")
    print(f"Status: {run.status}\n")

    # Simulate progress updates
    for epoch in range(1, 4):
        manager.update_run_progress(
            run.run_id,
            progress={
                "current_epoch": epoch,
                "total_epochs": 3,
                "percent_complete": (epoch / 3) * 100
            },
            metrics={
                "training_loss": [2.5 - (epoch * 0.2)],
                "validation_loss": [2.3 - (epoch * 0.15)]
            }
        )
        print(f"Updated progress: Epoch {epoch}/3")

    # Complete run
    manager.complete_run(run.run_id, status="completed")
    print(f"\nCompleted run: {run.run_id}")


def example_2_with_gold_samples():
    """Example 2: Tuning with gold sample validation"""
    print("\n=== Example 2: With Gold Sample Validation ===\n")

    manager = TuningStableManager()

    # Create stable with validation config
    stable = manager.create_stable(
        name="llama-qa-validated",
        base_model={
            "model_id": "llama-3-8b-base",
            "catalogue_entry": "llama-3-8b-base"
        },
        validation_config={
            "gold_sample_suite": "qa-gold-suite-v1",
            "validation_frequency": "every_epoch",
            "quality_gates": {
                "min_gold_sample_pass_rate": 0.85,
                "max_regression_tolerance": 0.05
            },
            "early_stopping": {
                "enabled": True,
                "patience": 3,
                "metric": "validation_loss"
            }
        }
    )

    print(f"Created stable with gold sample validation: {stable.stable_id}")
    print(f"Gold suite: {stable.validation_config['gold_sample_suite']}")
    print(f"Min pass rate: {stable.validation_config['quality_gates']['min_gold_sample_pass_rate']}")


def example_3_with_cicd():
    """Example 3: Tuning with CI/CD integration"""
    print("\n=== Example 3: With CI/CD Integration ===\n")

    manager = TuningStableManager()

    # Create stable with CI/CD integration
    stable = manager.create_stable(
        name="llama-qa-cicd",
        base_model={
            "model_id": "llama-3-8b-base",
            "catalogue_entry": "llama-3-8b-base"
        },
        cicd_integration={
            "pipeline_id": "deploy-qa-model-pipeline",
            "auto_trigger": True,
            "trigger_on": ["quality_gate_pass", "checkpoint"]
        }
    )

    print(f"Created stable with CI/CD integration: {stable.stable_id}")
    print(f"Pipeline: {stable.cicd_integration['pipeline_id']}")
    print(f"Auto-trigger: {stable.cicd_integration['auto_trigger']}")


def example_4_checkpoint_management():
    """Example 4: Checkpoint management"""
    print("\n=== Example 4: Checkpoint Management ===\n")

    manager = TuningStableManager()

    # Create stable
    stable = manager.create_stable(
        name="llama-qa-checkpoints",
        base_model={
            "model_id": "llama-3-8b-base",
            "catalogue_entry": "llama-3-8b-base"
        },
        checkpoint_config={
            "save_frequency": "every_epoch",
            "keep_best_n": 3,
            "keep_last_n": 2,
            "auto_catalogue": True
        }
    )

    # Start run
    run = manager.start_run(stable.stable_id)

    # Save checkpoints
    for epoch in range(1, 4):
        checkpoint_id = manager.save_checkpoint(
            run_id=run.run_id,
            stable_id=stable.stable_id,
            epoch=epoch,
            step=epoch * 1000,
            path=f"/checkpoints/{stable.stable_id}/epoch_{epoch}",
            metrics={"loss": 2.5 - (epoch * 0.2)},
            is_best=(epoch == 2)  # Epoch 2 is best
        )
        print(f"Saved checkpoint: {checkpoint_id} (epoch {epoch})")

    # List checkpoints
    checkpoints = manager.get_checkpoints(stable_id=stable.stable_id)
    print(f"\nTotal checkpoints: {len(checkpoints)}")

    # Get best checkpoint
    best_checkpoints = manager.get_checkpoints(stable_id=stable.stable_id, best_only=True)
    if best_checkpoints:
        print(f"Best checkpoint: {best_checkpoints[0]['checkpoint_id']} (epoch {best_checkpoints[0]['epoch']})")


def example_5_training_executor():
    """Example 5: Using the training executor"""
    print("\n=== Example 5: Training Executor ===\n")

    manager = TuningStableManager()
    executor = TrainingExecutor(manager)

    # Create stable
    stable = manager.create_stable(
        name="llama-qa-executor",
        base_model={
            "model_id": "llama-3-8b-base",
            "catalogue_entry": "llama-3-8b-base"
        }
    )

    # Define training functions
    def train_epoch(epoch, config):
        print(f"  Training epoch {epoch}...")
        return {
            "loss": 2.5 - (epoch * 0.2),
            "lr": config.get('hyperparameters', {}).get('learning_rate', 2e-4),
            "step": epoch * 1000,
            "total_steps": 3000,
            "samples_processed": epoch * 10000
        }

    def validate(model, config):
        print(f"  Validating...")
        return {
            "loss": 2.3,
            "perplexity": 10.5,
            "accuracy": 0.85
        }

    def save_checkpoint(model, path):
        print(f"  Saving checkpoint to {path}...")

    # Define callbacks
    callbacks = {
        'on_run_start': lambda run, stable: print(f"Starting run {run.run_id}"),
        'on_epoch_start': lambda epoch, run, stable: print(f"\nEpoch {epoch}:"),
        'on_epoch_end': lambda epoch, metrics, run, stable: print(f"  Completed with loss: {metrics['loss']:.3f}"),
        'on_run_complete': lambda run, stable: print(f"\nRun completed: {run.run_id}")
    }

    # Execute run
    run_id = executor.execute_run(
        stable_id=stable.stable_id,
        train_fn=train_epoch,
        validate_fn=validate,
        checkpoint_fn=save_checkpoint,
        callbacks=callbacks
    )

    print(f"\nFinal run ID: {run_id}")


def example_6_list_and_query():
    """Example 6: Listing and querying stables"""
    print("\n=== Example 6: Listing and Querying ===\n")

    manager = TuningStableManager()

    # List all stables
    all_stables = manager.list_stables(limit=10)
    print(f"Total stables: {len(all_stables)}")

    # List by status
    running_stables = manager.list_stables(status="running")
    print(f"Running stables: {len(running_stables)}")

    # List by tags
    qa_stables = manager.list_stables(tags=["qa"])
    print(f"QA stables: {len(qa_stables)}")

    # List runs
    all_runs = manager.list_runs(limit=10)
    print(f"\nTotal runs: {len(all_runs)}")

    # List completed runs
    completed_runs = manager.list_runs(status="completed")
    print(f"Completed runs: {len(completed_runs)}")


if __name__ == "__main__":
    # Run examples
    example_1_basic_stable()
    example_2_with_gold_samples()
    example_3_with_cicd()
    example_4_checkpoint_management()
    example_5_training_executor()
    example_6_list_and_query()

    print("\n=== All Examples Complete ===")
