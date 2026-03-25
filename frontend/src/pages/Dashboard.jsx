import React, { useState, useEffect } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, LayoutDashboard, FileText, Trophy, ExternalLink, Award } from 'lucide-react';
import ResultCard from '../components/ResultCard';
import SkillGap from '../components/SkillGap';
import AIPerfectMatch from '../components/AIPerfectMatch';
import { motion, AnimatePresence } from 'framer-motion';

const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState(location.state || null);

  useEffect(() => {
    window.scrollTo(0, 0);
    if (!data) {
      const saved = localStorage.getItem('lastAnalysis');
      if (saved) setData(JSON.parse(saved));
    }
  }, [data]);

  if (!data) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center text-center p-8">
        <div className="bg-slate-900/50 p-8 rounded-3xl border border-white/5 animate-pulse">
          <LayoutDashboard className="w-16 h-16 text-slate-700 mx-auto mb-6" />
          <h2 className="text-3xl font-black text-slate-400 mb-4">No Analysis Found</h2>
          <p className="text-slate-500 max-w-xs mx-auto mb-8">Perform your first intelligent match on the home page to see insights here.</p>
          <Link to="/" className="inline-block bg-primary-600 hover:bg-primary-500 text-white px-8 py-3 rounded-2xl font-bold transition-all shadow-xl shadow-primary-500/20">
            Go to Workspace
          </Link>
        </div>
      </div>
    );
  }

  const { result, results, isMulti } = data;

  return (
    <div className="max-w-6xl mx-auto py-12 px-4 space-y-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <button 
            onClick={() => navigate('/')} 
            className="group flex items-center gap-2 text-slate-500 hover:text-primary-400 transition-colors mb-4 text-sm font-bold uppercase tracking-widest"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            New Analysis
          </button>
          <h1 className="text-4xl md:text-5xl font-black flex items-center gap-4">
             <div className="p-3 bg-primary-600 rounded-2xl"><LayoutDashboard className="text-white w-8 h-8" /></div>
             Result <span className="text-primary-400">Insights</span>
          </h1>
        </div>
        <div className="bg-white/5 px-6 py-3 rounded-2xl border border-white/10">
           <span className="text-xs font-black text-slate-500 uppercase block mb-1">Mode</span>
           <span className="text-lg font-bold text-primary-400 tracking-tight">{isMulti ? 'Multi-Candidate Ranking' : 'Individual Deep Dive'}</span>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {!isMulti ? (
          <motion.div 
            key="single"
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }} 
            exit={{ opacity: 0, y: -20 }}
            className="space-y-12"
          >
            <div className="grid gap-8">
               <ResultCard score={result.score} explanation={result.llm_insights?.refined_match_summary || result.explanation} />
            </div>

            <AIPerfectMatch idealResume={result.ideal_resume} />

            <SkillGap 
              strongSkills={result.strong_skills} 
              missingSkills={result.missing_skills} 
              suggestions={result.suggestions} 
              llmInsights={result.llm_insights}
            />
          </motion.div>
        ) : (
          <motion.div 
            key="multi"
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }}
            className="space-y-12"
          >
            {/* Top Match Hero */}
            <div className="premium-card p-10 bg-gradient-to-br from-primary-600/20 via-transparent to-transparent border-primary-500/20">
               <div className="flex flex-col md:flex-row gap-8 items-center">
                  <div className="relative">
                    <div className="absolute inset-0 bg-primary-500 blur-2xl opacity-20 animate-pulse"></div>
                    <div className="relative bg-primary-600 p-6 rounded-3xl shadow-2xl">
                       <Award className="text-white w-12 h-12" />
                    </div>
                  </div>
                  <div className="flex-1 text-center md:text-left">
                     <h2 className="text-3xl font-black mb-3">Top Match Identified</h2>
                     <p className="text-slate-300 text-lg max-w-2xl leading-relaxed">
                       Based on semantic RAG analysis, <span className="text-white font-black underline decoration-primary-500 underline-offset-4">{results.candidates[0].filename}</span> is the superior match with a score of <span className="text-primary-400 font-bold">{results.candidates[0].score}%</span>.
                     </p>
                  </div>
               </div>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {results.candidates.map((candidate, idx) => (
                <motion.div 
                  key={idx} 
                  initial={{ opacity: 0, y: 20 }} 
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="premium-card p-8 group border-white/5 hover:bg-white/[0.02]"
                >
                  <div className="flex items-center justify-between mb-8">
                     <div className="bg-slate-800 p-3 rounded-2xl group-hover:bg-primary-600 transition-all duration-300 group-hover:scale-110 group-hover:rotate-3">
                       <FileText className="w-6 h-6 text-primary-400 group-hover:text-white" />
                     </div>
                     <div className="text-right">
                       <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Rank</span>
                       <div className="text-3xl font-black text-primary-400 drop-shadow-lg">#{candidate.rank}</div>
                     </div>
                  </div>

                  <h3 className="font-black text-xl mb-2 truncate text-white">{candidate.filename}</h3>
                  <div className="flex items-center gap-4 mb-6">
                     <div className="h-3 flex-1 bg-slate-800 rounded-full overflow-hidden p-[2px]">
                        <motion.div 
                          className="h-full bg-gradient-to-r from-primary-600 to-blue-400 rounded-full" 
                          initial={{ width: 0 }}
                          animate={{ width: `${candidate.score}%` }}
                          transition={{ duration: 1, delay: 0.5 }}
                        ></motion.div>
                     </div>
                     <span className="text-lg font-black text-primary-400">{Math.round(candidate.score)}%</span>
                  </div>

                  <p className="text-slate-400 text-sm leading-relaxed mb-8 italic line-clamp-3">
                    "{candidate.ranking_reason}"
                  </p>

                  <button 
                    onClick={() => setData({ result: candidate, isMulti: false })}
                    className="w-full bg-white/5 hover:bg-primary-600 text-slate-300 hover:text-white py-3 rounded-2xl text-sm font-bold transition-all border border-white/5 hover:border-primary-500 flex items-center justify-center gap-2 group/btn"
                  >
                    Deep Dive Analysis
                    <ExternalLink size={14} className="group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
                  </button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Dashboard;
