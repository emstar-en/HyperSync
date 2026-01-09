"""
API Server - Unified API server with all routes.

Main API server that wires all route modules together.
"""
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from hypersync.api.router_registry import get_router_registry
from hypersync.api.route_loader import load_all_routes

logger = logging.getLogger(__name__)


class HyperSyncAPIServer:
    """Main API server application."""

    def __init__(self, title: str = "HyperSync API", version: str = "1.0.0"):
        self.app = FastAPI(
            title=title,
            version=version,
            description="Hyperbolic Orchestration Platform API"
        )
        self.registry = get_router_registry()
        self._setup_middleware()

    def _setup_middleware(self):
        """Setup middleware."""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Request logging
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            logger.info(f"{request.method} {request.url.path}")
            response = await call_next(request)
            logger.info(f"Response status: {response.status_code}")
            return response

    def initialize(self):
        """Initialize the API server by loading all routes."""
        logger.info("Initializing HyperSync API Server...")

        # Load all route modules
        loaded_count = load_all_routes()
        logger.info(f"Loaded {loaded_count} route modules")

        # Mount routes from registry
        self._mount_routes()

        # Add health check endpoint
        self._add_health_check()

        # Add OpenAPI endpoint
        self._add_openapi_endpoint()

        logger.info("API server initialization complete")

    def _mount_routes(self):
        """Mount all routes from the registry."""
        for group in self.registry.list_groups():
            logger.debug(f"Mounting router group: {group.name} at {group.prefix}")

            for route in group.routes:
                full_path = f"{group.prefix}{route.path}"

                # Create route handler
                self.app.add_api_route(
                    path=full_path,
                    endpoint=route.handler,
                    methods=[route.method.value],
                    summary=route.summary,
                    description=route.description,
                    tags=route.tags,
                    deprecated=route.deprecated,
                    response_model=route.response_model
                )

                logger.debug(f"  Mounted: {route.method.value} {full_path}")

    def _add_health_check(self):
        """Add health check endpoint."""
        @self.app.get("/health", tags=["health"])
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "service": "hypersync-api",
                "version": self.app.version
            }

        @self.app.get("/ready", tags=["health"])
        async def readiness_check():
            """Readiness check endpoint."""
            status = self.registry.get_status()
            return {
                "status": "ready",
                "routes": status["total_routes"],
                "groups": status["total_groups"]
            }

    def _add_openapi_endpoint(self):
        """Add custom OpenAPI endpoint."""
        @self.app.get("/openapi.json", include_in_schema=False)
        async def get_openapi():
            """Get OpenAPI specification."""
            return self.registry.generate_openapi_spec()

    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app


def create_app() -> FastAPI:
    """
    Create and initialize the API server.

    Returns:
        FastAPI application instance
    """
    server = HyperSyncAPIServer()
    server.initialize()
    return server.get_app()


# For uvicorn
app = create_app()
