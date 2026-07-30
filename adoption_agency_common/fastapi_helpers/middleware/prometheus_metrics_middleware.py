import time


from adoption_agency_common.metrics.requests import IN_PROGRESS, REQUEST_COUNT, REQUEST_LATENCY

build_in_endpoints = ["/health", "/metrics"]

async def prometheus_middleware(request, call_next):
    method = request.method
    endpoint = request.url.path
    if endpoint in build_in_endpoints:
        return await call_next(request)
    IN_PROGRESS.inc()
    start = time.perf_counter()

    try:
        response = await call_next(request)
        route = request.scope.get("route")
        if route:
            endpoint = route.path
        status = str(response.status_code)
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=status,
        ).inc()
        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint,
        ).observe(time.perf_counter() - start)
        return response
    except Exception:
        route = request.scope.get("route")
        if route:
            endpoint = route.path
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status="500",
        ).inc()
        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint,
        ).observe(time.perf_counter() - start)
        raise
    finally:
        IN_PROGRESS.dec()