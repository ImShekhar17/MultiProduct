import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, X, Info, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { selectToasts, removeToast } from '../Redux/ReduxSlice/NotificationSlice';

const Toast = () => {
    const dispatch = useDispatch();
    const toasts = useSelector(selectToasts);

    return (
        <div className="fixed bottom-8 right-8 z-[100] flex flex-col gap-4 pointer-events-none">
            <AnimatePresence>
                {toasts.map((toast) => (
                    <ToastItem
                        key={toast.id}
                        toast={toast}
                        onClose={() => dispatch(removeToast(toast.id))}
                    />
                ))}
            </AnimatePresence>
        </div>
    );
};

const ToastItem = ({ toast, onClose }) => {
    useEffect(() => {
        const timer = setTimeout(onClose, 5000);
        return () => clearTimeout(timer);
    }, [onClose]);

    const icons = {
        system: <Info className="w-5 h-5 text-apple-indigo" />,
        alert: <AlertTriangle className="w-5 h-5 text-red-500" />,
        success: <CheckCircle2 className="w-5 h-5 text-green-500" />,
        welcome: <Bell className="w-5 h-5 text-apple-indigo" />,
        billing: <Info className="w-5 h-5 text-green-500" />
    };

    return (
        <motion.div
            layout
            initial={{ opacity: 0, x: 50, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
            className="pointer-events-auto glass rounded-2xl shadow-2xl p-5 border border-white/20 dark:border-white/10 w-80 md:w-96 flex gap-4 items-start"
        >
            <div className={`p-2 rounded-xl shrink-0 ${toast.type === 'alert' ? 'bg-red-500/10' :
                    toast.type === 'success' || toast.type === 'billing' ? 'bg-green-500/10' : 'bg-apple-indigo/10'
                }`}>
                {icons[toast.type] || icons.system}
            </div>
            <div className="flex-1 min-w-0">
                <h4 className="font-bold text-sm mb-1">{toast.title}</h4>
                <p className="text-xs opacity-60 leading-relaxed font-medium">{toast.desc}</p>
            </div>
            <button
                onClick={onClose}
                className="p-1 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg transition-all opacity-40 hover:opacity-100"
            >
                <X className="w-4 h-4" />
            </button>
        </motion.div>
    );
};

export default Toast;
