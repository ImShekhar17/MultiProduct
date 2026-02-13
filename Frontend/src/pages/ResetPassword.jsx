import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, Lock, ShieldCheck, ArrowRight, Loader2, Eye, EyeOff } from 'lucide-react';
import { Link, useSearchParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { resetPassword, selectAuth, clearError } from '../Redux/ReduxSlice/AuthSlice';

const ResetPassword = () => {
    const [searchParams] = useSearchParams();
    const dispatch = useDispatch();
    const { loading, error: reduxError } = useSelector(selectAuth);

    const [step, setStep] = useState(1); // 1: Reset Form, 2: Success
    const [showPassword, setShowPassword] = useState(false);

    // Clear global errors on mount and unmount for a professional UI experience
    useEffect(() => {
        dispatch(clearError());
        return () => dispatch(clearError());
    }, [dispatch]);

    const [passwords, setPasswords] = useState({
        new: '',
        confirm: ''
    });
    const [localError, setLocalError] = useState('');

    // Enhanced handler to clear errors on interaction
    const handleInputChange = (field) => (e) => {
        setPasswords({ ...passwords, [field]: e.target.value });
        if (localError) setLocalError('');
        if (reduxError) dispatch(clearError());
    };

    const handleReset = async (e) => {
        e.preventDefault();
        setLocalError('');

        if (passwords.new !== passwords.confirm) {
            setLocalError('The encryption sequences do not match.');
            return;
        }

        const uidb64 = searchParams.get('uid');
        const token = searchParams.get('token');

        if (!uidb64 || !token) {
            setLocalError('Invalid or expired reset link. Please request a new one.');
            return;
        }

        const result = await dispatch(resetPassword({
            new_password: passwords.new,
            confirm_password: passwords.confirm,
            uidb64,
            token
        }));

        if (resetPassword.fulfilled.match(result)) {
            setStep(2);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA] dark:bg-[#050505] p-4 md:p-6 relative overflow-hidden">
            {/* Background patterns */}
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden opacity-20 dark:opacity-10">
                <div className="absolute top-[20%] right-[10%] w-[40%] h-[40%] bg-apple-blue rounded-full blur-[150px]" />
                <div className="absolute bottom-[20%] left-[10%] w-[40%] h-[40%] bg-apple-violet rounded-full blur-[150px]" />
            </div>

            <Link to="/login" className="absolute top-6 left-6 md:top-8 md:left-8 flex items-center gap-2 z-20 group">
                <div className="bg-gradient-to-tr from-apple-indigo to-apple-violet p-1.5 rounded-lg shadow-lg">
                    <Layers className="w-5 h-5 text-white" />
                </div>
                <span className="text-base md:text-lg font-bold text-apple-slate dark:text-white tracking-tight">MultiProduct</span>
            </Link>

            <div className="w-full max-w-lg relative z-10">
                <AnimatePresence mode="wait">
                    {step === 1 ? (
                        <motion.div
                            key="reset-step"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 1.05 }}
                            className="bento-card p-6 md:p-12"
                        >
                            <div className="w-16 h-16 md:w-20 md:h-20 bg-apple-blue/10 rounded-[24px] md:rounded-[28px] flex items-center justify-center mx-auto mb-6 md:mb-8 shadow-inner">
                                <ShieldCheck className="w-8 h-8 md:w-10 md:h-10 text-apple-blue" />
                            </div>

                            <div className="text-center mb-8 md:mb-10">
                                <h1 className="text-2xl md:text-4xl font-black tracking-tight mb-3">Reset Password</h1>
                                <p className="text-sm md:text-base text-apple-slate/60 dark:text-gray-400 font-medium leading-relaxed max-w-sm mx-auto">
                                    Define a new encryption sequence to restore <br /> full access to your account.
                                </p>
                            </div>

                            {(localError || reduxError) && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mb-8 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] md:text-xs font-black uppercase tracking-widest text-center"
                                >
                                    {localError || reduxError}
                                </motion.div>
                            )}

                            <form onSubmit={handleReset} className="space-y-5 md:space-y-6">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black uppercase tracking-[0.2em] text-apple-slate/40 dark:text-gray-500 px-1">
                                        New Password
                                    </label>
                                    <div className="relative group">
                                        <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none text-apple-slate/20 group-focus-within:text-apple-violet transition-all">
                                            <Lock className="w-5 h-5" />
                                        </div>
                                        <input
                                            type={showPassword ? "text" : "password"}
                                            required
                                            value={passwords.new}
                                            onChange={handleInputChange('new')}
                                            placeholder="••••••••"
                                            className="w-full pl-12 md:pl-14 pr-12 md:pr-14 py-4 md:py-4.5 rounded-[20px] md:rounded-[22px] bg-white dark:bg-white/5 border border-apple-slate/10 dark:border-white/10 focus:outline-none focus:ring-4 focus:ring-apple-violet/10 focus:border-apple-violet transition-all font-bold text-base md:text-lg"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="absolute inset-y-0 right-0 pr-5 flex items-center text-apple-slate/20 hover:text-apple-slate transition-colors"
                                        >
                                            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                        </button>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-[10px] font-black uppercase tracking-[0.2em] text-apple-slate/40 dark:text-gray-500 px-1">
                                        Confirm Sequence
                                    </label>
                                    <div className="relative group">
                                        <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none text-apple-slate/20 group-focus-within:text-apple-violet transition-all">
                                            <ShieldCheck className="w-5 h-5" />
                                        </div>
                                        <input
                                            type={showPassword ? "text" : "password"}
                                            required
                                            value={passwords.confirm}
                                            onChange={handleInputChange('confirm')}
                                            placeholder="••••••••"
                                            className="w-full pl-12 md:pl-14 pr-6 py-4 md:py-4.5 rounded-[20px] md:rounded-[22px] bg-white dark:bg-white/5 border border-apple-slate/10 dark:border-white/10 focus:outline-none focus:ring-4 focus:ring-apple-violet/10 focus:border-apple-violet transition-all font-bold text-base md:text-lg"
                                        />
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full py-4.5 md:py-5 rounded-[20px] md:rounded-[22px] bg-apple-slate dark:bg-white text-white dark:text-apple-slate font-black text-base md:text-lg shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3 group disabled:opacity-70"
                                >
                                    {loading ? (
                                        <Loader2 className="w-6 h-6 animate-spin" />
                                    ) : (
                                        <>
                                            Renew Security Key
                                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                        </>
                                    )}
                                </button>
                            </form>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="success-step"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bento-card p-6 md:p-12 text-center"
                        >
                            <div className="w-20 h-20 md:w-24 md:h-24 bg-apple-indigo/10 rounded-[28px] md:rounded-[32px] flex items-center justify-center mx-auto mb-6 md:mb-8 shadow-inner">
                                <div className="bg-gradient-to-tr from-apple-indigo to-apple-violet p-3 md:p-4 rounded-xl md:rounded-2xl shadow-lg">
                                    <Lock className="w-6 h-6 md:w-8 md:h-8 text-white" />
                                </div>
                            </div>

                            <h1 className="text-2xl md:text-4xl font-black tracking-tight mb-4">Access Restored</h1>
                            <p className="text-sm md:text-base text-apple-slate/60 dark:text-gray-400 font-medium leading-relaxed mb-8 md:mb-10 max-w-sm mx-auto">
                                Your encryption sequence has been updated. <br />
                                You can now return to the authentication gate.
                            </p>

                            <Link
                                to="/login"
                                className="w-full py-4.5 md:py-5 inline-block rounded-[20px] md:rounded-[22px] bg-apple-slate dark:bg-white text-white dark:text-apple-slate font-black text-base md:text-lg shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all"
                            >
                                Enter Dashboard
                            </Link>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default ResetPassword;
