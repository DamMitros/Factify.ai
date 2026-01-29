'use client';

import React, { JSX } from "react";
import GlassEffect from "./GlassEffect";
import { useKeycloak } from "../../auth/KeycloakProviderWrapper";

interface AuthModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps): JSX.Element | null {
    const { keycloak } = useKeycloak();

    if (!isOpen) return null;

    const handleLogin = () => {
        keycloak?.login();
    };

    const handleSignup = () => {
        if (keycloak) {
            keycloak.register();
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <GlassEffect className="w-full max-w-md rounded-2xl border border-white/10 bg-[#0f0f0f] shadow-2xl overflow-hidden">
                <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/5">
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Authentication Required</span>
                    <button 
                        onClick={onClose} 
                        className="text-gray-500 hover:text-white transition-colors p-1.5 hover:bg-white/10 rounded-full"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                
                <div className="p-8 flex flex-col items-center text-center">
                    <div className="w-16 h-16 bg-purple-500/10 rounded-full flex items-center justify-center mb-6 border border-purple-500/20">
                        <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                    </div>
                    
                    <h3 className="text-xl font-bold text-white mb-3">Sign in to continue</h3>
                    <p className="text-gray-400 mb-8 leading-relaxed">
                        You need to be logged in to use this analysis feature. 
                        Please log in or create an account to unlock full access.
                    </p>
                    
                    <div className="flex flex-col w-full gap-3">
                        <button 
                            onClick={handleLogin}
                            className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl transition-all shadow-lg shadow-indigo-500/20 active:scale-[0.98]"
                        >
                            Log In
                        </button>
                        <button 
                            onClick={handleSignup}
                            className="w-full py-3 px-4 bg-white/5 hover:bg-white/10 text-white font-semibold rounded-xl border border-white/10 transition-all active:scale-[0.98]"
                        >
                            Create an account
                        </button>
                    </div>
                </div>
            </GlassEffect>
        </div>
    );
}
