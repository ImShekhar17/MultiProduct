import React, { useState, useEffect } from 'react';
import { Layers, Menu, X, User, Sun, Moon, ShoppingCart } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useTheme } from '../Context/ThemeContext';
import { toggleCart, selectCartCount } from '../Redux/ReduxSlice/CartSlice';


const Navbar = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const { theme, toggleTheme } = useTheme();
    const dispatch = useDispatch();
    const cartCount = useSelector(selectCartCount);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navLinks = [
        { name: 'Products', href: '#products' },
        { name: 'Features', href: '#features' },
        { name: 'About', href: '#about' },
        { name: 'Pricing', href: '#pricing' },
    ];

    return (
        <nav
            className={`fixed ${isScrolled ? 'top-4 md:top-6' : 'top-6 md:top-8'} left-1/2 -translate-x-1/2 w-[90%] md:w-[95%] max-w-6xl z-50 transition-all duration-500 rounded-[24px] ${isScrolled
                ? 'glass h-16 shadow-2xl border border-white/20'
                : 'h-20 bg-white/30 dark:bg-black/20 backdrop-blur-md border border-white/10'
                }`}
        >
            <div className="px-5 md:px-8 h-full flex items-center justify-between">

                {/* Logo */}
                <Link to="/" className="flex items-center gap-2 group cursor-pointer transition-transform active:scale-95">
                    <div className="bg-gradient-to-tr from-apple-indigo to-apple-violet p-1.5 md:p-2 rounded-xl group-hover:rotate-12 transition-transform duration-300">
                        <Layers className="w-5 h-5 md:w-6 md:h-6 text-white" />
                    </div>
                    <span className="text-lg md:text-xl font-bold tracking-tight">MultiProduct</span>
                </Link>


                {/* Desktop Nav */}
                <div className="hidden md:flex items-center gap-8">
                    {navLinks.map((link) => (
                        <a
                            key={link.name}
                            href={link.href}
                            className="text-sm font-medium hover:text-apple-violet transition-colors"
                        >
                            {link.name}
                        </a>
                    ))}
                    <div className="h-6 w-px bg-apple-slate/10 dark:bg-white/10 mx-2" />

                    {/* Cart Trigger */}
                    <button
                        onClick={() => dispatch(toggleCart())}
                        className="relative p-2.5 rounded-xl hover:bg-apple-slate/5 dark:hover:bg-white/5 transition-all active:scale-90"
                    >
                        <ShoppingCart className="w-5 h-5 text-apple-slate dark:text-white" />
                        {cartCount > 0 && (
                            <motion.span
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="absolute -top-1 -right-1 w-5 h-5 bg-apple-violet text-white text-[10px] font-black rounded-full flex items-center justify-center border-2 border-white dark:border-black shadow-lg"
                            >
                                {cartCount}
                            </motion.span>
                        )}
                    </button>

                    {/* Theme Toggle Button */}
                    <button
                        onClick={toggleTheme}
                        className="p-2.5 rounded-xl hover:bg-apple-slate/5 dark:hover:bg-white/5 transition-colors cursor-pointer relative overflow-hidden group flex items-center justify-center"
                        aria-label="Toggle Theme"
                    >
                        <AnimatePresence mode="wait">
                            {theme === 'dark' ? (
                                <motion.div
                                    key="moon"
                                    initial={{ scale: 0.5, rotate: -45, opacity: 0 }}
                                    animate={{ scale: 1, rotate: 0, opacity: 1 }}
                                    exit={{ scale: 0.5, rotate: 45, opacity: 0 }}
                                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                                    className="relative z-10"
                                >
                                    <Moon className="w-5 h-5 text-apple-violet fill-apple-violet/10 group-hover:drop-shadow-[0_0_8px_rgba(139,92,246,0.5)]" />
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="sun"
                                    initial={{ scale: 0.5, rotate: 45, opacity: 0 }}
                                    animate={{ scale: 1, rotate: 0, opacity: 1 }}
                                    exit={{ scale: 0.5, rotate: -45, opacity: 0 }}
                                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                                    className="relative z-10"
                                >
                                    <Sun className="w-5 h-5 text-amber-500 fill-amber-500/10 group-hover:drop-shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </button>

                    <Link to="/login" className="text-sm font-medium hover:text-apple-violet transition-colors">
                        Login
                    </Link>
                    <Link to="/signup" className="bg-apple-slate dark:bg-white text-white dark:text-apple-slate px-5 py-2 rounded-full text-sm font-semibold hover:scale-105 transition-transform active:scale-95">
                        Get Started
                    </Link>
                </div>


                {/* Mobile Icons */}
                <div className="flex items-center gap-2 md:hidden">
                    <button
                        onClick={() => dispatch(toggleCart())}
                        className="relative p-2 text-apple-slate dark:text-white flex items-center justify-center min-w-[40px] min-h-[40px]"
                    >
                        <ShoppingCart size={22} />
                        {cartCount > 0 && (
                            <span className="absolute top-1 right-1 w-4 h-4 bg-apple-violet text-white text-[8px] font-black rounded-full flex items-center justify-center border border-white dark:border-black">
                                {cartCount}
                            </span>
                        )}
                    </button>
                    <button
                        onClick={toggleTheme}
                        className="p-2 text-apple-slate dark:text-white flex items-center justify-center min-w-[40px] min-h-[40px]"
                        aria-label="Toggle Theme"
                    >
                        <AnimatePresence mode="wait">
                            {theme === 'dark' ? (
                                <motion.div
                                    key="moon-mobile"
                                    initial={{ scale: 0.5, rotate: -45, opacity: 0 }}
                                    animate={{ scale: 1, rotate: 0, opacity: 1 }}
                                    exit={{ scale: 0.5, rotate: 45, opacity: 0 }}
                                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                                >
                                    <Moon size={22} className="text-apple-violet fill-apple-violet/10" />
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="sun-mobile"
                                    initial={{ scale: 0.5, rotate: 45, opacity: 0 }}
                                    animate={{ scale: 1, rotate: 0, opacity: 1 }}
                                    exit={{ scale: 0.5, rotate: -45, opacity: 0 }}
                                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                                >
                                    <Sun size={22} className="text-amber-500 fill-amber-500/10" />
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </button>
                    <button
                        className="p-2 text-apple-slate dark:text-white transition-transform active:scale-90"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    >
                        {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -10 }}
                        className="absolute top-[calc(100%+12px)] left-0 w-full bg-white/95 dark:bg-black/95 backdrop-blur-2xl shadow-[0_20px_50px_rgba(0,0,0,0.3)] md:hidden rounded-[24px] overflow-hidden border border-apple-slate/10 dark:border-white/10"
                    >
                        <div className="flex flex-col p-6 gap-2">
                            {navLinks.map((link) => (
                                <a
                                    key={link.name}
                                    href={link.href}
                                    className="text-lg font-semibold py-3 px-4 rounded-xl hover:bg-apple-slate/5 dark:hover:bg-white/5 transition-colors"
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    {link.name}
                                </a>
                            ))}
                            <div className="h-px bg-apple-slate/5 dark:bg-white/5 my-2" />
                            <div className="flex flex-col gap-3">
                                <Link
                                    to="/login"
                                    className="w-full py-4 text-center font-bold text-lg rounded-xl hover:bg-apple-slate/5 dark:hover:bg-white/5"
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    Login
                                </Link>
                                <Link
                                    to="/signup"
                                    className="w-full py-4 rounded-2xl bg-apple-slate text-white dark:bg-white dark:text-apple-slate font-black text-center text-lg active:scale-[0.98] transition-transform"
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    Get Started
                                </Link>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
};

export default Navbar;
