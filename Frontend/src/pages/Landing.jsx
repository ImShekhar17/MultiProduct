import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import BentoGrid from '../components/BentoGrid';
import PricingMatrix from '../components/PricingMatrix';
import ProductShowcase from '../components/ProductShowcase';
import { motion } from 'framer-motion';


const Landing = () => {
    return (
        <div className="relative w-full">
            <Navbar />
            <main>
                <Hero />

                {/* Product Showcase Section */}
                <ProductShowcase />

                {/* About / Bento Grid Section */}
                <BentoGrid />

                {/* Pricing Matrix Section */}
                <PricingMatrix />


                {/* Call to Action Section */}
                <section className="py-24 px-6">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        className="max-w-4xl mx-auto rounded-apple-xl bg-gradient-to-br from-apple-indigo to-apple-violet p-12 md:p-20 text-center text-white relative overflow-hidden shadow-2xl"
                    >
                        {/* Decorative background elements */}
                        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -mr-20 -mt-20" />
                        <div className="absolute bottom-0 left-0 w-64 h-64 bg-black/10 rounded-full blur-3xl -ml-20 -mb-20" />

                        <h2 className="text-4xl md:text-6xl font-black mb-8 leading-tight relative z-10">
                            Transform Your <br /> Workflow Today.
                        </h2>
                        <p className="text-lg md:text-xl text-white/80 mb-12 max-w-xl mx-auto relative z-10">
                            Join thousands of businesses already scaling with MultiProduct. Start your 14-day free trial on any service.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 relative z-10">
                            <button className="w-full sm:w-auto px-8 py-4 bg-white text-apple-indigo font-bold rounded-full hover:scale-105 transition-transform">
                                Get Started Now
                            </button>
                            <button className="w-full sm:w-auto px-8 py-4 bg-transparent border border-white/30 text-white font-bold rounded-full hover:bg-white/10 transition-colors">
                                Contact Sales
                            </button>
                        </div>
                    </motion.div>
                </section>

                {/* Simple Footer */}
                <footer className="py-12 border-t border-apple-slate/5 dark:border-white/5">
                    <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-8">
                        <div className="flex items-center gap-2">
                            <div className="bg-apple-indigo/10 p-1.5 rounded-lg">
                                <div className="w-5 h-5 bg-apple-indigo rounded-sm" />
                            </div>
                            <span className="font-bold">MultiProduct</span>
                        </div>
                        <div className="flex gap-8 text-sm text-apple-slate/40 dark:text-gray-500 font-medium">
                            <a href="#" className="hover:text-apple-slate dark:hover:text-white transition-colors">Privacy Policy</a>
                            <a href="#" className="hover:text-apple-slate dark:hover:text-white transition-colors">Terms of Service</a>
                            <a href="#" className="hover:text-apple-slate dark:hover:text-white transition-colors">Status</a>
                        </div>
                        <p className="text-sm text-apple-slate/30 dark:text-gray-600">
                            &copy; 2025 MultiProduct Inc. All rights reserved.
                        </p>
                    </div>
                </footer>
            </main>
        </div>
    );
};

export default Landing;
