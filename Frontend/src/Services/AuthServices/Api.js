import axios from "axios";

/**
 * Professional Axios Instance Configuration.
 * Optimized for high-load React applications with concurrent request handling.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/";

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    timeout: 10000, // 10s timeout standard for better UX
    headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
});

// State for handling concurrent 401 refreshes
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

// 🔐 Request Interceptor
api.interceptors.request.use(
    config => {
        const token = sessionStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => Promise.reject(error)
);

// 🔄 Response Interceptor (Optimized for Scalability)
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        // If error is 401 and we aren't already refreshing
        if (error.response?.status === 401 && !originalRequest._retry) {

            if (isRefreshing) {
                // Return a promise that resolves when the token is refreshed
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                })
                    .then(token => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return api(originalRequest);
                    })
                    .catch(err => Promise.reject(err));
            }

            originalRequest._retry = true;
            isRefreshing = true;

            const refreshToken = sessionStorage.getItem("refresh_token");

            if (!refreshToken) {
                isRefreshing = false;
                window.location.href = "/login";
                return Promise.reject(error);
            }

            return new Promise((resolve, reject) => {
                axios.post(`${API_BASE_URL}auth/kn/token/refresh/`, { refresh: refreshToken })
                    .then(({ data }) => {
                        sessionStorage.setItem("token", data.access);
                        api.defaults.headers.common["Authorization"] = `Bearer ${data.access}`;
                        originalRequest.headers.Authorization = `Bearer ${data.access}`;
                        processQueue(null, data.access);
                        resolve(api(originalRequest));
                    })
                    .catch((err) => {
                        processQueue(err, null);
                        sessionStorage.clear();
                        window.location.href = "/login";
                        reject(err);
                    })
                    .finally(() => {
                        isRefreshing = false;
                    });
            });
        }

        // Global Error Handling: Enhance error message for easier debugging
        const customError = {
            ...error,
            message: error.response?.data?.error || error.message || "An unexpected error occurred",
            fields: error.response?.data?.fields || null
        };

        return Promise.reject(customError);
    }
);

export default api;
