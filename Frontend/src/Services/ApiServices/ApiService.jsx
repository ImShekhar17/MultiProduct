import api from '../AuthServices/Api';

/**
 * ApiService.jsx
 * Professional API Service Module.
 * 
 * Features:
 * - Centralized Error Handling
 * - Auto-Authentication (via Axios Interceptors)
 * - Standardized Response Format
 */

// --- Internal Utilities ---

const handleResponse = (response) => {
    return response.data;
};

const handleError = (error) => {
    if (import.meta.env.DEV) {
        console.error("API Service Error:", error.message, error.response?.data);
    }
    const errRes = error?.response?.data;
    return {
        success: false,
        status: error?.response?.status || 500,
        message: errRes?.error || errRes?.message || errRes?.detail || error.message || "An unexpected error occurred.",
        fields: errRes?.fields || null,
        errors: errRes
    };
};

// --- Generic wrappers ---

export const getApiData = async (endpoint, config = {}) => {
    try {
        const response = await api.get(endpoint, config);
        return handleResponse(response);
    } catch (error) {
        return handleError(error);
    }
};

export const postData = async (endpoint, data, config = {}) => {
    try {
        const response = await api.post(endpoint, data, config);
        return handleResponse(response);
    } catch (error) {
        return handleError(error);
    }
};

export const patchData = async (endpoint, data, config = {}) => {
    try {
        const response = await api.patch(endpoint, data, config);
        return handleResponse(response);
    } catch (error) {
        return handleError(error);
    }
};

export const putData = async (endpoint, data, config = {}) => {
    try {
        const response = await api.put(endpoint, data, config);
        return handleResponse(response);
    } catch (error) {
        return handleError(error);
    }
};

export const deleteData = async (endpoint, config = {}) => {
    try {
        const response = await api.delete(endpoint, config);
        return handleResponse(response);
    } catch (error) {
        return handleError(error);
    }
};


// =========================== AUTHENTICATION ===================

export const register = (data) => postData('auth/kn/signup/', data);
export const login = (data) => postData('auth/kn/login/', data);
export const OtpValidate = (data) => postData('auth/kn/verifyotp/', data);
export const resendOtp = (data) => postData('auth/kn/resend-otp/', data);
export const forgotPassword = (data) => postData('auth/kn/password-reset-request/', data);
export const resetPassword = ({ new_password, confirm_password, uidb64, token }) => {
    return postData(`auth/kn/password-reset-confirm/?uid=${uidb64}&token=${token}`, { new_password, confirm_password });
};
export const socialLoginAction = (data) => postData('auth/kn/social/token/', data);
export const checkUsernameAvailability = (username) => getApiData(`auth/kn/check-username/?username=${username}`);
export const createRole = (data) => postData('auth/kn/role/', data);


// =========================== STOREFRONT / PRODUCTS ===================

export const getProducts = () => getApiData('services/products/');
export const getProductDetail = (productId) => getApiData(`services/products/${productId}/`);


// =========================== SUBSCRIPTIONS ===================

export const getAvailablePlans = () => getApiData('services/subscriptions/');
export const getUserSubscriptions = () => getApiData('services/subscriptions/list/');
export const startTrial = () => postData('services/subscriptions/trial/start/');
export const purchaseSubscription = (data) => postData('services/subscriptions/purchase/', data);
export const cancelSubscription = (subscriptionId) => postData(`services/subscriptions/${subscriptionId}/cancel/`);
export const renewSubscription = (subscriptionId) => postData(`services/subscriptions/${subscriptionId}/renew/`);


// =========================== INVOICES & PAYMENTS ===================

export const createInvoice = (data) => postData('services/invoice/create/', data);
export const processPayment = (data) => postData('services/payment/process/', data);
export const getInvoices = () => getApiData('services/invoices/');


// =========================== NOTIFICATIONS ===================

export const getNotifications = () => getApiData('services/notifications/');
export const markNotificationRead = (id) => patchData(`services/notifications/${id}/read/`);


export default {
    getApiData,
    postData,
    patchData,
    putData,
    deleteData,
    register,
    login,
    OtpValidate,
    resendOtp,
    forgotPassword,
    resetPassword,
    socialLoginAction,
    checkUsernameAvailability,
    createRole,
    getProducts,
    getProductDetail,
    getAvailablePlans,
    getUserSubscriptions,
    startTrial,
    purchaseSubscription,
    cancelSubscription,
    renewSubscription,
    createInvoice,
    processPayment,
    getInvoices,
    getNotifications,
    markNotificationRead,
};
