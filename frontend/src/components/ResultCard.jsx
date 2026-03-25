import React from 'react';
import { Award, Target, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

const ResultCard = ({ score, explanation, llmInsights }) => {
  const getScoreTheme = (s) => {
    if (s >= 80) return {
       color: 'text-green-400',
       bg: 'from-green-500/10 to-transparent',
       border: 'border-green-500/20',
       glow: 'shadow-green-500/10'
    };
    if (s >= 60) return {
       color: 'text-yellow-400',
       bg: 'from-yellow-500/10 to-transparent',
       border: 'border-yellow-500/20',
       glow: 'shadow-yellow-500/10'
    };
    return {
       color: 'text-red-400',
       bg: 'from-red-500/10 to-transparent',
       border: 'border-red-500/20',
       glow: 'shadow-red-500/10'
    };
  };

  const theme = getScoreTheme(score);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`premium-card p-10 border bg-gradient-to-br ${theme.bg} ${theme.border} ${theme.glow}`}
    >
      <div className="flex flex-col lg:flex-row items-center gap-12">
        <div className="relative group">
          <div className={`absolute inset-0 blur-3xl opacity-20 group-hover:opacity-40 transition-opacity rounded-full ${theme.color.replace('text', 'bg')}`}></div>
          <svg className="w-40 h-40 transform -rotate-90 relative z-10">
            <circle
              cx="80"
              cy="80"
              r="72"
              stroke="currentColor"
              strokeWidth="12"
              fill="transparent"
              className="text-white/5"
            />
            <motion.circle
              cx="80"
              cy="80"
              r="72"
              stroke="currentColor"
              strokeWidth="12"
              fill="transparent"
              strokeDasharray={452}
              initial={{ strokeDashoffset: 452 }}
              animate={{ strokeDashoffset: 452 - (452 * score) / 100 }}
              strokeLinecap="round"
              className={`${theme.color} transition-all duration-1000 ease-out`}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center relative z-10">
            <span className={`text-4xl font-black ${theme.color}`}>{Math.round(score)}%</span>
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Match</span>
          </div>
        </div>

        <div className="flex-1 text-center lg:text-left">
          <div className="flex items-center justify-center lg:justify-start gap-3 mb-6">
             <div className={`p-2 rounded-lg ${theme.bg} ${theme.border}`}>
                <Award className={`${theme.color} w-6 h-6`} />
             </div>
             <h2 className="text-3xl font-black text-white tracking-tight">Match Analysis</h2>
          </div>
          <div className="relative">
            <span className="absolute -left-4 -top-4 text-6xl text-white/5 font-serif">"</span>
            <p className="text-slate-300 leading-relaxed text-lg relative z-10 font-medium">
              {explanation}
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center lg:justify-start gap-4 text-xs font-black uppercase tracking-widest text-slate-500">
               <div className="flex items-center gap-2 bg-slate-900/50 px-3 py-1.5 rounded-lg"><Target size={14} className="text-primary-400" /> Precision Engine v4.0</div>
               <div className="flex items-center gap-2 bg-slate-900/50 px-3 py-1.5 rounded-lg"><Sparkles size={14} className="text-primary-400" /> RAG Powered</div>
               {llmInsights?.hire_signal && (
                 <div className="flex items-center gap-2 bg-white/10 border border-white/10 px-3 py-1.5 rounded-lg text-white shadow-lg shadow-white/5">
                   Signal: <span className="text-primary-400">{llmInsights.hire_signal}</span>
                 </div>
               )}
               {llmInsights?.confidence_score && (
                 <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg text-white">
                   Confidence: <span className="text-indigo-400">{llmInsights.confidence_score}</span>
                 </div>
               )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ResultCard;
