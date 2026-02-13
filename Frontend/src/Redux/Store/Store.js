import { configureStore } from "@reduxjs/toolkit";
import authReducer from "../ReduxSlice/AuthSlice";
import notificationReducer from "../ReduxSlice/NotificationSlice";
import cartReducer from "../ReduxSlice/CartSlice";

/**
 * Industry Standard Redux Store Setup (Fresh).
 * This configuration uses Redux Toolkit's 'configureStore', 
 * which automatically sets up 'redux-thunk' and the Redux DevTools extension.
 */
const store = configureStore({
    reducer: {
        auth: authReducer,
        notifications: notificationReducer,
        cart: cartReducer,
    },

    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: false, // Recommended for handling complex backend responses
        }),
});

export default store;
