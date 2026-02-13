import api from './Api';

// Industry standard: Encapsulated Auth logic for modularity and high-load scalability
const AuthService = {
    /**
     * Registers a new user and triggers OTP flow.
     * @param {Object} userData - { email, username, first_name, last_name, password }
     */
    async signup(userData) {
        const response = await api.post('auth/kn/signup/', userData);
        return response.data;
    },


    /**
     * Verifies the 6-digit OTP sent during signup/login.
     * @param {string} email 
     * @param {string} otp 
     */
    async verifyOTP(email, otp) {
        const response = await api.post('auth/kn/verifyotp/', { email, otp });
        // Auto-login or proceed to password login depending on flow
        return response.data;
    },

    /**
     * Resends OTP to the specified email with rate-limiting support.
     * @param {string} email 
     */
    async resendOTP(email) {
        const response = await api.post('auth/kn/resend-otp/', { email });
        return response.data;
    },

    /**
     * Professional role-based login.
     * Supports Email/Password or Phone/Password combinations.
     * @param {Object} credentials - { email, phone_number, password, otp }
     */
    async login(credentials) {
        const response = await api.post('auth/kn/login/', credentials);
        if (response.data.access) {
            sessionStorage.setItem('token', response.data.access);
            sessionStorage.setItem('refresh_token', response.data.refresh);
            sessionStorage.setItem('user', JSON.stringify(response.data.user));
        }
        return response.data;
    },


    /**
     * Clears session and tokens for a professional logout experience.
     */
    logout() {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('refresh_token');
        sessionStorage.removeItem('user');
    },

    /**
     * Retrieves current user data from storage.
     */
    getCurrentUser() {
        const user = sessionStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
};

export default AuthService;
