import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, Mail, Lock, ArrowRight, Github, Chrome, CheckCircle2, Eye, EyeOff, Loader2 } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { login, verifyOTP, socialLogin, resendOTP, selectAuth, clearError } from '../Redux/ReduxSlice/AuthSlice';

const Login = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const { loading: isLoading, error: reduxError } = useSelector(selectAuth);

    const [step, setStep] = useState(1); // 1: Login Form, 2: OTP Verification
    const [loginMethod, setLoginMethod] = useState('password'); // 'password' | 'otp'
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [showPassword, setShowPassword] = useState(false);
    const [localError, setLocalError] = useState('');

    // Clear global errors on mount and unmount for a professional UI experience
    useEffect(() => {
        dispatch(clearError());
        return () => dispatch(clearError());
    }, [dispatch]);

    // Enhanced handler to clear errors on interaction
    const handleInputChange = (setter) => (e) => {
        setter(e.target.value);
        if (localError) setLocalError('');
        if (reduxError) dispatch(clearError());
    };

    const error = reduxError || localError;

    const handleLogin = async (e) => {
        e.preventDefault();
        setLocalError('');

        if (loginMethod === 'password') {
            const result = await dispatch(login({ email, password }));
            if (login.fulfilled.match(result)) {
                navigate('/dashboard');
            }
        } else {
            // For OTP login method, we might need a specific backend endpoint or use login with a flag
            // For now, let's assume login handles sending OTP if requested, or we use resendOTP
            const result = await dispatch(resendOTP(email));
            if (resendOTP.fulfilled.match(result)) {
                setStep(2);
            }
        }
    };

    const handleSocialLogin = async (provider) => {
        // Implementation for social login
        const result = await dispatch(socialLogin({ provider, token: 'dummy_token' }));
        if (socialLogin.fulfilled.match(result)) {
            navigate('/dashboard');
        }
    };

    const handleOTPVerify = async (e) => {
        e.preventDefault();
        setLocalError('');
        const otpString = otp.join('');
        const result = await dispatch(verifyOTP({ email, otp: otpString }));
        if (verifyOTP.fulfilled.match(result)) {
            navigate('/dashboard');
        }
    };

    const handleOtpChange = (index, value) => {
        if (isNaN(value)) return;
        const newOtp = [...otp];
        newOtp[index] = value.slice(-1); // Only take last character
        setOtp(newOtp);

        if (localError) setLocalError('');
        if (reduxError) dispatch(clearError());

        // Auto focus next
        if (value !== '' && index < 5) {
            const nextInput = document.getElementById(`otp-${index + 1}`);
            nextInput?.focus();
        }
    };

    const handleKeyDown = (index, e) => {
        if (e.key === 'Backspace' && otp[index] === '' && index > 0) {
            const prevInput = document.getElementById(`otp-${index - 1}`);
            prevInput?.focus();
        }
    };

    const handlePaste = (e) => {
        e.preventDefault();
        const data = e.clipboardData.getData('text').slice(0, 6).split('');
        if (data.length === 6 && data.every(char => !isNaN(char))) {
            setOtp(data);
            const lastInput = document.getElementById(`otp-5`);
            lastInput?.focus();
        }
    };

    return (
        <div className="min-h-screen flex flex-col md:flex-row bg-[#FAFAFA] dark:bg-[#050505]">
            {/* Left Side: Branding */}
            <div className="hidden md:flex flex-1 relative overflow-hidden bg-apple-slate dark:bg-black p-16 flex-col justify-between">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-apple-indigo/20 rounded-full blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-apple-violet/20 rounded-full blur-[120px]" />

                <Link to="/" className="flex items-center gap-2 relative z-10 group">
                    <div className="bg-gradient-to-tr from-apple-indigo to-apple-violet p-2 rounded-xl shadow-lg">
                        <Layers className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-xl font-bold text-white tracking-tight">MultiProduct</span>
                </Link>

                <div className="relative z-10 p-8 lg:p-12">
                    <motion.h2
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="text-4xl lg:text-6xl font-black text-white leading-tight mb-8"
                    >
                        Design. <br />
                        Integrate. <br />
                        <span className="bg-gradient-to-r from-apple-violet to-apple-indigo bg-clip-text text-transparent">Scale.</span>
                    </motion.h2>
                    <p className="text-white/50 text-base md:text-lg max-w-sm leading-relaxed font-medium">
                        Experience the most unique SaaS management platform. Clean, fast, and integrated with your Stark-grade infrastructure.
                    </p>
                </div>

                <div className="relative z-10 flex gap-4 text-white/30 text-xs md:sm font-medium p-8 md:p-12 mt-auto">
                    <span>&copy; 2025 MultiProduct</span>
                    <span>&bull;</span>
                    <span>Privacy</span>
                    <span>&bull;</span>
                    <span>Terms</span>
                </div>
            </div>

            {/* Right Side: Authentication Forms */}
            <div className="flex-1 flex items-center justify-center p-5 md:p-12 lg:p-20 relative overflow-hidden">
                <div className="w-full max-w-md relative z-10">
                    <AnimatePresence mode="wait">
                        {step === 1 ? (
                            <motion.div
                                key="login-step"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                transition={{ duration: 0.5 }}
                            >
                                <div className="mb-8 md:mb-10 text-center md:text-left">
                                    <h1 className="text-3xl md:text-4xl font-black tracking-tight mb-3">Welcome Back</h1>
                                    <p className="text-apple-slate/60 dark:text-gray-400 font-medium">Choose your preferred login method.</p>
                                </div>

                                {/* Method Switcher */}
                                <div className="flex p-1.5 bg-apple-slate/5 dark:bg-white/5 rounded-[20px] mb-8 border border-apple-slate/10 dark:border-white/10">
                                    <button
                                        onClick={() => setLoginMethod('password')}
                                        className={`flex-1 py-3 px-4 rounded-[16px] text-sm font-black transition-all ${loginMethod === 'password' ? 'bg-white dark:bg-apple-slate shadow-xl scale-100' : 'opacity-40 hover:opacity-100 text-apple-slate dark:text-white'}`}
                                    >
                                        Password
                                    </button>
                                    <button
                                        onClick={() => setLoginMethod('otp')}
                                        className={`flex-1 py-3 px-4 rounded-[16px] text-sm font-black transition-all ${loginMethod === 'otp' ? 'bg-white dark:bg-apple-slate shadow-xl scale-100' : 'opacity-40 hover:opacity-100 text-apple-slate dark:text-white'}`}
                                    >
                                        OTP Login
                                    </button>
                                </div>

                                {error && (
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className="mb-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm font-bold text-center"
                                    >
                                        {error}
                                    </motion.div>
                                )}

                                <form onSubmit={handleLogin} className="space-y-5">
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black uppercase tracking-[0.2em] text-apple-slate/40 dark:text-gray-500 px-1">
                                            Email Address
                                        </label>
                                        <div className="relative group">
                                            <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none text-apple-slate/20 group-focus-within:text-apple-violet transition-all">
                                                <Mail className="w-5 h-5" />
                                            </div>
                                            <input
                                                type="email"
                                                required
                                                value={email}
                                                onChange={handleInputChange(setEmail)}
                                                placeholder="name@company.com"
                                                className="w-full pl-14 pr-6 py-4.5 rounded-[22px] bg-white dark:bg-white/5 border border-apple-slate/10 dark:border-white/10 focus:outline-none focus:ring-4 focus:ring-apple-violet/10 focus:border-apple-violet transition-all font-bold text-lg"
                                            />
                                        </div>
                                    </div>

                                    <AnimatePresence mode="popLayout">
                                        {loginMethod === 'password' && (
                                            <motion.div
                                                initial={{ opacity: 0, height: 0 }}
                                                animate={{ opacity: 1, height: 'auto' }}
                                                exit={{ opacity: 0, height: 0 }}
                                                className="space-y-2 overflow-hidden"
                                            >
                                                <div className="flex justify-between items-center px-1">
                                                    <label className="text-[10px] font-black uppercase tracking-[0.2em] text-apple-slate/40 dark:text-gray-500">
                                                        Password
                                                    </label>
                                                    <Link to="/forgot-password" size="sm" className="text-[10px] font-black uppercase tracking-[0.1em] text-apple-violet hover:underline">
                                                        Forgot?
                                                    </Link>
                                                </div>
                                                <div className="relative group">
                                                    <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none text-apple-slate/20 group-focus-within:text-apple-violet transition-all">
                                                        <Lock className="w-5 h-5" />
                                                    </div>
                                                    <input
                                                        type={showPassword ? "text" : "password"}
                                                        required={loginMethod === 'password'}
                                                        value={password}
                                                        onChange={handleInputChange(setPassword)}
                                                        placeholder="••••••••"
                                                        className="w-full pl-14 pr-14 py-4.5 rounded-[22px] bg-white dark:bg-white/5 border border-apple-slate/10 dark:border-white/10 focus:outline-none focus:ring-4 focus:ring-apple-violet/10 focus:border-apple-violet transition-all font-bold text-lg"
                                                    />
                                                    <button
                                                        type="button"
                                                        onClick={() => setShowPassword(!showPassword)}
                                                        className="absolute inset-y-0 right-0 pr-5 flex items-center text-apple-slate/20 hover:text-apple-slate transition-colors"
                                                    >
                                                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                                    </button>
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>

                                    <button
                                        type="submit"
                                        disabled={isLoading}
                                        className="w-full py-5 rounded-[22px] bg-apple-slate dark:bg-white text-white dark:text-apple-slate font-black text-lg shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3 group relative disabled:opacity-70 disabled:hover:scale-100"
                                    >
                                        {isLoading ? (
                                            <Loader2 className="w-6 h-6 animate-spin" />
                                        ) : (
                                            <>
                                                {loginMethod === 'password' ? 'Secure Login' : 'Send Code'}
                                                <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                                            </>
                                        )}
                                    </button>
                                </form>

                                <div className="my-10 flex items-center gap-4">
                                    <div className="h-px flex-1 bg-apple-slate/10 dark:bg-white/10" />
                                    <span className="text-[10px] font-black text-apple-slate/30 dark:text-gray-600 uppercase tracking-[0.3em]">Identity Hub</span>
                                    <div className="h-px flex-1 bg-apple-slate/10 dark:bg-white/10" />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <button
                                        onClick={() => handleSocialLogin('google')}
                                        disabled={isLoading}
                                        className="flex items-center justify-center gap-3 py-4 rounded-[20px] border border-apple-slate/10 dark:border-white/10 hover:bg-apple-slate/5 dark:hover:bg-white/5 transition-all font-black text-sm group disabled:opacity-50"
                                    >
                                        <Chrome className="w-5 h-5 group-hover:scale-110 transition-transform" /> Google
                                    </button>
                                    <button
                                        onClick={() => handleSocialLogin('github')}
                                        disabled={isLoading}
                                        className="flex items-center justify-center gap-3 py-4 rounded-[20px] border border-apple-slate/10 dark:border-white/10 hover:bg-apple-slate/5 dark:hover:bg-white/5 transition-all font-black text-sm group disabled:opacity-50"
                                    >
                                        <Github className="w-5 h-5 group-hover:scale-110 transition-transform" /> Github
                                    </button>
                                </div>

                                <p className="mt-12 text-center text-apple-slate/60 dark:text-gray-400 font-bold">
                                    New to the interface? <Link to="/signup" className="text-apple-violet font-black hover:underline ml-1">Create Account</Link>
                                </p>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="otp-step"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                transition={{ duration: 0.5 }}
                                className="text-center"
                            >
                                <div className="mb-10">
                                    <div className="w-24 h-24 bg-apple-violet/10 rounded-[32px] flex items-center justify-center mx-auto mb-8 shadow-inner relative group">
                                        <div className="absolute inset-0 bg-apple-violet/5 rounded-[32px] animate-ping" />
                                        <CheckCircle2 className="w-12 h-12 text-apple-violet relative z-10" />
                                    </div>
                                    <h1 className="text-4xl font-black tracking-tight mb-4">Verify Identity</h1>
                                    <p className="text-apple-slate/60 dark:text-gray-400 font-medium leading-relaxed">
                                        A distinct 6-digit code has been dispatched to <br />
                                        <span className="text-apple-slate dark:text-white font-black">{email}</span>
                                    </p>
                                </div>

                                {error && (
                                    <div className="mb-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm font-bold">
                                        {error}
                                    </div>
                                )}

                                <div className="flex justify-center gap-2 md:gap-4 mb-10" onPaste={handlePaste}>
                                    {otp.map((digit, i) => (
                                        <input
                                            key={i}
                                            id={`otp-${i}`}
                                            type="text"
                                            maxLength={1}
                                            value={digit}
                                            onChange={(e) => handleOtpChange(i, e.target.value)}
                                            onKeyDown={(e) => handleKeyDown(i, e)}
                                            className="w-12 h-16 md:w-16 md:h-20 text-center text-2xl md:text-3xl font-black rounded-[18px] md:rounded-[22px] bg-white dark:bg-white/5 border border-apple-slate/10 dark:border-white/10 focus:outline-none focus:ring-4 focus:ring-apple-violet/10 focus:border-apple-violet transition-all shadow-sm"
                                            autoFocus={i === 0}
                                        />
                                    ))}
                                </div>

                                <button
                                    onClick={handleOTPVerify}
                                    disabled={isLoading || otp.includes('')}
                                    className="w-full py-5 rounded-[22px] bg-apple-slate dark:bg-white text-white dark:text-apple-slate font-black text-lg shadow-2xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
                                >
                                    {isLoading ? <Loader2 className="w-6 h-6 animate-spin mx-auto" /> : 'Complete Secure Login'}
                                </button>

                                <div className="mt-12 space-y-6">
                                    <p className="text-apple-slate/60 dark:text-gray-400 font-bold">
                                        Didn't receive the sequence? <button onClick={() => dispatch(resendOTP(email))} className="text-apple-violet font-black hover:underline cursor-pointer">Resend OTP</button>
                                    </p>
                                    <button
                                        onClick={() => setStep(1)}
                                        className="text-xs font-black uppercase tracking-[0.2em] text-apple-slate/30 dark:text-gray-600 hover:text-apple-violet transition-colors"
                                    >
                                        Use a different credentials
                                    </button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};

export default Login;
