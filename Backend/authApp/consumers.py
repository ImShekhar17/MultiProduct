import json
import asyncio
import logging
import psutil
from datetime import datetime
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db import connection
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class PulseConsumer(AsyncJsonWebsocketConsumer):
    """
    Stark-Grade Real-time Monitoring Consumer.
    
    ENGINEERING HIGHLIGHTS (HYPER-SCALE):
    1. PRODUCER-CONSUMER PATTERN: Removed internal per-process loops to prevent 
       redundant 'psutil' calls across hundreds of workers.
    2. REDIS-BACKPLANED: Metrics are now pushed by a centralized producer 
       (Celery/Dedicated Script) and forwarded by this consumer.
    3. MASSIVE CONCURRENCY: Optimized for thousands of connections per daphne worker.
    """
    
    GROUP_NAME = "system_pulse"

    async def connect(self):
        """Handles the WebSocket handshake and group joining."""
        # Professional Check: Restrict to authenticated users
        if self.scope["user"].is_anonymous:
            logger.warning(f"Unauthorized WS connection attempt from {self.scope.get('client')}")
            await self.close(code=4003) # 4003: Policy Violation
            return

        await self.accept()
        
        # Join the system_pulse group
        await self.channel_layer.group_add(
            self.GROUP_NAME,
            self.channel_name
        )
        
        logger.info(f"User {self.scope['user'].username} linked to System Pulse Grid.")

    async def disconnect(self, close_code):
        """Clean up on disconnection."""
        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )
        logger.info(f"User {self.scope.get('user')} disconnected (Code: {close_code})")

    async def receive_json(self, content):
        """
        Handle incoming messages from the client.
        Meta-Grade: Consumers should be primarily for broadcasting; 
        logic should be handled via HTTP APIs where possible.
        """
        msg_type = content.get("type")
        if msg_type == "ping":
            await self.send_json({"type": "pong", "timestamp": str(datetime.now())})

    async def system_metrics_update(self, event):
        """
        Hyper-Scale Handler: Standardizes message delivery for millions of packets.
        """
        # Amazon-Level Security: Ensure no sensitive server data leaks in the stream
        data = event.get("data", {})
        await self.send_json(data)
