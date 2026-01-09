"""
API Router Registry - Central registry for API routes.

Manages registration and organization of API routes into groups.
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class RouteCategory(Enum):
    """Categories for organizing routes."""
    CORE = "core"
    MESH = "mesh"
    SCHEDULER = "scheduler"
    GOVERNANCE = "governance"
    DEPLOYMENT = "deployment"
    TELEMETRY = "telemetry"
    SECURITY = "security"
    AGENT = "agent"
    ORCHESTRATOR = "orchestrator"
    HEALTH = "health"
    ADMIN = "admin"


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


@dataclass
class RouteMetadata:
    """Metadata for an API route."""
    path: str
    method: HTTPMethod
    handler: Callable
    category: RouteCategory
    summary: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    requires_auth: bool = True
    deprecated: bool = False
    version: str = "v1"
    request_model: Optional[Any] = None
    response_model: Optional[Any] = None


@dataclass
class RouterGroup:
    """Group of related routes."""
    name: str
    prefix: str
    category: RouteCategory
    routes: List[RouteMetadata] = field(default_factory=list)
    middleware: List[Callable] = field(default_factory=list)


class APIRouterRegistry:
    """
    Central registry for API routes.

    Responsibilities:
    - Register routes with metadata
    - Organize routes into groups
    - Provide route lookup
    - Generate OpenAPI documentation
    """

    def __init__(self):
        self._routes: Dict[str, RouteMetadata] = {}
        self._groups: Dict[str, RouterGroup] = {}
        self._categories: Dict[RouteCategory, List[str]] = {
            cat: [] for cat in RouteCategory
        }

    def register_group(
        self,
        name: str,
        prefix: str,
        category: RouteCategory,
        middleware: Optional[List[Callable]] = None
    ) -> RouterGroup:
        """
        Register a router group.

        Args:
            name: Group name
            prefix: URL prefix (e.g., "/api/v1/mesh")
            category: Route category
            middleware: Group-level middleware

        Returns:
            RouterGroup instance
        """
        if name in self._groups:
            logger.warning(f"Router group {name} already registered, replacing")

        group = RouterGroup(
            name=name,
            prefix=prefix,
            category=category,
            middleware=middleware or []
        )

        self._groups[name] = group
        logger.debug(f"Registered router group: {name} ({prefix})")

        return group

    def register_route(
        self,
        group_name: str,
        path: str,
        method: HTTPMethod,
        handler: Callable,
        summary: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        requires_auth: bool = True,
        deprecated: bool = False,
        version: str = "v1",
        request_model: Optional[Any] = None,
        response_model: Optional[Any] = None
    ) -> None:
        """
        Register an API route.

        Args:
            group_name: Router group name
            path: Route path (relative to group prefix)
            method: HTTP method
            handler: Handler function
            summary: Short summary
            description: Detailed description
            tags: OpenAPI tags
            requires_auth: Whether route requires authentication
            deprecated: Whether route is deprecated
            version: API version
            request_model: Pydantic request model
            response_model: Pydantic response model
        """
        if group_name not in self._groups:
            raise ValueError(f"Router group {group_name} not registered")

        group = self._groups[group_name]
        full_path = f"{group.prefix}{path}"
        route_key = f"{method.value}:{full_path}"

        if route_key in self._routes:
            logger.warning(f"Route {route_key} already registered, replacing")

        metadata = RouteMetadata(
            path=path,
            method=method,
            handler=handler,
            category=group.category,
            summary=summary,
            description=description,
            tags=tags or [group.category.value],
            requires_auth=requires_auth,
            deprecated=deprecated,
            version=version,
            request_model=request_model,
            response_model=response_model
        )

        self._routes[route_key] = metadata
        group.routes.append(metadata)
        self._categories[group.category].append(route_key)

        logger.debug(f"Registered route: {method.value} {full_path}")

    def get_route(self, method: HTTPMethod, path: str) -> Optional[RouteMetadata]:
        """Get route metadata by method and path."""
        route_key = f"{method.value}:{path}"
        return self._routes.get(route_key)

    def get_group(self, name: str) -> Optional[RouterGroup]:
        """Get router group by name."""
        return self._groups.get(name)

    def list_routes(
        self,
        category: Optional[RouteCategory] = None,
        version: Optional[str] = None,
        include_deprecated: bool = False
    ) -> List[RouteMetadata]:
        """
        List routes, optionally filtered.

        Args:
            category: Filter by category
            version: Filter by version
            include_deprecated: Include deprecated routes

        Returns:
            List of route metadata
        """
        routes = list(self._routes.values())

        if category:
            routes = [r for r in routes if r.category == category]

        if version:
            routes = [r for r in routes if r.version == version]

        if not include_deprecated:
            routes = [r for r in routes if not r.deprecated]

        return sorted(routes, key=lambda r: (r.category.value, r.path))

    def list_groups(self) -> List[RouterGroup]:
        """List all router groups."""
        return list(self._groups.values())

    def generate_openapi_spec(self) -> Dict[str, Any]:
        """
        Generate OpenAPI specification.

        Returns:
            OpenAPI spec dictionary
        """
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "HyperSync API",
                "version": "1.0.0",
                "description": "Hyperbolic Orchestration Platform API"
            },
            "servers": [
                {"url": "/api/v1", "description": "Version 1"}
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }

        # Add routes to paths
        for route in self.list_routes():
            group = self._find_group_for_route(route)
            if not group:
                continue

            full_path = f"{group.prefix}{route.path}"

            if full_path not in spec["paths"]:
                spec["paths"][full_path] = {}

            method_lower = route.method.value.lower()
            spec["paths"][full_path][method_lower] = {
                "summary": route.summary,
                "description": route.description,
                "tags": route.tags,
                "deprecated": route.deprecated
            }

            if route.requires_auth:
                spec["paths"][full_path][method_lower]["security"] = [
                    {"bearerAuth": []}
                ]

            # Add request/response models if available
            if route.request_model:
                spec["paths"][full_path][method_lower]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{route.request_model.__name__}"}
                        }
                    }
                }

            if route.response_model:
                spec["paths"][full_path][method_lower]["responses"] = {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{route.response_model.__name__}"}
                            }
                        }
                    }
                }

        return spec

    def _find_group_for_route(self, route: RouteMetadata) -> Optional[RouterGroup]:
        """Find the group that contains a route."""
        for group in self._groups.values():
            if route in group.routes:
                return group
        return None

    def get_status(self) -> Dict[str, Any]:
        """Get registry status."""
        return {
            "total_routes": len(self._routes),
            "total_groups": len(self._groups),
            "categories": {
                cat.value: len(self._categories[cat])
                for cat in RouteCategory
            },
            "deprecated_routes": len([
                r for r in self._routes.values()
                if r.deprecated
            ])
        }


# Global registry instance
_registry: Optional[APIRouterRegistry] = None


def get_router_registry() -> APIRouterRegistry:
    """Get the global API router registry instance."""
    global _registry
    if _registry is None:
        _registry = APIRouterRegistry()
    return _registry
