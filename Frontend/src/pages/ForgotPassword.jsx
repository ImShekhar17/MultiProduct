import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, Mail, ArrowRight, Loader2, Send } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { forgotPassword, selectAuth, clearError } from '../Redux/ReduxSlice/AuthSlice';

const ForgotPassword = () => {
    const dispatch = useDispatch();
    const { loading, error } = useSelector(selectAuth);
    const [step, setStep] = useState(1); // 1: Request, 2: Success
    const [email, setEmail] = useState('');

    // Clear global errors on mount and unmount for a professional UI experience
    useEffect(() => {
        dispatch(clearError());
        return () => dispatch(clearError());
    }, [dispatch]);

    // Enhanced handler to clear errors on interaction
    const handleInputChange = (setter) => (e) => {
        setter(e.target.value);
        if (error) dispatch(clearError());
    };

    const handleRequest = async (e) => {
        e.preventDefault();
        const result = await dispatch(forgotPassword({ email }));
        if (forgotPassword.fulfilled.match(result)) {
            setStep(2);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA] dark:bg-[#050505] p-4 md:p-6 relative overflow-hidden">
            {/* Background patterns */}
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden opacity-20 dark:opacity-10">
                <div className="absolute -top-[10%] -left-[10%] w-[50%] h-[50%] bg-apple-indigo rounded-full blur-[150px]" />
                <div className="absolute -bottom-[10%] -right-[10%] w-[50%] h-[50%] bg-apple-violet rounded-full blur-[150px]" />
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
                            key="request-step"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="bento-card p-6 md:p-12 text-center"
                        >
                            <div className="w-16 h-16 md:w-20 md:h-20 bg-apple-violet/10 rounded-[24px] md:rounded-[28px] flex items-center justify-center mx-auto mb-6 md:mb-8 shadow-inner">
                                <Mail className="w-8 h-8 md:w-10 md:h-10 text-apple-violet" />
                            </div>

                            <h1 className="text-2xl md:text-4xl font-black tracking-tight mb-3">Forgot Password?</h1>
                            <p className="text-sm md:text-base text-apple-slate/60 dark:text-gray-400 font-medium mb-8 md:mb-10 leading-relaxed max-w-sm mx-auto">
                                No worries. Enter your email and we'll dispatch a secure link to reset your access.
                            </p>

                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mb-8 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] md:text-xs font-black uppercase tracking-widest text-center"
                                >
                                    {error}
                                </motion.div>
                            )}

                            <form onSubmit={handleRequest} className="space-y-5 md:space-y-6">
                                <div className="space-y-2 text-left">
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
                                            Send Reset Link
                                            <Send className="w-5 h-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                                        </>
                                    )}
                                </button>
                            </form>

                            <Link
                                to="/login"
                                className="mt-8 inline-block text-xs font-black uppercase tracking-widest text-apple-slate/40 dark:text-gray-500 hover:text-apple-violet transition-colors"
                            >
                                Back to login
                            </Link>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="success-step"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bento-card p-6 md:p-12 text-center"
                        >
                            <div className="w-20 h-20 md:w-24 md:h-24 bg-green-500/10 rounded-[28px] md:rounded-[32px] flex items-center justify-center mx-auto mb-6 md:mb-8 shadow-inner relative group">
                                <div className="absolute inset-0 bg-green-500/5 rounded-[28px] md:rounded-[32px] animate-ping" />
                                <Send className="w-10 h-10 md:w-12 md:h-12 text-green-500 relative z-10" />
                            </div>

                            <h1 className="text-2xl md:text-4xl font-black tracking-tight mb-4">Link Sent!</h1>
                            <p className="text-sm md:text-base text-apple-slate/60 dark:text-gray-400 font-medium leading-relaxed mb-6 md:mb-8">
                                A secure recovery sequence has been dispatched to <br />
                                <span className="text-apple-slate dark:text-white font-black break-all">{email}</span>
                            </p>

                            <div className="p-4 rounded-xl md:rounded-2xl bg-apple-indigo/5 border border-apple-indigo/10 mb-8 md:mb-10 text-center">
                                <p className="text-[10px] md:text-xs font-bold text-apple-indigo/60 mb-2 uppercase tracking-widest">Dev Shortcut</p>
                                <Link to="/reset-password?uid=stark&token=access" className="text-apple-violet font-black hover:underline text-sm md:text-base">
                                    Simulate Email Link
                                </Link>
                            </div>

                            <Link
                                to="/login"
                                className="w-full py-4.5 md:py-5 inline-block rounded-[20px] md:rounded-[22px] bg-apple-slate dark:bg-white text-white dark:text-apple-slate font-black text-base md:text-lg shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all"
                            >
                                Return to Interface
                            </Link>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default ForgotPassword;
