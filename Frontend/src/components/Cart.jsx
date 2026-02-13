import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSelector, useDispatch } from 'react-redux';
import {
    ShoppingCart, X, Trash2, Plus, Minus, CreditCard,
    Sparkles, ShieldCheck, Zap, ArrowRight, Package
} from 'lucide-react';
import {
    selectCartItems,
    selectCartTotal,
    selectIsCartOpen,
    toggleCart,
    removeFromCart,
    updateQuantity,
    clearCart
} from '../Redux/ReduxSlice/CartSlice';
import { addNotification } from '../Redux/ReduxSlice/NotificationSlice';

const Cart = () => {
    const dispatch = useDispatch();
    const items = useSelector(selectCartItems);
    const totalAmount = useSelector(selectCartTotal);
    const isOpen = useSelector(selectIsCartOpen);

    const handleCheckout = () => {
        dispatch(addNotification({
            title: "Uplink Successful",
            desc: "Your nodes are being provisioned on Stark-Grade infrastructure.",
            type: "success"
        }));
        dispatch(clearCart());
        dispatch(toggleCart());
    };

    const containerVariants = {
        hidden: { x: '100%', opacity: 0.8 },
        visible: {
            x: 0,
            opacity: 1,
            transition: {
                type: 'spring',
                damping: 30,
                stiffness: 350,
                mass: 0.8,
                staggerChildren: 0.05,
                delayChildren: 0.1
            }
        },
        exit: {
            x: '100%',
            opacity: 0,
            transition: {
                type: 'spring',
                damping: 30,
                stiffness: 300,
                mass: 1
            }
        }
    };

    const itemVariants = {
        hidden: { x: 30, opacity: 0 },
        visible: { x: 0, opacity: 1 },
        exit: { x: 20, opacity: 0 }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Spatial Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => dispatch(toggleCart())}
                        className="fixed inset-0 bg-black/60 backdrop-blur-[4px] z-[1001]"
                    />

                    {/* Matrix Side Panel */}
                    <motion.div
                        variants={containerVariants}
                        initial="hidden"
                        animate="visible"
                        exit="exit"
                        className="fixed right-3 top-3 bottom-3 w-[calc(100%-1.5rem)] max-w-sm bg-white/95 dark:bg-[#0A0A0A]/95 backdrop-blur-2xl border border-white/20 dark:border-white/10 z-[1002] flex flex-col rounded-[2rem] shadow-[0_40px_80px_-15px_rgba(0,0,0,0.5)] overflow-hidden"
                    >
                        {/* Dynamic Island Header - Compact */}
                        <div className="px-6 py-5 flex justify-between items-center relative overflow-hidden shrink-0 border-b border-black/[0.03] dark:border-white/[0.03]">
                            <div className="absolute top-0 right-0 w-48 h-48 bg-apple-indigo/5 rounded-full blur-[80px] -mr-24 -mt-24" />
                            <div className="flex items-center gap-3 relative z-10">
                                <motion.div
                                    whileHover={{ scale: 1.05 }}
                                    className="w-10 h-10 rounded-xl bg-gradient-to-tr from-apple-indigo to-apple-violet flex items-center justify-center shadow-xl shadow-apple-indigo/20"
                                >
                                    <ShoppingCart className="w-5 h-5 text-white" />
                                </motion.div>
                                <div>
                                    <h2 className="text-xl font-black tracking-tight bg-gradient-to-r from-apple-slate to-apple-slate/60 dark:from-white dark:to-white/40 bg-clip-text text-transparent leading-none mb-1">
                                        Workspace.
                                    </h2>
                                    <div className="flex items-center gap-1.5 leading-none">
                                        <div className="w-1 h-1 rounded-full bg-green-500 animate-pulse" />
                                        <p className="text-[8px] font-black uppercase tracking-[0.15em] opacity-40">System Uplink Active</p>
                                    </div>
                                </div>
                            </div>
                            <button
                                onClick={() => dispatch(toggleCart())}
                                className="w-9 h-9 flex items-center justify-center bg-apple-slate/5 dark:bg-white/5 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-full transition-all active:scale-90"
                            >
                                <X className="w-4 h-4 opacity-60" />
                            </button>
                        </div>

                        {/* Inventory Section - Scrollable */}
                        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 scrollbar-hide">
                            {items.length === 0 ? (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="h-full flex flex-col items-center justify-center text-center px-6"
                                >
                                    <div className="relative mb-6">
                                        <div className="absolute inset-0 bg-apple-indigo/20 blur-[40px] rounded-full scale-125" />
                                        <Package className="w-16 h-16 text-apple-indigo relative z-10 opacity-30" />
                                    </div>
                                    <h3 className="text-lg font-black mb-2 tracking-tight">System Empty</h3>
                                    <p className="text-[11px] opacity-40 font-medium leading-relaxed max-w-[180px]">
                                        No active modules detected in your current workspace.
                                    </p>
                                    <button
                                        onClick={() => dispatch(toggleCart())}
                                        className="mt-6 px-6 py-2.5 bg-apple-indigo text-white rounded-full font-black text-[9px] uppercase tracking-widest hover:brightness-110 transition-all shadow-lg"
                                    >
                                        Browse Modules
                                    </button>
                                </motion.div>
                            ) : (
                                <AnimatePresence mode="popLayout">
                                    {items.map((item) => (
                                        <motion.div
                                            layout
                                            key={item.name}
                                            variants={itemVariants}
                                            className="group"
                                        >
                                            <div className="p-4 bg-white/50 dark:bg-white/[0.02] backdrop-blur-xl border border-black/[0.03] dark:border-white/[0.03] rounded-2xl flex gap-4 items-center transition-all hover:bg-white dark:hover:bg-white/[0.04] hover:shadow-[0_15px_30px_-10px_rgba(0,0,0,0.05)] active:scale-[0.98]">
                                                {/* Product Icon - Smaller */}
                                                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center shadow-lg relative shrink-0`}>
                                                    <item.icon className="w-7 h-7 text-white" />
                                                </div>

                                                {/* Content - Compact */}
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-1.5 mb-0.5 opacity-40">
                                                        <Zap className="w-2.5 h-2.5" />
                                                        <p className="text-[7px] font-black uppercase tracking-widest leading-none">Active</p>
                                                    </div>
                                                    <h4 className="text-sm font-black truncate leading-tight group-hover:text-apple-indigo transition-colors">{item.name}</h4>
                                                    <p className="text-xs font-black text-apple-indigo mt-0.5">₹{item.price.toLocaleString()}</p>
                                                </div>

                                                {/* Controls - Streamlined */}
                                                <div className="flex flex-col items-end gap-2 shrink-0">
                                                    <div className="flex items-center bg-neutral-100 dark:bg-neutral-900/50 rounded-lg p-0.5 border border-black/5 dark:border-white/5 scale-90 origin-right">
                                                        <button
                                                            onClick={() => dispatch(updateQuantity({ name: item.name, quantity: Math.max(1, item.quantity - 1) }))}
                                                            className="w-6 h-6 flex items-center justify-center hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-md transition-all active:scale-75"
                                                        >
                                                            <Minus className="w-3 h-3" />
                                                        </button>
                                                        <span className="text-[11px] font-black w-6 text-center">{item.quantity}</span>
                                                        <button
                                                            onClick={() => dispatch(updateQuantity({ name: item.name, quantity: item.quantity + 1 }))}
                                                            className="w-6 h-6 flex items-center justify-center hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-md transition-all active:scale-75"
                                                        >
                                                            <Plus className="w-3 h-3" />
                                                        </button>
                                                    </div>
                                                    <button
                                                        onClick={() => dispatch(removeFromCart(item.name))}
                                                        className="text-[8px] font-black uppercase text-red-500/50 hover:text-red-500 tracking-wider transition-colors"
                                                    >
                                                        Remove
                                                    </button>
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                            )}
                        </div>

                        {/* Control Deck - Compact */}
                        {items.length > 0 && (
                            <motion.div
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                className="p-6 bg-white dark:bg-black/20 backdrop-blur-3xl border-t border-black/5 dark:border-white/5 shrink-0"
                            >
                                <div className="space-y-4 mb-6">
                                    <div className="flex justify-between items-start">
                                        <div className="space-y-0.5">
                                            <p className="text-[7px] font-black uppercase tracking-[0.2em] opacity-40 leading-none">Matrix Cost</p>
                                            <h3 className="text-2xl font-black tracking-tight leading-none">
                                                ₹{totalAmount.toLocaleString()}
                                            </h3>
                                        </div>
                                        <div className="flex items-center gap-1.5 text-green-500 bg-green-500/5 px-2 py-1 rounded-md">
                                            <ShieldCheck className="w-3 h-3" />
                                            <span className="text-[8px] font-black uppercase tracking-wider leading-none">Secured</span>
                                        </div>
                                    </div>

                                    {/* Progress simulation - Thinner */}
                                    <div className="space-y-1.5">
                                        <div className="h-1 w-full bg-black/5 dark:bg-white/10 rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: "65%" }}
                                                className="h-full bg-apple-indigo"
                                            />
                                        </div>
                                        <div className="flex justify-between text-[7px] font-black uppercase tracking-widest opacity-30 px-0.5">
                                            <span>Config</span>
                                            <span>Validation</span>
                                            <span>Uplink</span>
                                        </div>
                                    </div>
                                </div>

                                <motion.button
                                    whileHover={{ scale: 1.01 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={handleCheckout}
                                    className="w-full h-14 bg-apple-slate dark:bg-white text-white dark:text-apple-slate rounded-2xl font-black text-sm shadow-xl flex items-center justify-center gap-3 transition-all relative overflow-hidden group"
                                >
                                    <span className="relative z-10">Confirm Matrix Uplink</span>
                                    <ArrowRight className="w-4 h-4 relative z-10 group-hover:translate-x-1 transition-transform" />
                                    <div className="absolute inset-0 bg-white/10 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite] skew-x-12" />
                                </motion.button>

                                <p className="text-center mt-4 text-[7px] font-black uppercase tracking-[0.3em] opacity-20">
                                    Protocol 27-B &bull; Stark-Grade Security
                                </p>
                            </motion.div>
                        )}
                    </motion.div>
                </>
            )}

            <style dangerouslySetInnerHTML={{
                __html: `
                @keyframes shimmer {
                    100% {
                        transform: translateX(200%) skewX(12deg);
                    }
                }
                .scrollbar-hide::-webkit-scrollbar {
                    display: none;
                }
                .scrollbar-hide {
                    -ms-overflow-style: none;
                    scrollbar-width: none;
                }
            `}} />
        </AnimatePresence>
    );
};

export default Cart;
