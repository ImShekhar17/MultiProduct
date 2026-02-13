import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, ArrowRight, Shield, Globe, Zap, Cpu, Code, Database, CheckCircle2, ChevronRight, Layout } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Onboarding = () => {
    const [step, setStep] = useState(1);
    const [workspace, setWorkspace] = useState('');
    const [selectedProducts, setSelectedProducts] = useState([]);
    const navigate = useNavigate();

    const products = [
        { id: 'analytics', name: 'Cloud Analytics', icon: Zap, color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
        { id: 'security', name: 'Shield Security', icon: Shield, color: 'text-blue-500', bg: 'bg-blue-500/10' },
        { id: 'api', name: 'Nexus API', icon: Code, color: 'text-purple-500', bg: 'bg-purple-500/10' },
        { id: 'storage', name: 'Deep Storage', icon: Database, color: 'text-indigo-500', bg: 'bg-indigo-500/10' },
        { id: 'compute', name: 'Core Compute', icon: Cpu, color: 'text-green-500', bg: 'bg-green-500/10' },
        { id: 'deploy', name: 'Instant Deploy', icon: Globe, color: 'text-red-500', bg: 'bg-red-500/10' },
    ];

    const toggleProduct = (id) => {
        setSelectedProducts(prev =>
            prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
        );
    };

    const handleNext = () => setStep(step + 1);
    const handleFinish = () => navigate('/dashboard');

    return (
        <div className="min-h-screen bg-[#FAFAFA] dark:bg-[#050505] relative overflow-hidden flex items-center justify-center p-6">
            {/* Dynamic Background */}
            <div className="absolute inset-0 pointer-events-none">
                <motion.div
                    animate={{
                        scale: [1, 1.2, 1],
                        rotate: [0, 90, 0],
                        x: [0, 100, 0],
                        y: [0, 50, 0]
                    }}
                    transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                    className="absolute -top-[20%] -left-[10%] w-[60%] h-[60%] bg-apple-violet/10 rounded-full blur-[120px]"
                />
                <motion.div
                    animate={{
                        scale: [1, 1.1, 1],
                        rotate: [0, -90, 0],
                        x: [0, -80, 0],
                        y: [0, -40, 0]
                    }}
                    transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
                    className="absolute -bottom-[20%] -right-[10%] w-[60%] h-[60%] bg-apple-blue/10 rounded-full blur-[120px]"
                />
            </div>

            {/* Logo */}
            <div className="absolute top-10 left-10 flex items-center gap-3 z-20">
                <div className="bg-gradient-to-tr from-apple-indigo to-apple-violet p-2 rounded-xl shadow-lg">
                    <Layers className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold tracking-tight text-apple-slate dark:text-white">MultiProduct</span>
            </div>

            {/* Progress indicator */}
            <div className="absolute top-12 left-1/2 -translate-x-1/2 flex gap-3 z-20">
                {[1, 2, 3].map(i => (
                    <div
                        key={i}
                        className={`h-1.5 rounded-full transition-all duration-500 ${step >= i ? 'w-8 bg-apple-violet' : 'w-4 bg-apple-slate/10 dark:bg-white/10'}`}
                    />
                ))}
            </div>

            <div className="w-full max-w-4xl relative z-10">
                <AnimatePresence mode="wait">
                    {step === 1 && (
                        <motion.div
                            key="step1"
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 1.1, y: -20 }}
                            className="text-center"
                        >
                            <span className="inline-block px-4 py-1.5 rounded-full bg-apple-violet/10 text-apple-violet text-[10px] font-black uppercase tracking-[0.2em] mb-6">
                                The Genesis
                            </span>
                            <h1 className="text-5xl md:text-7xl font-black tracking-tight mb-8 leading-tight">
                                Name your <span className="gradient-text">World.</span>
                            </h1>
                            <div className="relative max-w-2xl mx-auto group">
                                <input
                                    type="text"
                                    value={workspace}
                                    onChange={(e) => setWorkspace(e.target.value)}
                                    placeholder="Enter Workspace Name"
                                    className="w-full bg-transparent border-b-4 border-apple-slate/5 dark:border-white/5 focus:border-apple-violet transition-colors text-3xl md:text-5xl font-black py-8 outline-none text-center placeholder:text-apple-slate/10 dark:placeholder:text-white/10"
                                    autoFocus
                                />
                                <div className="absolute -bottom-1 left-0 w-0 h-1 bg-apple-violet group-focus-within:w-full transition-all duration-700 ease-out" />
                            </div>
                            <motion.button
                                initial={{ opacity: 0 }}
                                animate={{ opacity: workspace ? 1 : 0 }}
                                onClick={handleNext}
                                className="mt-12 group flex items-center gap-4 mx-auto text-xl font-black text-apple-slate dark:text-white hover:text-apple-violet transition-colors"
                            >
                                Continue to Ecosystem
                                <div className="p-3 rounded-full bg-apple-slate dark:bg-white text-white dark:text-apple-slate group-hover:bg-apple-violet group-hover:text-white transition-all shadow-xl">
                                    <ArrowRight className="w-6 h-6" />
                                </div>
                            </motion.button>
                        </motion.div>
                    )}

                    {step === 2 && (
                        <motion.div
                            key="step2"
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 1.1, y: -20 }}
                            className="text-center"
                        >
                            <span className="inline-block px-4 py-1.5 rounded-full bg-apple-blue/10 text-apple-blue text-[10px] font-black uppercase tracking-[0.2em] mb-6">
                                Selection Mode
                            </span>
                            <h1 className="text-4xl md:text-6xl font-black tracking-tight mb-4">
                                Pick your <span className="gradient-text">Tools.</span>
                            </h1>
                            <p className="text-apple-slate/40 dark:text-gray-500 font-bold mb-12 text-lg">
                                Select at least one product to begin your journey in {workspace}.
                            </p>

                            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                                {products.map((product) => (
                                    <button
                                        key={product.id}
                                        onClick={() => toggleProduct(product.id)}
                                        className={`p-8 rounded-[32px] border-2 transition-all duration-300 group text-left relative overflow-hidden ${selectedProducts.includes(product.id)
                                                ? 'bg-white dark:bg-white/5 border-apple-violet shadow-2xl scale-105'
                                                : 'bg-apple-slate/[0.02] dark:bg-white/[0.02] border-transparent grayscale hover:grayscale-0 hover:bg-white dark:hover:bg-white/5 hover:border-apple-slate/10'
                                            }`}
                                    >
                                        <div className={`p-4 rounded-2xl w-fit mb-6 shadow-inner ${product.bg} ${product.color}`}>
                                            <product.icon className="w-8 h-8" />
                                        </div>
                                        <h3 className="text-xl font-black mb-1">{product.name}</h3>
                                        <p className="text-xs font-bold opacity-40 uppercase tracking-widest">Enterprise Ready</p>

                                        {selectedProducts.includes(product.id) && (
                                            <div className="absolute top-6 right-6">
                                                <CheckCircle2 className="w-8 h-8 text-apple-violet" />
                                            </div>
                                        )}
                                    </button>
                                ))}
                            </div>

                            <div className="mt-16 flex items-center justify-between max-w-lg mx-auto">
                                <button onClick={() => setStep(1)} className="text-sm font-black uppercase tracking-widest opacity-40 hover:opacity-100 transition-opacity">Back</button>
                                <button
                                    disabled={selectedProducts.length === 0}
                                    onClick={handleNext}
                                    className="bg-apple-slate dark:bg-white text-white dark:text-apple-slate px-10 py-5 rounded-[22px] font-black text-xl shadow-2xl hover:scale-105 active:scale-95 transition-all disabled:opacity-20 disabled:scale-100"
                                >
                                    Initialize Workspace
                                </button>
                            </div>
                        </motion.div>
                    )}

                    {step === 3 && (
                        <motion.div
                            key="step3"
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            className="text-center"
                        >
                            <div className="w-32 h-32 bg-green-500/10 rounded-[40px] flex items-center justify-center mx-auto mb-10 shadow-inner relative">
                                <div className="absolute inset-0 bg-green-500/5 rounded-[40px] animate-ping" />
                                <CheckCircle2 className="w-16 h-16 text-green-500 relative z-10" />
                            </div>
                            <h1 className="text-5xl md:text-7xl font-black tracking-tight mb-6 leading-tight">
                                You're <span className="text-green-500">Live.</span>
                            </h1>
                            <p className="text-xl font-bold text-apple-slate/60 dark:text-gray-400 mb-12 max-w-xl mx-auto">
                                Welcome to <span className="text-apple-slate dark:text-white">{workspace}</span>. Your chosen ecosystem is ready for production.
                            </p>

                            <div className="flex flex-col md:flex-row gap-6 justify-center max-w-2xl mx-auto">
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={handleFinish}
                                    className="flex-1 p-8 rounded-[32px] bg-apple-slate dark:bg-white text-white dark:text-apple-slate text-left relative group border border-transparent shadow-2xl"
                                >
                                    <div className="p-3 bg-white/10 rounded-xl w-fit mb-6 text-white dark:text-apple-slate">
                                        <Layout className="w-6 h-6" />
                                    </div>
                                    <h3 className="text-2xl font-black mb-2">Explore Control Center</h3>
                                    <p className="text-sm font-bold opacity-60">General Management Dashboard</p>
                                    <ChevronRight className="absolute bottom-10 right-10 w-8 h-8 group-hover:translate-x-2 transition-transform opacity-30" />
                                </motion.button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Design detail */}
            <div className="absolute bottom-10 left-10 text-[10px] font-black uppercase tracking-[0.4em] opacity-20">
                MultiProduct Onboarding v1.0
            </div>
            <div className="absolute bottom-10 right-10 flex gap-10 opacity-20 text-[10px] font-black uppercase tracking-widest">
                <span>Stark-grade Security</span>
                <span>Role-based Protocol</span>
            </div>
        </div>
    );
};

export default Onboarding;
