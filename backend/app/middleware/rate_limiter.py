import time
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.dependencies import get_cache

logger = logging.getLogger("lecture-assistant.middleware.rate_limiter")

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window_secs: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_secs = window_secs

    async def dispatch(self, request: Request, call_next):
        # Allow Swagger UI, ReDoc and health check without rate limits
        path = request.url.path
        if path.startswith("/api/docs") or path.startswith("/api/redoc") or path == "/health" or path == "/api/health/":
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "unknown"
        cache = get_cache()
        
        # Unique key for rate limiting
        key = f"rate_limit:{client_ip}:{path}"
        
        try:
            current_requests = cache.get(key)
            if current_requests is None:
                # Initialize rate limit window
                cache.set(key, 1, expiry=self.window_secs)
                current_requests = 1
            else:
                current_requests = int(current_requests)
                if current_requests >= self.limit:
                    logger.warning(f"Rate limit exceeded for IP: {client_ip} on path: {path}")
                    return JSONResponse(
                        status_code=429,
                        content={
                            "status": "error",
                            "message": "Too many requests. Please try again later.",
                        }
                    )
                cache.set(key, current_requests + 1, expiry=self.window_secs)
                
        except Exception as e:
            # Degrade gracefully by skipping rate limiting on cache errors
            logger.error(f"Rate limiting cache error: {str(e)}")
            
        return await call_next(request)
