import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, Mail, User, ArrowRight, Shield, Star, Rocket, CheckCircle2, Loader2, AlertCircle, Check, X, Sparkles } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { signup, verifyOTP, resendOTP, checkUsername, resetUsernameStatus, selectAuth, clearError } from '../Redux/ReduxSlice/AuthSlice';
import { addNotification } from '../Redux/ReduxSlice/NotificationSlice';

const Signup = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const { loading, error: reduxError, usernameStatus, usernameMessage, usernameSuggestions } = useSelector(selectAuth);

    const [step, setStep] = useState(1); // 1: Role, 2: Account, 3: OTP
    const [role, setRole] = useState(null);
    const [showPassword, setShowPassword] = useState(false);

    // Clear global errors on mount and unmount for a professional UI experience
    useEffect(() => {
        dispatch(clearError());
        return () => dispatch(clearError());
    }, [dispatch]);

    const [formData, setFormData] = useState({
        email: '',
        username: '',
        phone_number: '',
        password: '',
        confirmPassword: ''
    });
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [localError, setLocalError] = useState('');

    const error = reduxError || localError;

    // Enhanced handler to clear errors on interaction
    const handleInputChange = (field) => (e) => {
        setFormData({ ...formData, [field]: e.target.value });
        if (localError) setLocalError('');
        if (reduxError) dispatch(clearError());
    };

    const handleOtpChange = (index, value) => {
        if (isNaN(value)) return;
        const newOtp = [...otp];
        newOtp[index] = value.slice(-1);
        setOtp(newOtp);

        if (localError) setLocalError('');
        if (reduxError) dispatch(clearError());

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

    useEffect(() => {
        if (formData.username.length >= 3) {
            const timer = setTimeout(() => {
                dispatch(checkUsername(formData.username));
            }, 500);
            return () => clearTimeout(timer);
        } else {
            dispatch(resetUsernameStatus());
        }
    }, [formData.username, dispatch]);

    const handleAccountSubmit = async (e) => {
        e.preventDefault();
        if (usernameStatus === 'taken') return;

        if (formData.password !== formData.confirmPassword) {
            dispatch(addNotification({
                title: "Validation Error",
                desc: "Passwords do not match.",
                type: "error"
            }));
            return;
        }

        const { email, username, phone_number, password, confirmPassword } = formData;
        const result = await dispatch(signup({
            email,
            username,
            phone_number,
            password,
            confirm_password: confirmPassword,
            role
        }));

        if (signup.fulfilled.match(result)) {
            setStep(3);
        }
    };

    const handleOTPSubmit = async (e) => {
        e.preventDefault();
        const otpString = otp.join('');
        const result = await dispatch(verifyOTP({ email: formData.email, otp: otpString }));
        if (verifyOTP.fulfilled.match(result)) {
            navigate('/login');
        }
    };

    const handleResendOTP = () => {
        dispatch(resendOTP(formData.email));
    };

    const roles = [
        {
            id: 'admin',
            title: 'Administrator',
            desc: 'Full access to system orchestration and multi-product analytics.',
            icon: <Shield className="w-8 h-8" />,
            color: 'from-apple-indigo/20 to-apple-blue/10'
        },
        {
            id: 'subscriber',
            title: 'Subscriber',
            desc: 'Unlock individual SaaS products with premium tools and support.',
            icon: <Star className="w-8 h-8" />,
            color: 'from-apple-violet/20 to-apple-indigo/10'
        },
        {
            id: 'guest',
            title: 'Guest User',
            desc: 'Explore the ecosystem with limited-time trial access.',
            icon: <Rocket className="w-8 h-8" />,
            color: 'from-apple-slate/10 to-transparent'
        }
    ];

    return (
        <div className="min-h-screen bg-[#FAFAFA] dark:bg-deep-midnight flex items-center justify-center p-6 overflow-x-hidden">
            <div className="fixed top-0 left-0 w-full h-full pointer-events-none overflow-hidden opacity-20 dark:opacity-10">
                <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-apple-indigo rounded-full blur-[150px]" />
                <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-apple-violet rounded-full blur-[150px]" />
            </div>

            <div className="w-full max-w-4xl relative z-10 px-4 md:px-0">
                <div className="flex justify-center mb-10 md:mb-12 gap-2">
                    {[1, 2, 3].map((s) => (
                        <div
                            key={s}
                            className={`h-1.5 rounded-full transition-all duration-500 ${s === step ? 'w-10 md:w-12 bg-apple-violet' : 'w-5 md:w-6 bg-apple-slate/10 dark:bg-white/10'
                                } ${s < step ? 'bg-apple-indigo/50' : ''}`}
                        />
                    ))}
                </div>

                <AnimatePresence mode="wait">
                    {step === 1 ? (
                        <motion.div
                            key="step-role"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="text-center"
                        >
                            <h1 className="text-3xl md:text-5xl font-black mb-4 tracking-tight">Choose your role.</h1>
                            <p className="text-apple-slate/60 dark:text-gray-400 mb-10 md:mb-12 max-w-lg mx-auto font-medium">
                                Select the experience that best fits your mission in the MultiProduct ecosystem.
                            </p>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-6">
                                {roles.map((r) => (
                                    <button
                                        key={r.id}
                                        onClick={() => { setRole(r.id); setStep(2); }}
                                        className={`bento-card text-left p-6 md:p-8 group transition-all duration-500 hover:scale-[1.02] active:scale-95 ${role === r.id ? 'ring-2 ring-apple-violet border-transparent' : ''}`}
                                    >
                                        <div className={`mb-6 p-4 rounded-xl md:rounded-2xl bg-gradient-to-br ${r.color} text-apple-violet group-hover:scale-110 transition-transform duration-500 inline-block shadow-sm`}>
                                            {r.icon}
                                        </div>
                                        <h3 className="text-xl md:text-2xl font-bold mb-3">{r.title}</h3>
                                        <p className="text-sm text-apple-slate/50 dark:text-gray-400 leading-relaxed mb-6 font-medium">
                                            {r.desc}
                                        </p>
                                        <div className="flex items-center text-[10px] font-black uppercase tracking-widest text-apple-violet opacity-0 group-hover:opacity-100 transition-opacity">
                                            Select Role <ArrowRight className="w-3 h-3 ml-2 group-hover:translate-x-1 transition-transform" />
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </motion.div>
                    ) : step === 2 ? (
                        <motion.div
                            key="step-details"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="max-w-md mx-auto"
                        >
                            <div className="text-center mb-8 md:mb-10">
                                <h1 className="text-3xl md:text-4xl font-black mb-2 tracking-tight">Create account.</h1>
                                <p className="text-apple-slate/40 dark:text-gray-500 uppercase text-[10px] md:text-xs font-black tracking-widest">
                                    Joining as <span className="text-apple-violet">{role}</span>
                                </p>
                            </div>

                            {error && (
                                <div className="mb-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm font-bold text-center">
                                    {error}
                                </div>
                            )}

                            <form onSubmit={handleAccountSubmit} className="space-y-5 md:space-y-6">
                                <div className="space-y-1.5 md:space-y-2">
                                    <label className="text-xs font-bold uppercase tracking-widest text-apple-slate/40 px-1 text-left block">Email Address</label>
                                    <input
                                        type="email" required placeholder="name@company.com"
                                        className="w-full px-6 py-4 rounded-[18px] bg-white dark:bg-white/5 border border-apple-slate/10 focus:ring-4 focus:ring-apple-violet/10 focus:border-apple-violet transition-all text-lg"
                                        value={formData.email} onChange={handleInputChange('email')}
                                        disabled={loading}
                                    />
                                </div>
                                <div className="space-y-1.5 md:space-y-2">
                                    <div className="flex justify-between px-1">
                                        <label className="text-xs font-bold uppercase tracking-widest text-apple-slate/40">Username</label>
                                        {usernameStatus === 'loading' && <Loader2 className="w-3 h-3 animate-spin text-apple-violet" />}
                                    </div>
                                    <input
                                        type="text" required placeholder="Choose a professional handle"
                                        className={`w-full px-6 py-4 rounded-[18px] bg-white dark:bg-white/5 border transition-all text-lg focus:outline-none focus:ring-4 ${usernameStatus === 'taken' ? 'border-red-500/50 focus:ring-red-500/10 focus:border-red-500' : usernameStatus === 'available' ? 'border-green-500/50 focus:ring-green-500/10 focus:border-green-500' : 'border-apple-slate/10 focus:ring-apple-violet/10 focus:border-apple-violet'}`}
                                        value={formData.username} onChange={handleInputChange('username')}
                                        disabled={loading}
                                        spellCheck="false"
                                    />
                                    <AnimatePresence>
                                        {usernameMessage && (
                                            <motion.p
                                                initial={{ opacity: 0, y: -5 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                className={`text-[10px] font-bold px-1 mt-1 ${usernameStatus === 'available' ? 'text-green-500' : 'text-red-500'}`}
                                            >
                                                {usernameMessage}
                                            </motion.p>
                                        )}
                                    </AnimatePresence>
                                </div>
                                {usernameStatus === 'taken' && usernameSuggestions.length > 0 && (
                                    <div className="flex flex-wrap gap-2 px-1">
                                        {usernameSuggestions.map((s) => (
                                            <button key={s} type="button" onClick={() => setFormData({ ...formData, username: s })} className="px-3 py-2 rounded-xl bg-apple-violet/5 text-apple-violet text-[11px] font-bold border border-apple-violet/10 hover:bg-apple-violet/10">
                                                {s}
                                            </button>
                                        ))}
                                    </div>
                                )}
                                <div className="space-y-1.5 md:space-y-2">
                                    <label className="text-xs font-bold uppercase tracking-widest text-apple-slate/40 px-1 text-left block">Phone Number</label>
                                    <input
                                        type="tel" required placeholder="+919876543210"
                                        className="w-full px-6 py-4 rounded-[18px] bg-white dark:bg-white/5 border border-apple-slate/10 focus:ring-4 focus:ring-apple-violet/10 focus:border-apple-violet transition-all text-lg"
                                        value={formData.phone_number} onChange={handleInputChange('phone_number')}
                                        disabled={loading}
                                    />
                                </div>
                                <div className="space-y-1.5 md:space-y-2">
                                    <label className="text-xs font-bold uppercase tracking-widest text-apple-slate/40 px-1 text-left block">Password</label>
                                    <input
                                        type="password" required placeholder="••••••••"
                                        className="w-full px-6 py-4 rounded-[18px] bg-white dark:bg-white/5 border border-apple-slate/10 focus:ring-4 focus:ring-apple-violet/10 focus:border-apple-violet transition-all text-lg"
                                        value={formData.password} onChange={handleInputChange('password')}
                                        disabled={loading}
                                    />
                                </div>
                                <div className="space-y-1.5 md:space-y-2">
                                    <div className="flex justify-between px-1">
                                        <label className="text-xs font-bold uppercase tracking-widest text-apple-slate/40">Confirm Password</label>
                                        {formData.confirmPassword && (
                                            <span className={`text-[10px] font-bold ${formData.password === formData.confirmPassword ? 'text-green-500' : 'text-red-500'}`}>
                                                {formData.password === formData.confirmPassword ? 'Match' : 'Mismatch'}
                                            </span>
                                        )}
                                    </div>
                                    <input
                                        type="password" required placeholder="••••••••"
                                        className={`w-full px-6 py-4 rounded-[18px] bg-white dark:bg-white/5 border transition-all text-lg focus:outline-none focus:ring-4 ${formData.confirmPassword ? (formData.password === formData.confirmPassword ? 'border-green-500/50 focus:ring-green-500/10 focus:border-green-500' : 'border-red-500/50 focus:ring-red-500/10 focus:border-red-500') : 'border-apple-slate/10 focus:ring-apple-violet/10 focus:border-apple-violet'}`}
                                        value={formData.confirmPassword} onChange={handleInputChange('confirmPassword')}
                                        disabled={loading}
                                    />
                                </div>
                                <button
                                    type="submit" disabled={loading || usernameStatus === 'taken'}
                                    className="w-full py-4 md:py-5 rounded-[22px] bg-apple-violet text-white font-bold text-lg hover:shadow-2xl hover:shadow-apple-violet/30 active:scale-95 transition-all flex items-center justify-center gap-3 group"
                                >
                                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <>Create Account & Verify <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" /></>}
                                </button>
                            </form>
                            <button onClick={() => setStep(1)} className="w-full mt-6 text-sm font-bold text-apple-slate/40 hover:text-apple-violet transition-colors">Go back</button>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="step-otp"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="max-w-md mx-auto text-center"
                        >
                            <div className="mb-10">
                                <div className="w-20 h-20 bg-apple-violet/10 rounded-3xl flex items-center justify-center mx-auto mb-6">
                                    <Mail className="w-10 h-10 text-apple-violet" />
                                </div>
                                <h1 className="text-3xl md:text-4xl font-black mb-3">Verify email.</h1>
                                <p className="text-apple-slate/60 dark:text-gray-400 font-medium px-4">
                                    We've sent a 6-digit verification code to
                                    <br /><span className="text-apple-dark font-black dark:text-white mt-1 block">{formData.email}</span>
                                </p>
                            </div>

                            <form onSubmit={handleOTPSubmit} className="space-y-8">
                                <div className="flex justify-between gap-2 md:gap-3">
                                    {otp.map((digit, index) => (
                                        <input
                                            key={index}
                                            id={`otp-${index}`}
                                            type="text"
                                            maxLength={1}
                                            value={digit}
                                            onChange={(e) => handleOtpChange(index, e.target.value)}
                                            onKeyDown={(e) => handleKeyDown(index, e)}
                                            onPaste={handlePaste}
                                            className="w-full aspect-square text-center text-2xl md:text-3xl font-black rounded-2xl md:rounded-[20px] bg-white dark:bg-white/5 border border-apple-slate/10 dark:border-white/10 focus:ring-4 focus:ring-apple-violet/10 focus:border-apple-violet outline-none transition-all shadow-sm"
                                        />
                                    ))}
                                </div>

                                <div className="space-y-6">
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="w-full py-4 md:py-5 rounded-[22px] bg-apple-violet text-white font-bold text-lg hover:shadow-2xl hover:shadow-apple-violet/30 active:scale-95 transition-all flex items-center justify-center gap-3 group"
                                    >
                                        {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : 'Verify Account'}
                                    </button>

                                    <div className="flex flex-col gap-3">
                                        <div className="flex justify-center gap-2">
                                            <p className="text-sm font-medium text-apple-slate/40">
                                                Didn't receive the code?
                                            </p>
                                            <button
                                                type="button"
                                                onClick={handleResendOTP}
                                                className="text-apple-violet font-black uppercase text-xs tracking-widest hover:opacity-70 transition-opacity"
                                            >
                                                Resend
                                            </button>
                                        </div>
                                        <button
                                            type="button"
                                            onClick={() => setStep(2)}
                                            className="text-sm font-bold text-apple-slate/30 hover:text-apple-violet transition-colors"
                                        >
                                            Change Email/Details
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default Signup;
