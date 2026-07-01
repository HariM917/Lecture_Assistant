import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("lecture-assistant.middleware.logging")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract request details
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        logger.info(f"Incoming request: {method} {path} from IP: {client_ip}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Log response details
            status_code = response.status_code
            logger.info(
                f"Completed response: {method} {path} - Status: {status_code} - "
                f"Duration: {process_time:.2f}ms"
            )
            
            # Add process time header
            response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Failed response: {method} {path} - Error: {str(e)} - "
                f"Duration: {process_time:.2f}ms"
            )
            raise e
