import React from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, Layers, BarChart, Shield, Mail } from 'lucide-react';

const PricingMatrix = () => {
    const [cycle, setCycle] = React.useState('monthly'); // 'weekly', 'monthly', 'quarterly', 'yearly'

    const plans = [
        {
            name: "Starter",
            price: { weekly: 799, monthly: 2499, quarterly: 6999, yearly: 24900 },
            features: ["Basic CRM access", "1,000 Emails/month", "Standard Analytics", "Community Support"],
            icon: <Layers className="w-6 h-6" />,
            popular: false
        },
        {
            name: "Professional",
            price: { weekly: 1999, monthly: 5999, quarterly: 16999, yearly: 59900 },
            features: ["Full ERP Integration", "Unlimited Emails", "Real-time Analytics", "24/7 Priority Support", "Custom Branding"],
            icon: <Zap className="w-6 h-6" />,
            popular: true
        },
        {
            name: "Enterprise",
            price: { weekly: 4999, monthly: 14999, quarterly: 39999, yearly: 149900 },
            features: ["Custom Schema Engine", "Multi-tenant Support", "Advanced Security Pack", "Dedicated Account Manager", "Service Level Agreement"],
            icon: <Shield className="w-6 h-6" />,
            popular: false
        }
    ];

    return (
        <section id="pricing" className="py-12 md:py-24 max-w-7xl mx-auto px-4 md:px-6">
            <div className="text-center mb-10 md:mb-16">
                <h2 className="text-3xl md:text-5xl font-black mb-4 md:mb-6 tracking-tight">Flexible Plans. <br className="hidden md:block" /> Premium Results.</h2>

                {/* Cycle Toggle */}
                <div className="inline-flex p-1.5 bg-apple-slate/5 dark:bg-white/5 rounded-2xl border border-apple-slate/10 gap-1 md:gap-4 overflow-x-auto max-w-full no-scrollbar">
                    {['weekly', 'monthly', 'quarterly', 'yearly'].map((c) => (
                        <button
                            key={c}
                            onClick={() => setCycle(c)}
                            className={`px-4 md:px-6 py-2.5 rounded-xl text-xs md:text-sm font-black capitalize transition-all whitespace-nowrap ${cycle === c ? 'bg-white dark:bg-apple-slate shadow-xl scale-100' : 'opacity-40 hover:opacity-100 scale-95'
                                }`}
                        >
                            {c}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
                {plans.map((plan, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className={`bento-card relative flex flex-col transition-all duration-500 hover:scale-[1.02] ${plan.popular ? 'ring-2 ring-apple-violet lg:scale-105 z-10' : ''}`}
                    >
                        {plan.popular && (
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 lg:left-auto lg:right-10 -translate-y-1/2 bg-apple-violet text-white text-[10px] font-black uppercase tracking-widest px-6 py-2 rounded-full shadow-2xl">
                                Top Pick
                            </div>
                        )}

                        <div className="mb-6 md:mb-8">
                            <div className="w-10 h-10 md:w-12 md:h-12 bg-apple-violet/10 rounded-xl flex items-center justify-center text-apple-violet mb-5 md:mb-6">
                                {plan.icon}
                            </div>
                            <h3 className="text-xl md:text-2xl font-black mb-2">{plan.name}</h3>
                            <div className="flex items-baseline gap-1.5">
                                <span className="text-3xl md:text-4xl font-black">₹{plan.price[cycle]}</span>

                                <span className="text-apple-slate/40 text-[10px] md:text-xs font-black uppercase tracking-widest">/ {cycle}</span>
                            </div>
                        </div>

                        <div className="space-y-3 md:space-y-4 mb-8 md:mb-10 flex-1">
                            {plan.features.map((feature, j) => (
                                <div key={j} className="flex gap-3 text-sm font-bold">
                                    <Check className="w-5 h-5 text-apple-violet shrink-0" />
                                    <span className="text-apple-slate/70 dark:text-gray-300">{feature}</span>
                                </div>
                            ))}
                        </div>

                        <button className={`w-full py-4.5 rounded-[20px] font-black text-lg transition-all active:scale-95 ${plan.popular
                            ? 'bg-apple-violet text-white shadow-xl hover:shadow-apple-violet/20'
                            : 'bg-apple-slate dark:bg-white text-white dark:text-apple-slate shadow-lg'
                            }`}>
                            Select {plan.name}
                        </button>
                    </motion.div>
                ))}
            </div>
        </section>
    );
};

export default PricingMatrix;
