import logging
from celery import shared_task
from authApp.services.pulse_producer import PulseProducer

logger = logging.getLogger(__name__)

@shared_task(name="authApp.tasks.pulse_heartbeat.broadcast_system_pulse")
def broadcast_system_pulse():
    """
    Centralized Pulse Broadcaster.
    Engineered for hyper-scale: Runs in a dedicated Celery worker to 
    ensure zero impact on the ASGI/Daphne request cycle.
    """
    PulseProducer.broadcast_pulse()
