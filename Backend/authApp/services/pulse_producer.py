import logging
import psutil
from datetime import datetime
from django.db import connection
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

class PulseProducer:
    """
    Hyper-Scale Metrics Producer.
    
    ENGINEERING HIGHLIGHTS:
    1. SINGLE SOURCE OF TRUTH: Gathers metrics once and broadcasts to all.
    2. LOW OVERHEAD: Uses non-blocking patterns to minimize impact on server cores.
    3. EXTENSIBLE: Can be easily hooked into prometheus or other monitoring sinks.
    """
    
    GROUP_NAME = "system_pulse"

    @classmethod
    def broadcast_pulse(cls):
        """
        The 'Heartbeat' of the entire platform. 
        Should be called by a centralized scheduler (Celery/Cron).
        """
        stats = cls._gather_stats()
        channel_layer = get_channel_layer()
        
        message = {
            "type": "system.metrics.update",
            "data": {
                "type": "metrics_pulse",
                "timestamp": str(datetime.now()),
                "stats": stats
            }
        }
        
        try:
            async_to_sync(channel_layer.group_send)(cls.GROUP_NAME, message)
        except Exception as e:
            logger.error(f"Global Pulse Broadcast failed: {e}")

    @staticmethod
    def _gather_stats():
        """
        Ultra-efficient stats gathering using cached-like behavior for psutil.
        """
        # CPU usage (non-blocking interval)
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        # Database verification (Stateless check)
        db_status = "healthy"
        try:
            # Note: We use a lightweight check to avoid DB connection exhaustion
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            db_status = "degraded"

        return {
            "cpu": cpu,
            "memory": mem,
            "disk": disk,
            "db": db_status
        }
