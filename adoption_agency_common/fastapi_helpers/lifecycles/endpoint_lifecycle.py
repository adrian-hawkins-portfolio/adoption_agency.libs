from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.routing import Mount, BaseRoute

from adoption_agency_common.util import logger

def _collect_routes(routes: list[BaseRoute], prefix: str = "") -> list[tuple[str, str]]:
    """Recursively collect all (methods, path) pairs."""
    result = []

    for route in routes:
        # Build the full path
        path = getattr(route, "path", "")
        full_path = (prefix.rstrip("/") + "/" + path.lstrip("/")).rstrip("/") or "/"

        if isinstance(route, APIRoute):
            methods = ", ".join(sorted(route.methods - {"HEAD", "OPTIONS"}))
            result.append((methods, full_path))

        elif isinstance(route, Mount):
            # Mounted sub-applications
            result.append(("MOUNT", full_path))
            # Recurse into the mounted app if it has routes
            if hasattr(route.app, "routes"):
                result.extend(_collect_routes(route.app.routes, full_path))

        # Handle included routers (the common case)
        elif hasattr(route, "routes"):
            result.extend(_collect_routes(route.routes, full_path if path else prefix))

    return result


@asynccontextmanager
async def endpoint_lifespan(app: FastAPI):
    print("\n=== Registered endpoints (from OpenAPI) ===")

    # Force generation of the schema
    openapi = app.openapi()

    paths = openapi.get("paths", {})
    for path, methods in sorted(paths.items()):
        method_list = [m.upper() for m in methods.keys() if m.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}]
        if method_list:
            print(f"{', '.join(sorted(method_list)):20} {path}")

    print("==========================================\n")
    yield