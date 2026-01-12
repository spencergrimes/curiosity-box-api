"""Health check endpoints for K8s/ECS probes."""
import logging
import os

from django.core.cache import cache
from django.db import connection
from rest_framework.decorators import (api_view, permission_classes,
                                       throttle_classes)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([])
def health_check(request):
    """Returns 200 if healthy, 503 if degraded. Checks DB, API config, cache."""
    checks = {
        'database': check_database(),
        'anthropic_api_configured': check_anthropic_api_configured(),
        'cache': check_cache(),
    }

    # System is healthy only if all critical checks pass
    critical_checks = ['database', 'anthropic_api_configured']
    all_critical_healthy = all(checks[key] for key in critical_checks)

    status_code = 200 if all_critical_healthy else 503
    status_text = 'healthy' if all_critical_healthy else 'degraded'

    logger.info(
        f"Health check: {status_text}",
        extra={
            'status': status_text,
            'checks': checks,
        }
    )

    return Response({
        'status': status_text,
        'checks': checks,
        'version': '1.0.0',
    }, status=status_code)


def check_database():
    """Verify database connectivity."""
    try:
        connection.ensure_connection()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def check_anthropic_api_configured():
    """Check if Anthropic API key is set."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    is_configured = bool(api_key and api_key != 'test-key-for-ci')

    if not is_configured:
        logger.warning("Anthropic API key not configured")

    return is_configured


def check_cache():
    """Verify cache is working (non-critical)."""
    try:
        cache.set('health_check', 'ok', 10)
        result = cache.get('health_check') == 'ok'
        cache.delete('health_check')
        return result
    except Exception as e:
        logger.warning(f"Cache health check failed: {e}")
        return False


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([])
def readiness_check(request):
    """K8s readiness probe - returns 200 when ready for traffic."""
    return health_check(request)


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([])
def liveness_check(request):
    """K8s liveness probe - process is alive if we respond."""
    return Response({'status': 'alive'}, status=200)
