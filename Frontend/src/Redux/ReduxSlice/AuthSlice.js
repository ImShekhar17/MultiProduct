import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import AuthService from '../../Services/AuthServices/AuthService';
import * as ApiService from '../../Services/ApiServices/ApiService';
import { addNotification } from './NotificationSlice';

/**
 * Professional Auth Slice.
 * Replaces the React Context logic with a high-performance Redux state.
 * Syncs automatically with sessionStorage for persistence.
 */

// --- Async Thunks ---

export const signup = createAsyncThunk('auth/signup', async (userData, { dispatch, rejectWithValue }) => {
    try {
        const response = await AuthService.signup(userData);
        if (response.success === false) return rejectWithValue(response.message);

        dispatch(addNotification({
            title: "Account Created",
            desc: "Your account has been successfully created. Please verify your OTP.",
            type: "success"
        }));
        return response;
    } catch (error) {
        dispatch(addNotification({
            title: "Signup Failed",
            desc: error.message || "An error occurred during signup.",
            type: "error"
        }));
        return rejectWithValue(error.message);
    }
});

export const verifyOTP = createAsyncThunk('auth/verifyOTP', async (otpData, { dispatch, rejectWithValue }) => {
    try {
        const { email, otp } = otpData;
        const response = await AuthService.verifyOTP(email, otp);
        if (response.success === false) return rejectWithValue(response.message);

        dispatch(addNotification({
            title: "OTP Verified",
            desc: "Your email has been successfully verified.",
            type: "success"
        }));
        return response;
    } catch (error) {
        dispatch(addNotification({
            title: "Verification Failed",
            desc: error.message || "Invalid or expired OTP.",
            type: "error"
        }));
        return rejectWithValue(error.message);
    }
});

export const resendOTP = createAsyncThunk('auth/resendOTP', async (email, { dispatch, rejectWithValue }) => {
    try {
        const response = await AuthService.resendOTP(email);
        if (response.success === false) return rejectWithValue(response.message);

        dispatch(addNotification({
            title: "OTP Sent",
            desc: "A new OTP has been sent to your email.",
            type: "success"
        }));
        return response;
    } catch (error) {
        dispatch(addNotification({
            title: "OTP Reset Failed",
            desc: error.message || "Unable to resend OTP at this time.",
            type: "error"
        }));
        return rejectWithValue(error.message);
    }
});

export const login = createAsyncThunk('auth/login', async (credentials, { dispatch, rejectWithValue }) => {
    try {
        const response = await AuthService.login(credentials);
        if (response.success === false) return rejectWithValue(response.message);

        dispatch(addNotification({
            title: "Login Successful",
            desc: `Welcome back!`,
            type: "success"
        }));
        return response;
    } catch (error) {
        dispatch(addNotification({
            title: "Login Failed",
            desc: error.message || "Invalid credentials. Please try again.",
            type: "error"
        }));
        return rejectWithValue(error.message);
    }
});

export const forgotPassword = createAsyncThunk('auth/forgotPassword', async (emailData, { dispatch, rejectWithValue }) => {
    try {
        const response = await ApiService.forgotPassword(emailData);
        if (response.success === false) return rejectWithValue(response.message);

        dispatch(addNotification({
            title: "Reset Email Sent",
            desc: "Please check your inbox for password reset instructions.",
            type: "success"
        }));
        return response;
    } catch (error) {
        dispatch(addNotification({
            title: "Request Failed",
            desc: error.message || "Unable to process password reset request.",
            type: "error"
        }));
        return rejectWithValue(error.message);
    }
});

export const resetPassword = createAsyncThunk('auth/resetPassword', async (resetData, { dispatch, rejectWithValue }) => {
    try {
        const response = await ApiService.resetPassword(resetData);
        if (response.success === false) return rejectWithValue(response.message);

        dispatch(addNotification({
            title: "Password Reset",
            desc: "Your password has been successfully updated.",
            type: "success"
        }));
        return response;
    } catch (error) {
        dispatch(addNotification({
            title: "Reset Failed",
            desc: error.message || "Unable to reset password. Link may be expired.",
            type: "error"
        }));
        return rejectWithValue(error.message);
    }
});

export const socialLogin = createAsyncThunk('auth/socialLogin', async (data, { dispatch, rejectWithValue }) => {
    try {
        const response = await ApiService.socialLoginAction(data);
        if (response.success === false) return rejectWithValue(response.message);

        dispatch(addNotification({
            title: "Social Login Successful",
            desc: `Welcome back!`,
            type: "success"
        }));
        return response;
    } catch (error) {
        dispatch(addNotification({
            title: "Social Login Failed",
            desc: error.message || "Social authentication failed.",
            type: "error"
        }));
        return rejectWithValue(error.message);
    }
});

export const checkUsername = createAsyncThunk('auth/checkUsername', async (username, { dispatch, rejectWithValue }) => {
    try {
        const response = await ApiService.checkUsernameAvailability(username);
        if (response.success === false) return rejectWithValue(response.message);
        return response;
    } catch (error) {
        if (error.status !== 400) {
            dispatch(addNotification({
                title: "System Error",
                desc: "Could not verify username availability.",
                type: "error"
            }));
        }
        return rejectWithValue(error.message);
    }
});

const initialState = {
    token: sessionStorage.getItem('token') || null,
    refreshToken: sessionStorage.getItem('refresh_token') || null,
    user: JSON.parse(sessionStorage.getItem('user')) || null,
    isAuthenticated: !!sessionStorage.getItem('token'),
    loading: false,
    error: null,
    usernameStatus: null, // For checkUsername
    usernameMessage: '',  // For API messages (Available/Taken)
    usernameSuggestions: [], // For suggestions
};

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        setAuthData: (state, action) => {
            const { token, refreshToken, user } = action.payload;
            state.token = token;
            state.refreshToken = refreshToken;
            state.user = user;
            state.isAuthenticated = true;
            state.error = null;
        },
        clearAuthData: (state) => {
            state.token = null;
            state.refreshToken = null;
            state.user = null;
            state.isAuthenticated = false;
            state.error = null;
            AuthService.logout();
        },
        updateToken: (state, action) => {
            state.token = action.payload;
            sessionStorage.setItem('token', action.payload);
        },
        resetUsernameStatus: (state) => {
            state.usernameStatus = null;
            state.usernameMessage = '';
            state.usernameSuggestions = [];
        },
        clearError: (state) => {
            state.error = null;
        }
    },
    extraReducers: (builder) => {
        builder
            // Login & Social Login
            .addCase(login.pending, (state) => { state.loading = true; state.error = null; })
            .addCase(login.fulfilled, (state, action) => {
                state.loading = false;
                state.token = action.payload.access;
                state.refreshToken = action.payload.refresh;
                state.user = action.payload.user;
                state.isAuthenticated = true;
            })
            .addCase(login.rejected, (state, action) => { state.loading = false; state.error = action.payload; })

            .addCase(socialLogin.pending, (state) => { state.loading = true; state.error = null; })
            .addCase(socialLogin.fulfilled, (state, action) => {
                state.loading = false;
                state.token = action.payload.access;
                state.refreshToken = action.payload.refresh;
                state.user = action.payload.user;
                state.isAuthenticated = true;
            })
            .addCase(socialLogin.rejected, (state, action) => { state.loading = false; state.error = action.payload; })

            // Signup
            .addCase(signup.pending, (state) => { state.loading = true; state.error = null; })
            .addCase(signup.fulfilled, (state) => { state.loading = false; })
            .addCase(signup.rejected, (state, action) => { state.loading = false; state.error = action.payload; })

            // Username Check
            .addCase(checkUsername.pending, (state) => { state.usernameStatus = 'loading'; })
            .addCase(checkUsername.fulfilled, (state, action) => {
                state.usernameStatus = action.payload.available ? 'available' : 'taken';
                state.usernameMessage = action.payload.message || '';
                state.usernameSuggestions = action.payload.suggestions || [];
            })
            .addCase(checkUsername.rejected, (state) => { state.usernameStatus = 'error'; })

            // OTP Verification
            .addCase(verifyOTP.pending, (state) => { state.loading = true; state.error = null; })
            .addCase(verifyOTP.fulfilled, (state) => { state.loading = false; })
            .addCase(verifyOTP.rejected, (state, action) => { state.loading = false; state.error = action.payload; })

            // Resend OTP
            .addCase(resendOTP.pending, (state) => { state.loading = true; state.error = null; })
            .addCase(resendOTP.fulfilled, (state) => { state.loading = false; })
            .addCase(resendOTP.rejected, (state, action) => { state.loading = false; state.error = action.payload; })

            // Password Reset
            .addCase(forgotPassword.pending, (state) => { state.loading = true; state.error = null; })
            .addCase(forgotPassword.fulfilled, (state) => { state.loading = false; })
            .addCase(forgotPassword.rejected, (state, action) => { state.loading = false; state.error = action.payload; })

            .addCase(resetPassword.pending, (state) => { state.loading = true; state.error = null; })
            .addCase(resetPassword.fulfilled, (state) => { state.loading = false; })
            .addCase(resetPassword.rejected, (state, action) => { state.loading = false; state.error = action.payload; });
    }
});

export const { setAuthData, clearAuthData, updateToken, resetUsernameStatus, clearError } = authSlice.actions;

// Selectors for easy consumption in components
export const selectAuth = (state) => state.auth;
export const selectUser = (state) => state.auth.user;
export const selectIsAuthenticated = (state) => state.auth.isAuthenticated;

export default authSlice.reducer;
