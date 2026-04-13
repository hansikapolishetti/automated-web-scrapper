import React, { useState } from 'react';
import { Link } from 'react-router-dom';

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 bg-gradient-to-br from-blue-700 via-purple-700 to-cyan-500 overflow-hidden font-sans">
      
      {/* Dynamic Background Noise */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDUiLz4KPC9zdmc+')] opacity-20 mix-blend-overlay pointer-events-none"></div>
      
      {/* Background Soft Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[800px] h-[800px] bg-blue-500/30 rounded-full blur-[140px] pointer-events-none mix-blend-screen"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-cyan-400/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
      
      <div className="relative w-full max-w-md z-10 animate-fade-in-up">
        {/* Glassmorphism Card */}
        <div className="bg-white/10 backdrop-blur-2xl border border-white/20 shadow-[0_20px_50px_rgba(0,0,0,0.3)] rounded-[2rem] p-8 sm:p-10">
          
          <div className="text-center mb-8">
            <Link to="/" className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 text-white font-black text-2xl shadow-lg transition-transform hover:scale-105 hover:-rotate-3 mb-6">P</Link>
            <h2 className="text-3xl font-extrabold text-white tracking-tight mb-2">Welcome back</h2>
            <p className="text-blue-50 font-medium">Enter your details to access your dashboard.</p>
          </div>

          <button className="w-full mb-6 flex items-center justify-center gap-3 bg-white hover:bg-slate-50 text-slate-700 font-bold py-3.5 px-4 rounded-xl shadow-lg transition-all active:scale-95 border border-white/10">
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 15.01 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Continue with Google
          </button>

          <div className="flex items-center my-6">
            <div className="flex-grow border-t border-white/20"></div>
            <span className="px-4 text-xs font-bold text-white/60 tracking-wider">OR</span>
            <div className="flex-grow border-t border-white/20"></div>
          </div>

          <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
            <div>
              <label className="block text-sm font-bold text-white/90 mb-2">Email Address</label>
              <input 
                type="email" 
                className="w-full bg-white/10 border border-white/20 text-white placeholder-white/50 rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:bg-white/20 transition-all font-medium"
                placeholder="you@example.com"
                required
              />
            </div>
            
            <div className="relative">
              <label className="block text-sm font-bold text-white/90 mb-2">Password</label>
              <input 
                type={showPassword ? "text" : "password"}
                className="w-full bg-white/10 border border-white/20 text-white placeholder-white/50 rounded-xl pl-4 pr-12 py-3.5 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:bg-white/20 transition-all font-medium"
                placeholder="••••••••"
                required
              />
              <button 
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-[38px] text-white/60 hover:text-white transition-colors"
                aria-label="Toggle password visibility"
              >
                {showPassword ? (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                )}
              </button>
            </div>

            <div className="flex items-center justify-between pt-2">
              <label className="flex items-center gap-2 cursor-pointer group">
                <div className="relative flex items-center justify-center w-5 h-5 rounded border border-white/30 bg-white/10 group-hover:bg-white/20 transition-colors">
                  <input type="checkbox" className="opacity-0 absolute inset-0 cursor-pointer peer" />
                  <svg className="w-3.5 h-3.5 text-cyan-300 opacity-0 peer-checked:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-sm font-medium text-white/80 group-hover:text-white transition-colors">Remember me</span>
              </label>
              
              <a href="#" className="flex-shrink-0 text-sm font-bold text-cyan-300 hover:text-cyan-200 transition-colors">
                Forgot password?
              </a>
            </div>

            <button type="submit" className="w-full mt-6 bg-cyan-400 hover:bg-cyan-300 text-slate-900 font-extrabold py-4 px-4 rounded-xl shadow-[0_0_20px_rgba(34,211,238,0.3)] hover:shadow-[0_0_30px_rgba(34,211,238,0.5)] transition-all active:scale-95">
              Sign In
            </button>
          </form>
          
          <p className="mt-8 text-center text-sm font-medium text-white/60">
            Don't have an account? <Link to="/register" className="text-cyan-300 font-bold hover:text-cyan-200 transition-colors ml-1">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
