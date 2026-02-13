import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import {
    Layers, User, Bell, Search, Settings, ArrowUpRight, ArrowDownRight, Activity,
    CreditCard, Shield, Zap, Globe, MessageSquare, Plus, CheckCircle2, Clock,
    Cpu, Database, HardDrive
} from 'lucide-react';

const data = [
    { name: 'Mon', usage: 400 },
    { name: 'Tue', usage: 300 },
    { name: 'Wed', usage: 600 },
    { name: 'Thu', usage: 800 },
    { name: 'Fri', usage: 500 },
    { name: 'Sat', usage: 900 },
    { name: 'Sun', usage: 1100 },
];

const TimeRangeSelector = ({ activeRange, setRange }) => (
    <div className="flex bg-black/5 dark:bg-white/5 p-1 rounded-xl border border-black/5 dark:border-white/5">
        {['1D', '7D', '1M', '1Y'].map((range) => (
            <button
                key={range}
                onClick={() => setRange(range)}
                className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${activeRange === range
                    ? 'bg-white dark:bg-white/10 shadow-sm text-apple-indigo opacity-100'
                    : 'opacity-40 hover:opacity-60'
                    }`}
            >
                {range}
            </button>
        ))}
    </div>
);

const ResourceGauge = ({ label, value, icon: Icon, color }) => (
    <div className="bento-card p-6 flex flex-col items-center justify-center relative overflow-hidden group">
        <div className={`absolute top-0 right-0 w-24 h-24 -mr-8 -mt-8 rounded-full opacity-10 blur-2xl transition-all duration-500 group-hover:scale-150 ${color}`} />
        <div className="relative z-10 flex flex-col items-center">
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-4 ${color.replace('bg-', 'text-').replace('blur-2xl', '')} bg-opacity-10`}>
                <Icon className="w-6 h-6" />
            </div>
            <div className="text-center">
                <p className="text-[10px] font-black uppercase tracking-widest opacity-40 mb-1">{label}</p>
                <div className="flex items-end justify-center gap-1">
                    <span className="text-2xl font-black">{value}</span>
                    <span className="text-[10px] font-bold opacity-30 mb-1">%</span>
                </div>
            </div>
            <div className="w-full h-1.5 bg-black/5 dark:bg-white/5 rounded-full mt-4 overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    className={`h-full rounded-full ${color.split(' ')[0]}`}
                />
            </div>
        </div>
    </div>
);



const OverviewView = ({ stats }) => {
    const [trafficRange, setTrafficRange] = useState('7D');
    const [productRange, setProductRange] = useState('1M');

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-8 md:space-y-12"
        >
            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 md:gap-6">
                {stats.map((stat, i) => (
                    <div key={i} className="bento-card p-6 transition-all duration-300 hover:scale-[1.02]">
                        <p className="text-[10px] font-black uppercase tracking-widest opacity-40 mb-2">{stat.label}</p>
                        <h3 className="text-2xl md:text-3xl font-black mb-1">{stat.val}</h3>
                        <div className={`flex items-center text-xs font-bold ${stat.up ? 'text-green-500' : 'text-red-500'}`}>
                            {stat.up ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                            {stat.delta}
                        </div>
                    </div>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 md:gap-8">
                <div className="bento-card p-6 md:p-8 min-h-[350px] md:min-h-[400px]">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
                        <h3 className="text-base md:text-lg font-black">Service Traffic</h3>
                        <TimeRangeSelector activeRange={trafficRange} setRange={setTrafficRange} />
                    </div>
                    <div className="h-[250px] md:h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data}>
                                <defs>
                                    <linearGradient id="colorUsage" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#88888822" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 700 }} />
                                <YAxis hide />
                                <Tooltip contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', background: 'rgba(255,255,255,0.8)', backdropFilter: 'blur(10px)' }} />
                                <Area type="monotone" dataKey="usage" stroke="#7c3aed" strokeWidth={3} fillOpacity={1} fill="url(#colorUsage)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="bento-card p-6 md:p-8 min-h-[350px] md:min-h-[400px]">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
                        <h3 className="text-base md:text-lg font-black">Product Distribution</h3>
                        <TimeRangeSelector activeRange={productRange} setRange={setProductRange} />
                    </div>
                    <div className="h-[250px] md:h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#88888822" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 700 }} />
                                <YAxis hide />
                                <Tooltip cursor={{ fill: '#88888811' }} contentStyle={{ borderRadius: '16px', border: 'none', background: 'rgba(255,255,255,0.8)', backdropFilter: 'blur(10px)' }} />
                                <Bar dataKey="usage" fill="#4338ca" radius={[6, 6, 6, 6]} barSize={24} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Resource Health Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
                <ResourceGauge label="CPU Usage" value={24} icon={Cpu} color="bg-apple-blue shadow-apple-blue/20" />
                <ResourceGauge label="Memory" value={68} icon={Activity} color="bg-apple-violet shadow-apple-violet/20" />
                <ResourceGauge label="Database" value={12} icon={Database} color="bg-apple-indigo shadow-apple-indigo/20" />
                <ResourceGauge label="Storage" value={45} icon={HardDrive} color="bg-apple-slate dark:bg-white shadow-apple-slate/20" />
            </div>

            {/* Bottom Bento Feed */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
                <div className="lg:col-span-2 bento-card p-6 md:p-8">
                    <h3 className="text-base md:text-lg font-black mb-6">Recent Activity</h3>
                    <div className="space-y-5 md:space-y-6">
                        {[...Array(3)].map((_, i) => (
                            <div key={i} className="flex items-center justify-between group cursor-pointer active:scale-[0.99] transition-transform">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 md:w-11 md:h-11 bg-apple-indigo/10 rounded-[14px] flex items-center justify-center text-apple-indigo shadow-sm">
                                        <Activity className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold truncate max-w-[150px] sm:max-w-none">New Subscription: CRM Pro</p>
                                        <p className="text-[10px] opacity-60 uppercase font-bold text-xs tracking-widest mt-0.5 font-black">2 minutes ago</p>
                                    </div>
                                </div>
                                <button className="opacity-0 group-hover:opacity-100 p-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg transition-all hidden sm:block">
                                    <ArrowUpRight className="w-4 h-4" />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="rounded-[28px] p-8 md:p-10 bg-gradient-to-br from-apple-indigo to-apple-violet text-white shadow-2xl relative overflow-hidden group">
                    <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-1000" />
                    <div className="relative z-10">
                        <h3 className="text-xl font-bold mb-4">System Health</h3>
                        <div className="text-5xl font-black mb-2 tracking-tighter">99.9%</div>
                        <p className="text-xs md:text-sm text-white/60 mb-8 font-medium leading-relaxed">All systems operational across 23 nodes with zero detected anomalies.</p>
                        <button className="w-full py-3.5 bg-white text-apple-indigo font-black rounded-xl text-sm shadow-xl active:scale-[0.98] transition-transform">
                            View Status Page
                        </button>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

const MyProductsView = () => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="space-y-8"
    >
        <div className="flex justify-between items-center">
            <h2 className="text-2xl font-black">My Subscriptions</h2>
            <button className="bg-apple-indigo text-white px-6 py-2.5 rounded-xl font-bold text-sm flex items-center gap-2 hover:scale-105 active:scale-95 transition-all shadow-lg">
                <Plus className="w-4 h-4" />
                Add Product
            </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
                { name: "CRM Enterprise", icon: <Globe className="w-6 h-6" />, status: "Active", usage: "85%", billing: "Monthly" },
                { name: "Ad Manager", icon: <Zap className="w-6 h-6" />, status: "Active", usage: "42%", billing: "Yearly" },
                { name: "Email Automator", icon: <MessageSquare className="w-6 h-6" />, status: "Paused", usage: "0%", billing: "Monthly" }
            ].map((product, i) => (
                <div key={i} className="bento-card p-6 flex items-center justify-between group">
                    <div className="flex items-center gap-5">
                        <div className="w-14 h-14 bg-apple-indigo/10 rounded-2xl flex items-center justify-center text-apple-indigo">
                            {product.icon}
                        </div>
                        <div>
                            <h4 className="font-bold text-lg">{product.name}</h4>
                            <p className="text-[10px] font-black uppercase tracking-widest opacity-40">{product.billing} Plan</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <span className={`text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full ${product.status === 'Active' ? 'bg-green-500/10 text-green-500' : 'bg-orange-500/10 text-orange-500'}`}>
                            {product.status}
                        </span>
                        <p className="mt-2 text-xs font-bold opacity-60">Usage: {product.usage}</p>
                    </div>
                </div>
            ))}
        </div>
    </motion.div>
);

const NotificationsView = () => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="space-y-6 max-w-3xl"
    >
        <h2 className="text-2xl font-black mb-8">Notifications</h2>
        {[
            { title: "System Update", desc: "v2.4.0 is now live with enhanced security patches.", type: "update", time: "5m ago" },
            { title: "Subscription Renewal", desc: "Your CRM Enterprise plan was renewed successfully.", type: "billing", time: "2h ago" },
            { title: "Security Alert", desc: "New login detected from Mumbai, India.", type: "alert", time: "1d ago" },
            { title: "Welcome", desc: "Thanks for joining MultiProduct! Take a tour.", type: "welcome", time: "3d ago" },
        ].map((notif, i) => (
            <div key={i} className="bento-card p-5 flex gap-5 hover:scale-[1.01] cursor-pointer">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${notif.type === 'alert' ? 'bg-red-500/10 text-red-500' :
                    notif.type === 'billing' ? 'bg-green-500/10 text-green-500' : 'bg-apple-indigo/10 text-apple-indigo'
                    }`}>
                    {notif.type === 'alert' ? <Shield className="w-6 h-6" /> : <Bell className="w-6 h-6" />}
                </div>
                <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                        <h4 className="font-bold">{notif.title}</h4>
                        <span className="text-[10px] font-bold opacity-30 uppercase tracking-widest">{notif.time}</span>
                    </div>
                    <p className="text-sm opacity-60 leading-relaxed">{notif.desc}</p>
                </div>
            </div>
        ))}
    </motion.div>
);

const SettingsView = () => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="space-y-10"
    >
        <h2 className="text-2xl font-black mb-4">Account Settings</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-1 space-y-4">
                <div className="bento-card p-8 flex flex-col items-center text-center">
                    <div className="w-24 h-24 rounded-full bg-apple-indigo/10 flex items-center justify-center border-2 border-apple-indigo/20 mb-4 group cursor-pointer relative overflow-hidden">
                        <User className="w-10 h-10 text-apple-indigo" />
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                            <Plus className="text-white w-6 h-6" />
                        </div>
                    </div>
                    <h3 className="font-bold text-xl">Stark System</h3>
                    <p className="text-xs opacity-40 font-black uppercase tracking-widest mt-1">Administrator</p>
                </div>

                <div className="bento-card p-4 space-y-1">
                    {['Profile', 'Security', 'Billing', 'Team'].map((tab, i) => (
                        <button key={i} className={`w-full text-left px-4 py-2.5 rounded-xl font-bold text-sm transition-all ${i === 0 ? 'bg-apple-indigo text-white' : 'hover:bg-apple-slate/5 dark:hover:bg-white/5 opacity-60'}`}>
                            {tab}
                        </button>
                    ))}
                </div>
            </div>

            <div className="md:col-span-2 space-y-6">
                <div className="bento-card p-8">
                    <h4 className="font-bold text-lg mb-6">Personal Information</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        {['First Name', 'Last Name', 'Email Address', 'Company'].map((field, i) => (
                            <div key={i} className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest opacity-60">{field}</label>
                                <input
                                    type="text"
                                    placeholder={field}
                                    className="w-full bg-apple-slate/5 dark:bg-white/5 border border-apple-slate/10 dark:border-white/10 rounded-xl px-4 py-3 text-sm focus:ring-2 ring-apple-indigo/50 outline-none transition-all"
                                />
                            </div>
                        ))}
                    </div>
                    <button className="mt-8 bg-apple-indigo text-white px-8 py-3 rounded-xl font-bold text-sm hover:scale-105 active:scale-95 transition-all shadow-lg">
                        Save Changes
                    </button>
                </div>

                <div className="bento-card p-8 border-red-500/20">
                    <h4 className="font-bold text-lg mb-2 text-red-500">Danger Zone</h4>
                    <p className="text-sm opacity-40 mb-6 font-medium">Permanently delete your account and all associated data.</p>
                    <button className="bg-red-500/10 text-red-500 border border-red-500/20 px-8 py-3 rounded-xl font-bold text-sm hover:bg-red-500 hover:text-white transition-all">
                        Delete Account
                    </button>
                </div>
            </div>
        </div>
    </motion.div>
);

const AdminView = () => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="space-y-10"
    >
        <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-black">Admin Console</h2>
            <div className="flex gap-4">
                <button className="bg-apple-indigo/10 text-apple-indigo px-6 py-2.5 rounded-xl font-bold text-sm hover:bg-apple-indigo hover:text-white transition-all">
                    System Audit
                </button>
                <button className="bg-apple-indigo text-white px-6 py-2.5 rounded-xl font-bold text-sm shadow-xl hover:scale-105 active:scale-95 transition-all">
                    Export Data
                </button>
            </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
                <div className="bento-card p-0 overflow-hidden">
                    <div className="px-8 py-6 border-b border-black/5 dark:border-white/5 flex justify-between items-center">
                        <h3 className="font-bold text-lg">User Management</h3>
                        <span className="text-[10px] font-black uppercase tracking-widest opacity-40">2,842 Total Users</span>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-apple-slate/[0.02] dark:bg-white/[0.02] text-[10px] font-black uppercase tracking-widest opacity-40">
                                    <th className="px-8 py-4">User</th>
                                    <th className="px-8 py-4">Role</th>
                                    <th className="px-8 py-4">Status</th>
                                    <th className="px-8 py-4">Action</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm font-bold">
                                {[
                                    { name: "Alex Rivet", email: "alex@stark.com", role: "Editor", status: "Active" },
                                    { name: "Sarah Chen", email: "sarah@media.io", role: "Subscriber", status: "Active" },
                                    { name: "Marcus Vane", email: "marcus@dev.net", role: "Guest", status: "Pending" },
                                    { name: "Elena Rossi", email: "elena@design.it", role: "Admin", status: "Active" },
                                ].map((user, i) => (
                                    <tr key={i} className="border-t border-black/5 dark:border-white/5 hover:bg-apple-slate/[0.01] dark:hover:bg-white/[0.01] transition-colors">
                                        <td className="px-8 py-5">
                                            <div>
                                                <p>{user.name}</p>
                                                <p className="text-[10px] opacity-40 font-medium">{user.email}</p>
                                            </div>
                                        </td>
                                        <td className="px-8 py-5 opacity-60 font-medium">{user.role}</td>
                                        <td className="px-8 py-5">
                                            <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${user.status === 'Active' ? 'bg-green-500/10 text-green-500' : 'bg-orange-500/10 text-orange-500'
                                                }`}>
                                                {user.status}
                                            </span>
                                        </td>
                                        <td className="px-8 py-5">
                                            <button className="text-apple-indigo hover:underline">Edit</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div className="space-y-8">
                <div className="bento-card p-8 bg-apple-indigo text-white">
                    <h3 className="font-bold text-lg mb-4">System Maintenance</h3>
                    <div className="space-y-4 mb-8">
                        <div className="flex justify-between items-center text-xs">
                            <span className="opacity-60">Database Integrity</span>
                            <CheckCircle2 className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex justify-between items-center text-xs">
                            <span className="opacity-60">API Gateway</span>
                            <CheckCircle2 className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex justify-between items-center text-xs">
                            <span className="opacity-60">Asset Cache</span>
                            <Clock className="w-4 h-4 text-white/50" />
                        </div>
                    </div>
                    <button className="w-full py-3 bg-white/20 backdrop-blur-md border border-white/20 rounded-xl font-bold text-sm hover:bg-white/30 transition-all">
                        Run Diagnostics
                    </button>
                </div>

                <div className="bento-card p-8">
                    <h3 className="font-bold text-lg mb-6">Security Logs</h3>
                    <div className="space-y-5">
                        {[
                            { event: "Login Attempt", status: "Success", time: "2m ago" },
                            { event: "API Key Gen", status: "Success", time: "15m ago" },
                            { event: "Config Change", status: "Warning", time: "1h ago" },
                        ].map((log, i) => (
                            <div key={i} className="flex justify-between items-center border-b border-black/5 dark:border-white/5 pb-4 last:border-0 last:pb-0">
                                <div>
                                    <p className="text-xs font-bold">{log.event}</p>
                                    <p className="text-[10px] opacity-40 font-medium">{log.time}</p>
                                </div>
                                <span className={`text-[9px] font-black uppercase tracking-widest ${log.status === 'Warning' ? 'text-orange-500' : 'text-green-500'}`}>
                                    {log.status}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    </motion.div>
);

const Dashboard = () => {
    const [activeView, setActiveView] = useState('Overview');

    const stats = [
        { label: "Total Usage", val: "12,940", delta: "+12%", up: true },
        { label: "Active Subs", val: "842", delta: "+5.4%", up: true },
        { label: "Avg Uptime", val: "99.98%", delta: "-0.01%", up: false },
        { label: "System Load", val: "24%", delta: "-10%", up: true },
    ];

    const menuItems = [
        { icon: <Activity className="w-5 h-5" />, label: "Overview" },
        { icon: <Layers className="w-5 h-5" />, label: "My Products" },
        { icon: <Shield className="w-5 h-5" />, label: "Admin" },
        { icon: <Bell className="w-5 h-5" />, label: "Notifications" },
        { icon: <Settings className="w-5 h-5" />, label: "Settings" },
    ];

    return (
        <div className="min-h-screen bg-apple-gray dark:bg-[#050505] flex">
            {/* Sidebar (Hidden on mobile) */}
            <aside className="w-20 md:w-64 h-screen glass border-r border-apple-slate/5 dark:border-white/5 sticky top-0 md:flex flex-col hidden z-40">
                <div className="p-8">
                    <div className="bg-gradient-to-tr from-apple-indigo to-apple-violet p-2 rounded-xl inline-block shadow-lg">
                        <Layers className="w-6 h-6 text-white" />
                    </div>
                </div>

                <nav className="flex-1 px-4 space-y-2">
                    {menuItems.map((item, i) => (
                        <button
                            key={i}
                            onClick={() => setActiveView(item.label)}
                            className={`w-full flex items-center gap-4 px-4 py-3 rounded-2xl transition-all active:scale-95 ${activeView === item.label ? 'bg-apple-slate dark:bg-white text-white dark:text-apple-slate font-bold shadow-xl' : 'hover:bg-apple-slate/5 dark:hover:bg-white/5 opacity-60'
                                }`}
                        >
                            {item.icon}
                            <span className="hidden md:block">{item.label}</span>
                        </button>
                    ))}
                </nav>

                <div className="p-4 border-t border-apple-slate/5 dark:border-white/5">
                    <div className="flex items-center gap-3 p-2">
                        <div className="w-10 h-10 rounded-full bg-apple-indigo/20 flex items-center justify-center border border-apple-indigo/30">
                            <User className="w-5 h-5 text-apple-indigo" />
                        </div>
                        <div className="hidden md:block overflow-hidden">
                            <p className="text-xs font-bold truncate">Stark System</p>
                            <p className="text-[10px] opacity-40 uppercase font-black tracking-widest">Admin</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 min-h-screen p-5 md:p-12 overflow-x-hidden">
                {/* Mobile Header (Only on mobile) */}
                <header className="flex md:hidden justify-between items-center mb-10">
                    <div className="flex items-center gap-3">
                        <div className="bg-gradient-to-tr from-apple-indigo to-apple-violet p-1.5 rounded-xl">
                            <Layers className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-xl font-black tracking-tight">MultiProduct</span>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-apple-indigo/10 flex items-center justify-center border border-apple-indigo/20">
                        <User className="w-5 h-5 text-apple-indigo" />
                    </div>
                </header>

                {/* Desktop Header */}
                <header className="hidden md:flex justify-between items-center mb-12">
                    <div>
                        <h1 className="text-4xl font-black tracking-tight">{activeView}.</h1>
                        <p className="opacity-40 text-xs font-black uppercase tracking-widest mt-1">
                            {activeView === 'Overview' ? 'Real-time product performance' :
                                activeView === 'My Products' ? 'Manage your ecosystem' :
                                    activeView === 'Notifications' ? 'Stay updated with your account' :
                                        activeView === 'Admin' ? 'Enterprise management tools' : 'Configure your experience'}
                        </p>
                    </div>
                    <div className="flex gap-4">
                        <button className="p-3 bg-white dark:bg-white/5 rounded-2xl border border-apple-slate/5 shadow-sm hover:scale-110 active:scale-95 transition-all">
                            <Search className="w-5 h-5" />
                        </button>
                        <button
                            onClick={() => setActiveView('Notifications')}
                            className={`p-3 bg-white dark:bg-white/5 rounded-2xl border border-apple-slate/5 shadow-sm hover:scale-110 active:scale-95 transition-all relative ${activeView === 'Notifications' ? 'ring-2 ring-apple-indigo' : ''}`}
                        >
                            <Bell className="w-5 h-5" />
                            <div className="absolute top-3 right-3 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-black shadow-sm" />
                        </button>
                    </div>
                </header>

                {/* View Content */}
                <AnimatePresence mode="wait">
                    {activeView === 'Overview' && <OverviewView key="overview" stats={stats} />}
                    {activeView === 'My Products' && <MyProductsView key="products" />}
                    {activeView === 'Notifications' && <NotificationsView key="notifications" />}
                    {activeView === 'Settings' && <SettingsView key="settings" />}
                    {activeView === 'Admin' && <AdminView key="admin" />}
                </AnimatePresence>
            </main>
        </div>
    );
};

export default Dashboard;
