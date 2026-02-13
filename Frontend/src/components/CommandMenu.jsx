import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Command, ArrowRight, X, Layout, CreditCard, User, LogIn, Sparkles, Map, Database, Factory, Landmark, Building2, Sun, Moon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../Context/ThemeContext';

const CommandMenu = () => {
    const { theme, toggleTheme } = useTheme();
    const [isOpen, setIsOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const navigate = useNavigate();
    const inputRef = useRef(null);

    // Navigation and Tools Data
    const items = [
        { id: 'dashboard', name: 'Go to Dashboard', icon: Layout, category: 'Navigation', shortcut: '↵', path: '/dashboard' },
        { id: 'theme', name: `Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`, icon: theme === 'dark' ? Sun : Moon, category: 'Appearance', shortcut: 'T', action: 'toggle' },
        { id: 'pcard', name: 'PCARD Solutions', icon: CreditCard, category: 'Products', path: '/#products' },
        { id: 'sugar', name: 'Sugar Factory Suite', icon: Factory, category: 'Products', path: '/#products' },
        { id: 'pacs', name: 'PACS Core Digital', icon: Landmark, category: 'Products', path: '/#products' },
        { id: 'bank', name: 'Urban Bank System', icon: Building2, category: 'Products', path: '/#products' },
        { id: 'pricing', name: 'View Pricing Matrix', icon: CreditCard, category: 'Navigation', shortcut: 'P', path: '/#pricing' },
        { id: 'login', name: 'Login to Account', icon: LogIn, category: 'Access', shortcut: 'L', path: '/login' },
        { id: 'signup', name: 'Create New Workspace', icon: Sparkles, category: 'Access', shortcut: 'S', path: '/signup' },
        { id: 'onboarding', name: 'Run Onboarding Tour', icon: Map, category: 'Tools', shortcut: 'O', path: '/onboarding' },
        { id: 'ecosystem', name: 'All Products Ecosystem', icon: Database, category: 'Navigation', path: '/#products' },
    ];

    const filteredItems = items.filter(item =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.category.toLowerCase().includes(searchQuery.toLowerCase())
    );

    useEffect(() => {
        const handleKeyDown = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                setIsOpen(prev => !prev);
            }
            if (!isOpen) return;

            if (e.key === 'Escape') {
                setIsOpen(false);
            }

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setSelectedIndex(prev => (prev + 1) % filteredItems.length);
            }

            if (e.key === 'ArrowUp') {
                e.preventDefault();
                setSelectedIndex(prev => (prev - 1 + filteredItems.length) % filteredItems.length);
            }

            if (e.key === 'Enter') {
                e.preventDefault();
                if (filteredItems[selectedIndex]) {
                    handleSelect(filteredItems[selectedIndex]);
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, filteredItems, selectedIndex]);

    useEffect(() => {
        setSelectedIndex(0);
    }, [searchQuery]);

    useEffect(() => {
        if (isOpen) {
            setSearchQuery('');
            setSelectedIndex(0);
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen]);

    const handleSelect = (item) => {
        if (item.action === 'toggle') {
            toggleTheme();
            return;
        }
        setIsOpen(false);
        if (item.path.startsWith('/#')) {
            window.location.href = item.path;
        } else {
            navigate(item.path);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[999]"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Menu Container */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -20 }}
                        transition={{ duration: 0.2, ease: "easeOut" }}
                        className="fixed top-[15%] left-1/2 -translate-x-1/2 w-[95%] max-w-2xl bg-white/90 dark:bg-black/90 backdrop-blur-2xl border border-white/20 dark:border-white/10 rounded-[28px] shadow-[0_32px_64px_-16px_rgba(0,0,0,0.4)] z-[1000] overflow-hidden"
                    >
                        {/* Search Input */}
                        <div className="relative p-6 border-b border-black/5 dark:border-white/5">
                            <div className="absolute inset-y-0 left-8 flex items-center pointer-events-none text-apple-slate/40 dark:text-gray-400">
                                <Search className="w-6 h-6" />
                            </div>
                            <input
                                ref={inputRef}
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Type a command or search..."
                                className="w-full pl-12 pr-4 bg-transparent border-none outline-none text-xl font-bold text-apple-slate dark:text-white placeholder:text-apple-slate/20 dark:placeholder:text-white/20"
                            />
                            <div className="absolute right-8 top-1/2 -translate-y-1/2 flex items-center gap-1.5 px-2 py-1 bg-apple-slate/5 dark:bg-white/5 rounded-lg border border-apple-slate/10 dark:border-white/10 uppercase text-[10px] font-black tracking-widest opacity-40">
                                <Command className="w-3 h-3" />
                                <span>K</span>
                            </div>
                        </div>

                        {/* Results */}
                        <div className="max-h-[400px] overflow-y-auto p-2 scrollbar-hide">
                            {filteredItems.length > 0 ? (
                                <div className="space-y-1 relative">
                                    {filteredItems.map((item, index) => (
                                        <button
                                            key={item.id}
                                            onClick={() => handleSelect(item)}
                                            onMouseEnter={() => setSelectedIndex(index)}
                                            className="w-full flex items-center justify-between p-4 rounded-xl transition-all relative group overflow-hidden"
                                        >
                                            {/* Advanced Selection Highlight */}
                                            {selectedIndex === index && (
                                                <motion.div
                                                    layoutId="selection-highlight"
                                                    className="absolute inset-0 bg-apple-violet/10 dark:bg-apple-violet/20 z-0"
                                                    initial={false}
                                                    transition={{ type: "spring", bounce: 0.1, duration: 0.5 }}
                                                />
                                            )}

                                            <div className="flex items-center gap-4 relative z-10">
                                                <div className={`p-2.5 rounded-lg transition-colors duration-300 ${selectedIndex === index
                                                    ? 'bg-apple-violet text-white'
                                                    : 'bg-apple-slate/5 dark:bg-white/5 text-apple-slate/40 dark:text-gray-400'
                                                    }`}>
                                                    <item.icon className="w-5 h-5 transition-transform duration-300 group-active:scale-90" />
                                                </div>
                                                <div className="text-left">
                                                    <p className={`font-bold transition-colors ${selectedIndex === index ? 'text-apple-violet' : 'text-apple-slate dark:text-white'}`}>
                                                        {item.name}
                                                    </p>
                                                    <div className="flex items-center gap-2">
                                                        <p className="text-[10px] font-black uppercase tracking-widest opacity-40">
                                                            {item.category}
                                                        </p>
                                                        {selectedIndex === index && (
                                                            <motion.span
                                                                initial={{ opacity: 0, x: -5 }}
                                                                animate={{ opacity: 1, x: 0 }}
                                                                className="text-[10px] text-apple-violet font-black uppercase tracking-widest"
                                                            >
                                                                &bull; Quick Action
                                                            </motion.span>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-3 relative z-10">
                                                {item.shortcut && (
                                                    <div className="flex items-center gap-2">
                                                        <div className="px-2 py-0.5 rounded bg-apple-slate/5 dark:bg-white/5 border border-apple-slate/10 dark:border-white/10 text-[10px] font-black opacity-40">
                                                            {item.shortcut}
                                                        </div>
                                                    </div>
                                                )}
                                                {selectedIndex === index && (
                                                    <motion.div
                                                        initial={{ opacity: 0, x: 10 }}
                                                        animate={{ opacity: 1, x: 0 }}
                                                    >
                                                        <ArrowRight className="w-4 h-4 text-apple-violet" />
                                                    </motion.div>
                                                )}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            ) : (
                                <div className="py-20 text-center">
                                    <Sparkles className="w-12 h-12 text-apple-slate/10 dark:text-white/10 mx-auto mb-4" />
                                    <p className="text-apple-slate/40 dark:text-gray-500 font-bold">No results found for "{searchQuery}"</p>
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="px-6 py-4 bg-apple-slate/[0.02] dark:bg-white/[0.02] border-t border-black/5 dark:border-white/5 flex items-center justify-between">
                            <div className="flex items-center gap-6 opacity-30 text-[10px] font-black uppercase tracking-[0.2em]">
                                <div className="flex items-center gap-1.5">
                                    <div className="w-4 h-4 rounded-sm border border-current flex items-center justify-center">↑</div>
                                    <div className="w-4 h-4 rounded-sm border border-current flex items-center justify-center">↓</div>
                                    <span>Navigate</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <div className="px-1 border border-current rounded-sm flex items-center justify-center">↵</div>
                                    <span>Select</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <div className="px-1 border border-current rounded-sm flex items-center justify-center">ESC</div>
                                    <span>Close</span>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 text-apple-violet font-black text-xs">
                                <span>MultiProduct OS</span>
                                <div className="w-1.5 h-1.5 rounded-full bg-apple-violet animate-pulse" />
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default CommandMenu;
