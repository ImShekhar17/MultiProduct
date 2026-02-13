import React from 'react';
import { motion } from 'framer-motion';
import { useDispatch } from 'react-redux';
import { addToCart } from '../Redux/ReduxSlice/CartSlice';
import { addNotification } from '../Redux/ReduxSlice/NotificationSlice';
import {
    CreditCard, Factory, Landmark, ShoppingCart, Building2, Home, Shirt,
    Hammer, Users, HandCoins, Store, Sprout, Receipt, Waves, Apple,
    Settings, LayoutGrid, Wind, Scissors, Box, HeartHandshake, Wallet, ArrowUpRight, Plus
} from 'lucide-react';

const products = [
    { name: 'PCARD', icon: CreditCard, color: 'from-blue-500 to-cyan-400', desc: 'Digital credit solutions for modern agricultural commerce.', price: 2499 },
    { name: 'Sugar Factory', icon: Factory, color: 'from-orange-500 to-amber-400', desc: 'Enterprise-scale sugar production and refinery management.', price: 14999 },
    { name: 'PACS', icon: Landmark, color: 'from-emerald-500 to-teal-400', desc: 'Primary Agricultural Credit Societies core infrastructure.', price: 5999 },
    { name: 'TAPCMS', icon: ShoppingCart, color: 'from-purple-500 to-indigo-400', desc: 'Advanced marketing and procurement system for growers.', price: 3499 },
    { name: 'Urban Bank', icon: Building2, color: 'from-slate-700 to-slate-500', desc: 'Complete digital banking suite for urban co-operative sectors.', price: 19999 },
    { name: 'HBCS', icon: Home, color: 'from-rose-500 to-pink-400', desc: 'Housing Building Co-operative Society management system.', price: 8999 },
    { name: 'Khadi', icon: Shirt, color: 'from-amber-700 to-orange-600', desc: 'Artisan commerce and supply chain for traditional textiles.', price: 1299 },
    { name: 'Kushala Kaigarike', icon: Hammer, color: 'from-cyan-600 to-blue-500', desc: 'Empowering small-scale industries and skilled craftsmanship.', price: 4499 },
    { name: 'District Union', icon: Users, color: 'from-indigo-600 to-violet-500', desc: 'Centralized union orchestration and resource management.', price: 7499 },
    { name: 'Credit Society', icon: HandCoins, color: 'from-green-600 to-emerald-500', desc: 'Micro-credit facilities and member savings optimization.', price: 3999 },
    { name: 'CCW Stores', icon: Store, color: 'from-red-600 to-rose-500', desc: 'Retail chain management for consumer co-operative wholesales.', price: 5499 },
    { name: 'Coir Societies', icon: Sprout, color: 'from-lime-600 to-green-500', desc: 'Sustainable coir production and international trade logistics.', price: 2999 },
    { name: 'Consumer CRS', icon: Receipt, color: 'from-sky-500 to-blue-400', desc: 'Streamlined consumer reporting and service automation.', price: 1899 },
    { name: 'Fisheries', icon: Waves, color: 'from-blue-600 to-cyan-500', desc: 'Deep-sea resource tracking and fishery trade management.', price: 6499 },
    { name: 'Hopcoms', icon: Apple, color: 'from-orange-400 to-red-500', desc: 'Horticultural produce marketing and distribution network.', price: 2199 },
    { name: 'Industrial', icon: Settings, color: 'from-gray-600 to-gray-400', desc: 'Heavy industrial automation and assembly line intelligence.', price: 12499 },
    { name: 'MPCS', icon: LayoutGrid, color: 'from-violet-500 to-purple-400', desc: 'Multi-Purpose Co-operative Society digital core.', price: 4999 },
    { name: 'Spinning Mill', icon: Wind, color: 'from-teal-500 to-emerald-400', desc: 'Precision textile spinning and mill output optimization.', price: 8999 },
    { name: 'Weavers', icon: Scissors, color: 'from-pink-600 to-rose-500', desc: 'Dedicated platform for handloom weavers and silk trade.', price: 1599 },
    { name: 'Multi Purpose', icon: Box, color: 'from-indigo-500 to-blue-400', desc: 'Versatile resource management for diversified operations.', price: 3799 },
    { name: 'Souharda MPCS', icon: HeartHandshake, color: 'from-amber-500 to-orange-400', desc: 'Community-driven multi-purpose society orchestration.', price: 4299 },
    { name: 'Souharda Credit', icon: Wallet, color: 'from-emerald-500 to-green-400', desc: 'Unified credit management and financial health tracking.', price: 5199 },
];

const ProductShowcase = () => {
    const dispatch = useDispatch();

    const handleAddToCart = (e, product) => {
        e.stopPropagation();
        dispatch(addToCart(product));
        dispatch(addNotification({
            title: "Added to Cart!",
            desc: `${product.name} has been added to your workspace.`,
            type: "success"
        }));
    };

    return (
        <section id="products" className="py-24 md:py-32 px-6 bg-white dark:bg-[#050505] overflow-hidden transition-colors duration-500">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="text-center mb-20 md:mb-24">
                    <motion.span
                        initial={{ opacity: 0, y: 10 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-block px-4 py-1.5 rounded-full bg-apple-violet/10 text-apple-violet text-[10px] font-black uppercase tracking-[0.2em] mb-6"
                    >
                        The Ecosystem
                    </motion.span>
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-4xl md:text-6xl font-black tracking-tight text-apple-slate dark:text-white mb-6"
                    >
                        Every tool for every <br />
                        <span className="gradient-text">Co-operative mission.</span>
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="max-w-2xl mx-auto text-lg md:text-xl text-apple-slate/50 dark:text-gray-400 font-medium"
                    >
                        Explore the industry-leading suite of products designed to power the next generation of co-operative societies.
                    </motion.p>
                </div>

                {/* Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 md:gap-8">
                    {products.map((product, index) => (
                        <motion.div
                            key={product.name}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.05 }}
                            whileHover={{ y: -10 }}
                            className="group relative cursor-pointer"
                        >
                            <div className="h-full bento-card flex flex-col justify-between overflow-hidden group-hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.15)] dark:group-hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.4)] border-transparent group-hover:border-apple-violet/20">
                                {/* Decorator Background */}
                                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${product.color} opacity-0 group-hover:opacity-10 blur-[60px] transition-all duration-700`} />

                                <div className="relative z-10">
                                    <div className="flex justify-between items-start mb-8">
                                        <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${product.color} flex items-center justify-center shadow-lg shadow-black/5 group-hover:scale-110 transition-transform duration-500`}>
                                            <product.icon className="w-7 h-7 text-white" />
                                        </div>
                                        <div className="text-right">
                                            <p className="text-[10px] font-black uppercase tracking-widest opacity-30 mb-0.5">Yearly Plan</p>
                                            <p className="text-lg font-black tracking-tight text-apple-violet">₹{product.price.toLocaleString()}</p>
                                        </div>
                                    </div>
                                    <h3 className="text-xl md:text-2xl font-black text-apple-slate dark:text-white mb-4 group-hover:text-apple-violet transition-colors">
                                        {product.name}
                                    </h3>
                                    <p className="text-sm text-apple-slate/40 dark:text-gray-500 font-bold leading-relaxed">
                                        {product.desc}
                                    </p>
                                </div>

                                <div className="mt-10 flex items-center justify-between relative z-10">
                                    <button
                                        onClick={(e) => handleAddToCart(e, product)}
                                        className="flex items-center gap-2 px-4 py-2 rounded-xl bg-apple-slate/5 dark:bg-white/5 border border-apple-slate/10 dark:border-white/10 group-hover:bg-apple-indigo group-hover:text-white group-hover:border-apple-indigo transition-all font-bold text-xs"
                                    >
                                        <Plus className="w-4 h-4" />
                                        Add to Cart
                                    </button>
                                    <div className="w-10 h-10 rounded-full bg-apple-slate/5 dark:bg-white/5 flex items-center justify-center opacity-0 group-hover:opacity-100 group-hover:translate-x-0 -translate-x-4 transition-all duration-500 border border-apple-slate/10 dark:border-white/10 text-apple-slate dark:text-white hover:bg-apple-violet hover:text-white">
                                        <ArrowUpRight className="w-5 h-5" />
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Footer Insight */}
                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    className="mt-24 py-12 border-t border-apple-slate/5 dark:border-white/5 flex flex-col md:flex-row items-center justify-between gap-8"
                >
                    <div className="flex items-center gap-6">
                        <div className="w-12 h-12 rounded-full border border-apple-slate/10 dark:border-white/10 flex items-center justify-center font-black text-xs">
                            S.I
                        </div>
                        <p className="text-sm font-bold text-apple-slate/30 uppercase tracking-[0.3em]">
                            Stark-Grade Infrastructure
                        </p>
                    </div>
                    <div className="flex gap-12 font-black text-[10px] uppercase tracking-widest text-apple-slate/20">
                        <span className="hover:text-apple-violet cursor-pointer transition-colors">Security</span>
                        <span className="hover:text-apple-violet cursor-pointer transition-colors">Scalability</span>
                        <span className="hover:text-apple-violet cursor-pointer transition-colors">Integrity</span>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};

export default ProductShowcase;
