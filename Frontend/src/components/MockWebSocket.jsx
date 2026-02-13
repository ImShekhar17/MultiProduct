import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { addNotification } from '../Redux/ReduxSlice/NotificationSlice';

/**
 * MockWebSocket component.
 * Simulates incoming real-time events from a WebSocket server.
 * Only for demonstration purposes as per user request.
 */
const MockWebSocket = () => {
    const dispatch = useDispatch();

    useEffect(() => {
        // Initial welcome message
        const welcomeTimeout = setTimeout(() => {
            dispatch(addNotification({
                title: "Connected to Matrix",
                desc: "Real-time sync established with Stark-Grade infrastructure.",
                type: "success"
            }));
        }, 2000);

        // Random events simulator
        const interval = setInterval(() => {
            const events = [
                { title: "Node Optimization", desc: "System nodes re-balanced for optimal latency.", type: "system" },
                { title: "New Subscriber", desc: "A guest user just upgraded to CRM Enterprise.", type: "success" },
                { title: "Traffic Surge", desc: "Detected 20% increase in API requests.", type: "system" },
                { title: "Backup Complete", desc: "Incremental backup successful for all product nodes.", type: "success" },
                { title: "Security Scan", desc: "0 vulnerabilities found in recent weekly audit.", type: "success" }
            ];

            // 15% chance of an event every 30 seconds
            if (Math.random() < 0.15) {
                const randomEvent = events[Math.floor(Math.random() * events.length)];
                dispatch(addNotification(randomEvent));
            }
        }, 30000);

        return () => {
            clearTimeout(welcomeTimeout);
            clearInterval(interval);
        };
    }, [dispatch]);

    return null; // This component doesn't render anything
};

export default MockWebSocket;
