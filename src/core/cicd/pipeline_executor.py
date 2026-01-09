"""
HyperSync CI/CD Pipeline Executor

Executes pipeline stages and manages workflow.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from .pipeline_manager import PipelineManager, PipelineStatus, StageType
from .gold_sample_manager import GoldSampleManager


class PipelineExecutor:
    """Executes CI/CD pipelines."""

    def __init__(self, pipeline_manager: PipelineManager, 
                 gold_sample_manager: GoldSampleManager):
        self.pipeline_manager = pipeline_manager
        self.gold_sample_manager = gold_sample_manager
        self.current_run_id = None
        self.current_run_data = None

    def execute_pipeline(self, pipeline_id: str, trigger_type: str = "manual",
                        trigger_source: str = "user") -> Dict[str, Any]:
        """Execute a complete pipeline."""
        # Get pipeline definition
        pipeline = self.pipeline_manager.get_pipeline(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        # Start run
        run_id = self.pipeline_manager.start_run(pipeline_id, trigger_type, trigger_source)
        self.current_run_id = run_id

        print(f"🚀 Starting pipeline run: {run_id}")
        print(f"   Pipeline: {pipeline['name']} v{pipeline['version']}")

        # Initialize run data
        self.current_run_data = {
            'run_id': run_id,
            'pipeline_id': pipeline_id,
            'status': PipelineStatus.RUNNING.value,
            'started_at': datetime.utcnow().isoformat(),
            'stages': [],
            'artifacts': [],
            'gold_samples_collected': [],
            'gold_sample_validations': [],
            'logs': []
        }

        # Update status to running
        self.pipeline_manager.update_run_status(run_id, PipelineStatus.RUNNING, 
                                               self.current_run_data)

        try:
            # Execute each stage
            for stage_def in pipeline['stages']:
                stage_result = self._execute_stage(stage_def, pipeline)
                self.current_run_data['stages'].append(stage_result)

                # Check if stage failed and should stop
                if stage_result['status'] == 'failed' and not stage_def.get('continue_on_error', False):
                    self._log(f"❌ Stage '{stage_def['name']}' failed, stopping pipeline")

                    # Check rollback policy
                    if pipeline.get('rollback_policy', {}).get('auto_rollback_on_failure', True):
                        self._execute_rollback(pipeline)

                    self.pipeline_manager.update_run_status(
                        run_id, PipelineStatus.FAILED, self.current_run_data
                    )
                    return self.current_run_data

            # All stages completed successfully
            self._log("✅ Pipeline completed successfully")
            self.pipeline_manager.update_run_status(
                run_id, PipelineStatus.SUCCESS, self.current_run_data
            )

        except Exception as e:
            self._log(f"❌ Pipeline execution error: {str(e)}", level="ERROR")
            self.current_run_data['error'] = str(e)
            self.pipeline_manager.update_run_status(
                run_id, PipelineStatus.FAILED, self.current_run_data
            )

        return self.current_run_data

    def _execute_stage(self, stage_def: Dict[str, Any], 
                      pipeline: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single pipeline stage."""
        stage_name = stage_def['name']
        stage_type = stage_def['type']

        self._log(f"▶️  Executing stage: {stage_name} ({stage_type})")

        stage_result = {
            'name': stage_name,
            'type': stage_type,
            'status': 'running',
            'started_at': datetime.utcnow().isoformat(),
            'steps': []
        }

        try:
            # Execute steps
            for step_def in stage_def['steps']:
                step_result = self._execute_step(step_def, stage_def, pipeline)
                stage_result['steps'].append(step_result)

                if step_result['status'] == 'failed':
                    stage_result['status'] = 'failed'
                    stage_result['completed_at'] = datetime.utcnow().isoformat()
                    return stage_result

            # Stage completed successfully
            stage_result['status'] = 'success'
            stage_result['completed_at'] = datetime.utcnow().isoformat()

            # Handle gold sample collection if this is a gold sample stage
            if stage_type == StageType.GOLD_SAMPLE_COLLECTION.value:
                self._collect_gold_samples(stage_def, stage_result, pipeline)

        except Exception as e:
            self._log(f"❌ Stage error: {str(e)}", level="ERROR")
            stage_result['status'] = 'failed'
            stage_result['error'] = str(e)
            stage_result['completed_at'] = datetime.utcnow().isoformat()

        return stage_result

    def _execute_step(self, step_def: Dict[str, Any], stage_def: Dict[str, Any],
                     pipeline: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step within a stage."""
        step_name = step_def['name']
        action = step_def['action']
        params = step_def.get('params', {})

        self._log(f"  ▸ Step: {step_name}")

        step_result = {
            'name': step_name,
            'action': action,
            'status': 'running',
            'started_at': datetime.utcnow().isoformat()
        }

        try:
            # Execute action based on type
            if action.startswith('script:'):
                # Execute script
                script_path = action.split(':', 1)[1]
                output = self._run_script(script_path, params)
                step_result['output'] = output

            elif action.startswith('command:'):
                # Execute command
                command = action.split(':', 1)[1]
                output = self._run_command(command, params)
                step_result['output'] = output

            elif action == 'conformance_test':
                # Run conformance tests
                output = self._run_conformance_tests(params)
                step_result['output'] = output

            elif action == 'gold_sample_validate':
                # Validate against gold sample
                validation_result = self._validate_gold_sample(params)
                step_result['output'] = validation_result

                # Add to run data
                self.current_run_data['gold_sample_validations'].append(validation_result)

                # Check if validation passed
                if not validation_result['passed']:
                    step_result['status'] = 'failed'
                    step_result['completed_at'] = datetime.utcnow().isoformat()
                    return step_result

            elif action == 'deploy_model':
                # Deploy model
                output = self._deploy_model(params, pipeline)
                step_result['output'] = output

            else:
                self._log(f"⚠️  Unknown action: {action}", level="WARNING")
                step_result['output'] = {'warning': f'Unknown action: {action}'}

            # Collect artifacts if specified
            if 'artifacts' in step_def:
                for artifact_pattern in step_def['artifacts']:
                    self._collect_artifacts(artifact_pattern, stage_def['name'])

            # Capture gold sample if requested
            if step_def.get('gold_sample_capture', False):
                self._capture_gold_sample(step_result, stage_def, pipeline)

            step_result['status'] = 'success'
            step_result['completed_at'] = datetime.utcnow().isoformat()

        except Exception as e:
            self._log(f"❌ Step error: {str(e)}", level="ERROR")
            step_result['status'] = 'failed'
            step_result['error'] = str(e)
            step_result['completed_at'] = datetime.utcnow().isoformat()

        return step_result

    def _run_script(self, script_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a script file."""
        script_file = Path(script_path)
        if not script_file.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        # Build command with parameters
        cmd = [str(script_file)]
        for key, value in params.items():
            cmd.extend([f"--{key}", str(value)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    def _run_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a shell command."""
        # Substitute parameters in command
        for key, value in params.items():
            command = command.replace(f"${{{key}}}", str(value))

        result = subprocess.run(command, shell=True, capture_output=True, 
                              text=True, timeout=300)

        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    def _run_conformance_tests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run conformance test suite."""
        # This would integrate with the existing conformance test system
        self._log("  Running conformance tests...")

        # Placeholder - would call actual test runner
        return {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'message': 'Conformance test integration pending'
        }

    def _validate_gold_sample(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate current output against a gold sample."""
        sample_id = params.get('sample_id')
        test_data = params.get('test_data', {})
        comparison_method = params.get('comparison_method', 'fuzzy')
        threshold = params.get('threshold', 0.95)

        if not sample_id:
            raise ValueError("sample_id required for gold sample validation")

        passed, score, differences = self.gold_sample_manager.validate_against_sample(
            sample_id, test_data, self.current_run_id, comparison_method, threshold
        )

        return {
            'sample_id': sample_id,
            'passed': passed,
            'similarity_score': score,
            'differences': differences,
            'comparison_method': comparison_method,
            'threshold': threshold
        }

    def _deploy_model(self, params: Dict[str, Any], 
                     pipeline: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a model."""
        model_id = params.get('model_id')
        target_env = params.get('target_environment', 'production')
        strategy = pipeline.get('deployment_strategy', 'rolling')

        self._log(f"  Deploying model {model_id} to {target_env} using {strategy} strategy")

        # Placeholder - would integrate with actual deployment system
        return {
            'model_id': model_id,
            'target_environment': target_env,
            'strategy': strategy,
            'deployed': True,
            'message': 'Deployment integration pending'
        }

    def _collect_artifacts(self, pattern: str, stage_name: str):
        """Collect artifacts matching pattern."""
        # Find files matching pattern
        artifacts_dir = Path('./artifacts')
        if not artifacts_dir.exists():
            return

        for artifact_path in artifacts_dir.glob(pattern):
            artifact_id = self.pipeline_manager.add_artifact(
                self.current_run_id, artifact_path.name, str(artifact_path), stage_name
            )

            self.current_run_data['artifacts'].append({
                'artifact_id': artifact_id,
                'name': artifact_path.name,
                'path': str(artifact_path),
                'stage': stage_name
            })

    def _capture_gold_sample(self, step_result: Dict[str, Any], 
                            stage_def: Dict[str, Any], 
                            pipeline: Dict[str, Any]):
        """Capture output as a gold sample."""
        gold_config = pipeline.get('gold_sample_config', {})

        if not gold_config.get('enabled', True):
            return

        # Create gold sample from step output
        sample_data = {
            'inputs': step_result.get('params', {}),
            'outputs': step_result.get('output', {}),
            'metrics': step_result.get('metrics', {})
        }

        sample_id = self.gold_sample_manager.create_sample(
            pipeline_id=pipeline['pipeline_id'],
            stage=stage_def['name'],
            step=step_result['name'],
            data=sample_data,
            version=pipeline['version']
        )

        self.current_run_data['gold_samples_collected'].append(sample_id)
        self._log(f"  📦 Captured gold sample: {sample_id}")

    def _collect_gold_samples(self, stage_def: Dict[str, Any], 
                             stage_result: Dict[str, Any],
                             pipeline: Dict[str, Any]):
        """Collect gold samples from a gold sample collection stage."""
        self._log("  📦 Collecting gold samples from stage outputs")

        # This would collect samples from all steps in the stage
        for step_result in stage_result['steps']:
            if step_result.get('output'):
                self._capture_gold_sample(step_result, stage_def, pipeline)

    def _execute_rollback(self, pipeline: Dict[str, Any]):
        """Execute rollback procedure."""
        self._log("🔄 Executing rollback...")

        rollback_policy = pipeline.get('rollback_policy', {})

        if not rollback_policy.get('enabled', True):
            self._log("  Rollback disabled in policy")
            return

        # Execute rollback stages
        rollback_stages = rollback_policy.get('rollback_stages', [])

        for stage_name in rollback_stages:
            self._log(f"  Rolling back stage: {stage_name}")
            # Placeholder - would execute actual rollback logic

        self.current_run_data['rollback'] = {
            'triggered': True,
            'reason': 'Pipeline failure',
            'timestamp': datetime.utcnow().isoformat()
        }

    def _log(self, message: str, level: str = "INFO"):
        """Log a message."""
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }

        if self.current_run_data:
            self.current_run_data['logs'].append(log_entry)

        print(f"[{timestamp}] {level}: {message}")
