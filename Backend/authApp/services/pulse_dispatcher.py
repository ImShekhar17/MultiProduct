import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

class PulseDispatcher:
    """
    Standardized Dispatcher for WebSocket events.
    Enables loose coupling between business logic and the real-time layer.
    """
    
    GROUP_NAME = "system_pulse"

    @classmethod
    def broadcast_event(cls, event_type, payload):
        """
        Sends an event to the system_pulse group.
        Standardizes the message format for consumption by PulseConsumer.
        """
        channel_layer = get_channel_layer()
        
        message = {
            "type": "system.metrics.update", # Maps to the consumer's handler
            "data": {
                "type": "system_event",
                "event": event_type,
                "payload": payload
            }
        }
        
        try:
            async_to_sync(channel_layer.group_send)(cls.GROUP_NAME, message)
            logger.info(f"Broadcasted event '{event_type}' to {cls.GROUP_NAME}")
        except Exception as e:
            logger.error(f"Failed to broadcast event '{event_type}': {e}")

    @classmethod
    def notify_user_update(cls, user_id, update_type, data):
        """
        Example of scoppable broadcasting. 
        In a production system, users would join groups like 'user_{id}'.
        """
        channel_layer = get_channel_layer()
        group_name = f"user_{user_id}"
        
        message = {
            "type": "user.notification", # Would need a corresponding handler in a consumer
            "data": {
                "type": update_type,
                "data": data
            }
        }
        
        try:
            async_to_sync(channel_layer.group_send)(group_name, message)
        except Exception:
            pass
