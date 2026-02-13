import React from 'react';
import { motion } from 'framer-motion';
import { UserPlus, BarChart3, Mail, Zap, Smartphone, Globe, ShieldCheck, Cpu } from 'lucide-react';

const BentoGrid = () => {
    const items = [
        {
            title: "Smart User Onboarding",
            description: "Seamlessly welcome your users with personalized flows and real-time OTP verification.",
            icon: <UserPlus className="w-8 h-8" />,
            className: "md:col-span-2",
            bgGradient: "from-apple-indigo/20 to-transparent"
        },
        {
            title: "Real-time Analytics",
            description: "Deep insights into product usage.",
            icon: <BarChart3 className="w-8 h-8" />,
            className: "md:col-span-1",
            bgGradient: "from-apple-violet/20 to-transparent"
        },
        {
            title: "Email Automation",
            description: "Automate your customer communication with high-end templates.",
            icon: <Mail className="w-8 h-8" />,
            className: "md:col-span-1",
            bgGradient: "from-apple-blue/20 to-transparent"
        },
        {
            title: "High Performance Infrastructure",
            description: "Built on a resilient Django backend with Redis caching and Celery task balancing for ultra-fast response times.",
            icon: <Cpu className="w-8 h-8" />,
            className: "md:col-span-2",
            bgGradient: "from-apple-slate/10 to-transparent"
        }
    ];

    return (
        <section id="features" className="py-12 md:py-24 max-w-7xl mx-auto px-4 md:px-6">
            <div className="text-center mb-10 md:mb-16">
                <h2 className="text-3xl md:text-5xl font-black mb-4 md:mb-6 tracking-tight">Engineered for Excellence.</h2>
                <p className="text-apple-slate/60 dark:text-gray-400 max-w-2xl mx-auto font-medium leading-relaxed">
                    Every component of MultiProduct is designed with precision to provide the most seamless user experience possible.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-6">
                {items.map((item, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: i * 0.1 }}
                        className={`bento-card overflow-hidden relative group ${item.className || ''}`}

                    >
                        <div className={`absolute inset-0 bg-gradient-to-br ${item.bgGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-700`} />
                        <div className="relative z-10 p-2 md:p-0">
                            <div className="mb-6 p-4 rounded-xl md:rounded-2xl bg-white dark:bg-white/5 shadow-sm inline-block text-apple-violet group-hover:scale-110 transition-transform duration-500">
                                {item.icon}
                            </div>
                            <h3 className="text-xl md:text-2xl font-black mb-3">{item.title}</h3>
                            <p className="text-sm md:text-base text-apple-slate/50 dark:text-gray-400 leading-relaxed font-medium">
                                {item.description}
                            </p>
                        </div>

                        {/* Visual Decorative Element for larger cards */}
                        {item.className?.includes('md:col-span-2') && (
                            <div className="absolute -bottom-10 -right-10 w-48 h-48 bg-apple-indigo/5 rounded-full blur-3xl opacity-50" />
                        )}
                    </motion.div>
                ))}
            </div>

            {/* Minor features row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 mt-12 md:mt-16 text-center">
                {[
                    { icon: <Smartphone className="w-5 h-5 md:w-6 md:h-6" />, label: "Mobile First" },
                    { icon: <Globe className="w-5 h-5 md:w-6 md:h-6" />, label: "Global Presence" },
                    { icon: <ShieldCheck className="w-5 h-5 md:w-6 md:h-6" />, label: "Stark-Grade Security" },
                    { icon: <Zap className="w-5 h-5 md:w-6 md:h-6" />, label: "Ultra Fast" }
                ].map((f, i) => (
                    <div key={i} className="flex flex-col items-center gap-3 grayscale opacity-40 hover:grayscale-0 hover:opacity-100 transition-all cursor-default">
                        <div className="text-apple-slate dark:text-white mb-1">{f.icon}</div>
                        <span className="text-[10px] font-black uppercase tracking-widest text-apple-slate/60 dark:text-gray-500">{f.label}</span>
                    </div>
                ))}
            </div>
        </section>
    );
};

export default BentoGrid;
