from contextlib import asynccontextmanager

from fastapi import FastAPI



@asynccontextmanager
async def node_lifespan(app: 'BOAFastApi'):
    await app.node.initialise()
    # print("\n=== Registered endpoints (from OpenAPI) ===")
    #
    # # Force generation of the schema
    # openapi = app.openapi()
    #
    # paths = openapi.get("paths", {})
    # for path, methods in sorted(paths.items()):
    #     method_list = [m.upper() for m in methods.keys() if m.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}]
    #     if method_list:
    #         print(f"{', '.join(sorted(method_list)):20} {path}")
    #
    # print("==========================================\n")
    yield