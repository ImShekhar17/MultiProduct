import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    notifications: [
        { id: 1, title: "System Online", desc: "All services are running at optimal performance.", type: "system", time: "Just now", read: false },
    ],
    toasts: [],
};

const notificationSlice = createSlice({
    name: 'notifications',
    initialState,
    reducers: {
        addNotification: (state, action) => {
            const newNotif = {
                id: Date.now(),
                time: "Just now",
                read: false,
                ...action.payload
            };
            state.notifications.unshift(newNotif);
            // Limit to last 20 notifications
            if (state.notifications.length > 20) state.notifications.pop();

            // Add to toasts
            state.toasts.push(newNotif);
        },
        removeToast: (state, action) => {
            state.toasts = state.toasts.filter(t => t.id !== action.payload);
        },
        markAsRead: (state, action) => {
            const notif = state.notifications.find(n => n.id === action.payload);
            if (notif) notif.read = true;
        },
        markAllAsRead: (state) => {
            state.notifications.forEach(n => n.read = true);
        }
    },
});

export const { addNotification, removeToast, markAsRead, markAllAsRead } = notificationSlice.actions;
export const selectNotifications = (state) => state.notifications.notifications;
export const selectToasts = (state) => state.notifications.toasts;

export default notificationSlice.reducer;
