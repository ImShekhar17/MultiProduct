import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Zap, Shield, Sparkles, Layers } from 'lucide-react';

const Hero = () => {
    return (
        <section className="relative pt-32 pb-20 overflow-hidden min-h-screen flex flex-col justify-center">
            {/* Background Blobs */}
            <div className="absolute top-0 -left-20 w-96 h-96 bg-apple-indigo/20 rounded-full blur-[120px] -z-10" />
            <div className="absolute bottom-10 -right-20 w-96 h-96 bg-apple-violet/20 rounded-full blur-[120px] -z-10" />

            <div className="max-w-7xl mx-auto px-6 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="inline-flex items-center gap-2 bg-apple-slate/5 dark:bg-white/5 border border-apple-slate/10 dark:border-white/10 px-4 py-2 rounded-full mb-8"
                >
                    <Sparkles className="w-4 h-4 text-apple-violet" />
                    <span className="text-sm font-medium">Reimagining the SaaS Experience</span>
                </motion.div>

                <motion.h1
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="text-6xl md:text-8xl font-bold tracking-tight mb-8 leading-[1.1]"
                >
                    One Platform. <br />
                    <span className="gradient-text">Infinite Products.</span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="text-lg md:text-xl text-apple-slate/60 dark:text-gray-400 max-w-2xl mx-auto mb-12 leading-relaxed"
                >
                    Empower your business with a unified suite of premium tools. CRM, Marketing, and Analytics—all under one roof, with the elegance of Cupertino design.
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                    className="flex flex-col sm:flex-row items-center justify-center gap-6"
                >
                    <button className="w-full sm:w-auto bg-apple-slate dark:bg-white text-white dark:text-apple-slate px-10 py-5 rounded-full text-lg font-bold hover:scale-105 transition-transform shadow-2xl flex items-center justify-center gap-2">
                        Get Started Free <ArrowRight className="w-5 h-5" />
                    </button>
                    <button className="w-full sm:w-auto glass px-10 py-5 rounded-full text-lg font-bold hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                        View All Products
                    </button>
                </motion.div>

                {/* Feature Pillows */}
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1, delay: 0.8 }}
                    className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto"
                >
                    {[
                        { icon: <Zap className="w-6 h-6" />, title: "Instant Access", desc: "Start using any product in seconds." },
                        { icon: <Shield className="w-6 h-6" />, title: "Safe & Secure", desc: "Enterprise-grade security by default." },
                        { icon: <Layers className="w-6 h-6" />, title: "Unified Suite", desc: "All your tools sharing one database." }
                    ].map((feature, i) => (
                        <div key={i} className="flex flex-col items-center text-center p-4">
                            <div className="mb-4 text-apple-violet">{feature.icon}</div>
                            <h3 className="font-bold mb-2">{feature.title}</h3>
                            <p className="text-sm text-apple-slate/60 dark:text-gray-400">{feature.desc}</p>
                        </div>
                    ))}
                </motion.div>
            </div>
        </section>
    );
};

export default Hero;
