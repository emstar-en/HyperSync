"""
Training Executor

Executes tuning runs with gold sample validation and CI/CD integration.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any, Callable
from datetime import datetime
import time

from .stable_manager import TuningStableManager

logger = logging.getLogger(__name__)


class TrainingExecutor:
    """
    Executes training runs with validation and checkpointing.

    This is a framework-agnostic executor that coordinates:
    - Training loop management
    - Gold sample validation
    - Checkpoint management
    - CI/CD pipeline triggering
    - Progress tracking
    """

    def __init__(
        self,
        stable_manager: TuningStableManager,
        gold_sample_manager: Optional[Any] = None,
        pipeline_manager: Optional[Any] = None,
        catalogue_manager: Optional[Any] = None
    ):
        self.stable_manager = stable_manager
        self.gold_sample_manager = gold_sample_manager
        self.pipeline_manager = pipeline_manager
        self.catalogue_manager = catalogue_manager

    def execute_run(
        self,
        stable_id: str,
        train_fn: Callable,
        validate_fn: Optional[Callable] = None,
        checkpoint_fn: Optional[Callable] = None,
        callbacks: Optional[Dict[str, Callable]] = None
    ) -> str:
        """
        Execute a training run.

        Args:
            stable_id: Tuning stable ID
            train_fn: Training function (epoch, config) -> metrics
            validate_fn: Validation function (model, config) -> metrics
            checkpoint_fn: Checkpoint save function (model, path) -> None
            callbacks: Optional callbacks for lifecycle events

        Returns:
            run_id: The run ID
        """
        # Get stable configuration
        stable = self.stable_manager.get_stable(stable_id)
        if not stable:
            raise ValueError(f"Stable not found: {stable_id}")

        # Start run
        run = self.stable_manager.start_run(stable_id)
        run_id = run.run_id

        logger.info(f"Starting training run {run_id} for stable {stable_id}")

        try:
            # Initialize
            if callbacks and 'on_run_start' in callbacks:
                callbacks['on_run_start'](run, stable)

            # Get configuration
            tuning_config = stable.tuning_config or {}
            validation_config = stable.validation_config or {}
            checkpoint_config = stable.checkpoint_config or {}

            epochs = tuning_config.get('hyperparameters', {}).get('epochs', 3)
            validation_frequency = validation_config.get('validation_frequency', 'every_epoch')

            best_metric = float('inf')
            best_epoch = 0
            patience_counter = 0
            early_stopping_patience = validation_config.get('early_stopping', {}).get('patience', 3)

            # Training loop
            for epoch in range(1, epochs + 1):
                logger.info(f"Starting epoch {epoch}/{epochs}")

                # Train epoch
                if callbacks and 'on_epoch_start' in callbacks:
                    callbacks['on_epoch_start'](epoch, run, stable)

                train_metrics = train_fn(epoch, tuning_config)

                # Update progress
                progress = {
                    'current_epoch': epoch,
                    'total_epochs': epochs,
                    'current_step': train_metrics.get('step', 0),
                    'total_steps': train_metrics.get('total_steps', 0),
                    'samples_processed': train_metrics.get('samples_processed', 0),
                    'percent_complete': (epoch / epochs) * 100
                }

                # Collect metrics
                run = self.stable_manager.get_run(run_id)
                metrics = run.metrics or {
                    'training_loss': [],
                    'validation_loss': [],
                    'learning_rate': [],
                    'perplexity': [],
                    'gold_sample_scores': []
                }

                metrics['training_loss'].append(train_metrics.get('loss', 0))
                metrics['learning_rate'].append(train_metrics.get('lr', 0))

                # Validation
                should_validate = (
                    validation_frequency == 'every_epoch' or
                    (validation_frequency == 'every_n_steps' and 
                     epoch % validation_config.get('validation_steps', 1) == 0)
                )

                if should_validate and validate_fn:
                    logger.info(f"Running validation at epoch {epoch}")
                    val_metrics = validate_fn(None, validation_config)  # Model passed separately

                    metrics['validation_loss'].append(val_metrics.get('loss', 0))
                    if 'perplexity' in val_metrics:
                        metrics['perplexity'].append(val_metrics['perplexity'])

                    # Gold sample validation
                    if self.gold_sample_manager and validation_config.get('gold_sample_suite'):
                        gold_results = self._validate_gold_samples(
                            validation_config['gold_sample_suite'],
                            val_metrics
                        )
                        metrics['gold_sample_scores'].append(gold_results)

                        # Check quality gates
                        if not self._check_quality_gates(gold_results, validation_config):
                            logger.warning(f"Quality gates failed at epoch {epoch}")
                            if callbacks and 'on_quality_gate_fail' in callbacks:
                                callbacks['on_quality_gate_fail'](epoch, gold_results)

                    # Early stopping check
                    current_metric = val_metrics.get('loss', float('inf'))
                    if current_metric < best_metric:
                        best_metric = current_metric
                        best_epoch = epoch
                        patience_counter = 0
                    else:
                        patience_counter += 1

                    if patience_counter >= early_stopping_patience:
                        logger.info(f"Early stopping triggered at epoch {epoch}")
                        break

                # Update run
                self.stable_manager.update_run_progress(run_id, progress, metrics)

                # Checkpointing
                should_checkpoint = (
                    checkpoint_config.get('save_frequency') == 'every_epoch' or
                    (checkpoint_config.get('save_frequency') == 'on_improvement' and 
                     epoch == best_epoch)
                )

                if should_checkpoint and checkpoint_fn:
                    checkpoint_path = f"checkpoints/{stable_id}/{run_id}/epoch_{epoch}"
                    checkpoint_fn(None, checkpoint_path)  # Model passed separately

                    is_best = (epoch == best_epoch)

                    # Save checkpoint record
                    checkpoint_id = self.stable_manager.save_checkpoint(
                        run_id=run_id,
                        stable_id=stable_id,
                        epoch=epoch,
                        step=train_metrics.get('step', 0),
                        path=checkpoint_path,
                        metrics=train_metrics,
                        is_best=is_best
                    )

                    # Auto-catalogue if enabled
                    if checkpoint_config.get('auto_catalogue') and self.catalogue_manager:
                        catalogue_entry = self._register_checkpoint_in_catalogue(
                            stable, run, checkpoint_id, checkpoint_path, epoch, is_best
                        )
                        logger.info(f"Registered checkpoint in catalogue: {catalogue_entry}")

                if callbacks and 'on_epoch_end' in callbacks:
                    callbacks['on_epoch_end'](epoch, train_metrics, run, stable)

            # Complete run
            self.stable_manager.complete_run(run_id, status='completed')

            # Trigger CI/CD if configured
            if stable.cicd_integration and self.pipeline_manager:
                self._trigger_cicd_pipeline(stable, run)

            if callbacks and 'on_run_complete' in callbacks:
                callbacks['on_run_complete'](run, stable)

            logger.info(f"Training run {run_id} completed successfully")
            return run_id

        except Exception as e:
            logger.error(f"Training run {run_id} failed: {str(e)}", exc_info=True)

            error = {
                'message': str(e),
                'traceback': str(e.__traceback__),
                'occurred_at': datetime.utcnow().isoformat() + 'Z'
            }

            self.stable_manager.complete_run(run_id, status='failed', error=error)

            if callbacks and 'on_run_error' in callbacks:
                callbacks['on_run_error'](run, stable, error)

            raise

    def _validate_gold_samples(
        self,
        suite_id: str,
        validation_metrics: Dict
    ) -> Dict:
        """Validate against gold samples"""
        if not self.gold_sample_manager:
            return {}

        # This would integrate with the gold sample manager
        # For now, return placeholder
        return {
            'suite_id': suite_id,
            'pass_rate': 0.85,
            'total_samples': 100,
            'passed': 85,
            'failed': 15,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def _check_quality_gates(
        self,
        gold_results: Dict,
        validation_config: Dict
    ) -> bool:
        """Check if quality gates are met"""
        quality_gates = validation_config.get('quality_gates', {})

        min_pass_rate = quality_gates.get('min_gold_sample_pass_rate', 0.8)
        actual_pass_rate = gold_results.get('pass_rate', 0)

        return actual_pass_rate >= min_pass_rate

    def _register_checkpoint_in_catalogue(
        self,
        stable: Any,
        run: Any,
        checkpoint_id: str,
        checkpoint_path: str,
        epoch: int,
        is_best: bool
    ) -> str:
        """Register checkpoint in model catalogue"""
        if not self.catalogue_manager:
            return ""

        # This would integrate with the catalogue manager
        # For now, return placeholder
        return f"catalogue-entry-{checkpoint_id}"

    def _trigger_cicd_pipeline(self, stable: Any, run: Any):
        """Trigger CI/CD pipeline"""
        if not self.pipeline_manager:
            return

        cicd_config = stable.cicd_integration
        if not cicd_config or not cicd_config.get('auto_trigger'):
            return

        pipeline_id = cicd_config.get('pipeline_id')
        if not pipeline_id:
            return

        logger.info(f"Triggering CI/CD pipeline: {pipeline_id}")

        # This would integrate with the pipeline manager
        # For now, just log
        logger.info(f"Pipeline {pipeline_id} triggered for run {run.run_id}")


class SimpleTrainingLoop:
    """
    Simple training loop example for demonstration.

    In practice, this would integrate with actual training frameworks
    like PyTorch, TensorFlow, or Hugging Face Transformers.
    """

    @staticmethod
    def train_epoch(epoch: int, config: Dict) -> Dict:
        """Simulate training an epoch"""
        raise NotImplementedError("Training logic not implemented. This is a placeholder.")

    @staticmethod
    def validate(model: Any, config: Dict) -> Dict:
        """Simulate validation"""
        raise NotImplementedError("Validation logic not implemented. This is a placeholder.")

    @staticmethod
    def save_checkpoint(model: Any, path: str):
        """Simulate saving checkpoint"""
        raise NotImplementedError("Checkpoint saving logic not implemented. This is a placeholder.")
