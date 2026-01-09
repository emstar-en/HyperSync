"""
HyperSync Gap Analysis Patches - Wiring Layer
Integrates all gap analysis patches into the core system.
"""

from typing import Dict, Any, Optional
import logging

# Import all patch components
from hypersync.document_processing.api import router as doc_processing_router
from hypersync.model_serving.api import router as model_serving_router
from hypersync.query_processing.api import router as query_processing_router
from hypersync.integrations.api import router as integrations_router
from hypersync.visualization.api.routes import router as visualization_router

# Import core components
from hypersync.document_processing.pipeline import DocumentPipeline
from hypersync.model_serving.registry import ModelRegistry
from hypersync.model_serving.inference import InferenceEngine
from hypersync.query_processing.parser import QueryParser
from hypersync.query_processing.enhancer import QueryEnhancer
from hypersync.integrations.storage.s3 import S3Client
from hypersync.integrations.queues.kafka import KafkaClient
from hypersync.visualization.graph.explorer import GraphExplorer
from hypersync.visualization.hyperbolic.viewer import PoincareViewer

logger = logging.getLogger(__name__)


class GapAnalysisIntegration:
    """Main integration class for gap analysis patches."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize gap analysis integration.

        Args:
            config: System configuration
        """
        self.config = config
        self.components = {}

        logger.info("Initializing Gap Analysis Integration")

    def initialize_document_processing(self):
        """Initialize document processing pipeline."""
        logger.info("Initializing Document Processing Pipeline")

        self.components['document_pipeline'] = DocumentPipeline(
            config=self.config.get('document_processing', {})
        )

        logger.info("✓ Document Processing Pipeline initialized")

    def initialize_model_serving(self):
        """Initialize model serving layer."""
        logger.info("Initializing Model Serving Layer")

        self.components['model_registry'] = ModelRegistry(
            db_config=self.config.get('database', {})
        )

        self.components['inference_engine'] = InferenceEngine(
            registry=self.components['model_registry'],
            config=self.config.get('model_serving', {})
        )

        logger.info("✓ Model Serving Layer initialized")

    def initialize_query_processing(self):
        """Initialize query processing and enhancement."""
        logger.info("Initializing Query Processing")

        self.components['query_parser'] = QueryParser()

        self.components['query_enhancer'] = QueryEnhancer(
            config=self.config.get('query_processing', {})
        )

        logger.info("✓ Query Processing initialized")

    def initialize_integrations(self):
        """Initialize external integrations."""
        logger.info("Initializing External Integrations")

        # Storage connectors
        if self.config.get('integrations', {}).get('storage', {}).get('s3', {}).get('enabled'):
            self.components['s3_client'] = S3Client(
                config=self.config['integrations']['storage']['s3']
            )

        # Message queues
        if self.config.get('integrations', {}).get('message_queues', {}).get('kafka', {}).get('enabled'):
            self.components['kafka_client'] = KafkaClient(
                config=self.config['integrations']['message_queues']['kafka']
            )

        logger.info("✓ External Integrations initialized")

    def initialize_visualization(self):
        """Initialize visualization layer."""
        logger.info("Initializing Visualization Layer")

        self.components['graph_explorer'] = GraphExplorer()

        logger.info("✓ Visualization Layer initialized")

    def initialize_all(self):
        """Initialize all gap analysis components."""
        logger.info("="*60)
        logger.info("INITIALIZING GAP ANALYSIS PATCHES")
        logger.info("="*60)

        try:
            self.initialize_document_processing()
            self.initialize_model_serving()
            self.initialize_query_processing()
            self.initialize_integrations()
            self.initialize_visualization()

            logger.info("="*60)
            logger.info("✅ ALL GAP ANALYSIS PATCHES INITIALIZED")
            logger.info("="*60)

            return True
        except Exception as e:
            logger.error(f"Failed to initialize gap analysis patches: {e}")
            return False

    def get_component(self, name: str) -> Optional[Any]:
        """Get initialized component by name.

        Args:
            name: Component name

        Returns:
            Component instance or None
        """
        return self.components.get(name)

    def get_all_routers(self):
        """Get all API routers for FastAPI integration.

        Returns:
            List of API routers
        """
        return [
            doc_processing_router,
            model_serving_router,
            query_processing_router,
            integrations_router,
            visualization_router
        ]


# Global integration instance
_integration_instance: Optional[GapAnalysisIntegration] = None


def initialize_gap_analysis(config: Dict[str, Any]) -> GapAnalysisIntegration:
    """Initialize gap analysis integration (singleton).

    Args:
        config: System configuration

    Returns:
        Integration instance
    """
    global _integration_instance

    if _integration_instance is None:
        _integration_instance = GapAnalysisIntegration(config)
        _integration_instance.initialize_all()

    return _integration_instance


def get_gap_analysis_integration() -> Optional[GapAnalysisIntegration]:
    """Get gap analysis integration instance.

    Returns:
        Integration instance or None
    """
    return _integration_instance
