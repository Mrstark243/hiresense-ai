import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import UploadForm from '../components/UploadForm';
import { analyzeResume, rankCandidates, generateIdealResume } from '../services/api';
import { Loader2, Zap, Shield, Target, ArrowRight, Sparkles, Cpu, BookOpen } from 'lucide-react';
import AIPerfectMatch from '../components/AIPerfectMatch';
import { motion, AnimatePresence } from 'framer-motion';

const Home = () => {
  const [files, setFiles] = useState([]);
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [isMulti, setIsMulti] = useState(false);
  const [idealBlueprint, setIdealBlueprint] = useState(null);
  const [blueprintLoading, setBlueprintLoading] = useState(false);
  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (!jdText || files.length === 0) return;
    setLoading(true);
    try {
      let data;
      if (isMulti) {
        data = await rankCandidates(files, jdText);
        localStorage.setItem('lastAnalysis', JSON.stringify({ results: data, isMulti: true }));
        navigate('/dashboard', { state: { results: data, isMulti: true } });
      } else {
        data = await analyzeResume(files[0], jdText);
        localStorage.setItem('lastAnalysis', JSON.stringify({ result: data, isMulti: false }));
        navigate('/dashboard', { state: { result: data, isMulti: false } });
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBlueprint = async () => {
    if (!jdText) return;
    setBlueprintLoading(true);
    try {
      const data = await generateIdealResume(jdText);
      setIdealBlueprint(data);
    } catch (error) {
       console.error('Failed to generate blueprint:', error);
    } finally {
      setBlueprintLoading(false);
    }
  };

  const scrollToAnalyze = () => {
    document.getElementById('analyze-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="space-y-24 pb-24">
      {/* Hero Section */}
      <section className="min-h-[85vh] flex flex-col items-center justify-center text-center px-4 pt-20">
        <motion.div
           initial={{ opacity: 0, scale: 0.9 }}
           animate={{ opacity: 1, scale: 1 }}
           className="inline-flex items-center gap-2 bg-primary-500/10 text-primary-400 px-4 py-2 rounded-full text-sm font-bold mb-8 border border-primary-500/20"
        >
          <Sparkles size={16} />
          <span>Next-Gen Recruitment Intelligence</span>
        </motion.div>
        
        <motion.h1 
          className="text-6xl md:text-8xl font-black mb-8 tracking-tight leading-[1.1]"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
        >
          Hire with <br /><span className="gradient-text">Absolute Precision</span>
        </motion.h1>
        
        <motion.p 
          className="text-xl text-slate-400 max-w-2xl mx-auto mb-12 leading-relaxed"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Stop guessing. Use AI-powered RAG to analyze resumes against job descriptions with recruiter-level reasoning.
        </motion.p>

        <motion.button
          onClick={scrollToAnalyze}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="group flex items-center gap-3 bg-white text-[#020617] px-8 py-4 rounded-full font-bold text-lg hover:bg-primary-500 hover:text-white transition-all duration-300 shadow-2xl shadow-white/5 hover:shadow-primary-500/20"
        >
          Get Started Now
          <ArrowRight className="group-hover:translate-x-1 transition-transform" />
        </motion.button>
      </section>

      {/* Analysis Workspace */}
      <section id="analyze-section" className="container mx-auto px-4 scroll-mt-32">
        <div className="text-center mb-12">
           <h2 className="text-3xl font-bold mb-4">Analysis Workspace</h2>
           <p className="text-slate-500 italic">"Simulating recruiter-level decision making at scale."</p>
        </div>

        <div className="premium-card p-1 overflow-hidden">
          <div className="grid lg:grid-cols-12 gap-1">
            {/* Left Box: Resumes */}
            <div className="lg:col-span-5 bg-slate-900/40 p-8">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-xl font-bold flex items-center gap-3">
                  <div className="p-2 bg-primary-600/20 rounded-lg"><Zap className="text-primary-400 w-5 h-5" /></div>
                  Resumes
                </h3>
                <button 
                  onClick={() => setIsMulti(!isMulti)}
                  className="text-xs font-bold text-primary-400 hover:text-white bg-primary-500/10 hover:bg-primary-500 px-4 py-2 rounded-full transition-all border border-primary-500/20"
                >
                  {isMulti ? 'Switch to Single' : 'Switch to Ranking'}
                </button>
              </div>
              <UploadForm onFilesSelect={setFiles} multiple={isMulti} />
              <div className="mt-8 p-4 bg-primary-500/5 rounded-2xl border border-primary-500/10">
                 <p className="text-xs text-slate-400 leading-relaxed">
                   <span className="font-bold text-primary-400">Pro Tip:</span> Ranking mode allows you to compare multiple candidates against the same JD simultaneously.
                 </p>
              </div>
            </div>

            {/* Right Box: JD */}
            <div className="lg:col-span-7 bg-slate-900/60 p-8 border-l border-white/5">
              <h3 className="text-xl font-bold mb-8 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-600/20 rounded-lg"><Target className="text-indigo-400 w-5 h-5" /></div>
                  Job Description
                </div>
                <button 
                  onClick={handleGenerateBlueprint}
                  disabled={!jdText || blueprintLoading}
                  className="text-xs font-black text-indigo-400 flex items-center gap-2 hover:bg-indigo-500/10 px-4 py-2 rounded-xl transition-all disabled:opacity-30"
                >
                  {blueprintLoading ? <Loader2 className="animate-spin" size={14} /> : <BookOpen size={14} />}
                  Generate Ideal Blueprint
                </button>
              </h3>
              <textarea
                className="w-full h-[300px] bg-[#020617]/50 border border-white/10 rounded-2xl p-6 text-slate-200 focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 outline-none transition-all placeholder:text-slate-600 resize-none font-mono text-sm leading-relaxed"
                placeholder="Paste the job description here..."
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
              />
              
              <div className="mt-8 flex items-center justify-end gap-4">
                <button
                  onClick={handleAnalyze}
                  disabled={loading || !jdText || files.length === 0}
                  className="w-full sm:w-auto sm:min-w-[280px] bg-primary-600 hover:bg-primary-500 disabled:bg-slate-800 py-4 px-8 rounded-2xl font-black text-lg shadow-2xl shadow-primary-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-3 active:scale-95 text-white"
                >
                  {loading ? (
                    <>
                      <Loader2 className="animate-spin" />
                      Analyzing with AI...
                    </>
                  ) : (
                    <>
                      Start Intelligent Match
                      <Sparkles size={18} />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        <AnimatePresence>
          {idealBlueprint && (
             <motion.div 
               initial={{ opacity: 0, height: 0 }}
               animate={{ opacity: 1, height: 'auto' }}
               exit={{ opacity: 0, height: 0 }}
               className="mt-12"
             >
                <AIPerfectMatch idealResume={idealBlueprint} />
             </motion.div>
          )}
        </AnimatePresence>
      </section>


      {/* Trust Section */}
      <section className="container mx-auto px-4 grid md:grid-cols-3 gap-8">
          <div className="premium-card p-10 bg-slate-900/40">
             <div className="bg-primary-600/20 w-14 h-14 rounded-2xl flex items-center justify-center mb-8"><Shield className="text-primary-400 w-8 h-8" /></div>
              <h4 className="font-bold text-2xl mb-4 tracking-tight text-white">Explainable RAG</h4>
              <p className="text-slate-400 text-sm leading-relaxed">Our system doesn't just score; it tells you WHY. It retrieves semantic context from resumes to back its decisions with data.</p>
          </div>
          <div className="premium-card p-10 bg-slate-900/40">
             <div className="bg-indigo-600/20 w-14 h-14 rounded-2xl flex items-center justify-center mb-8"><Zap className="text-indigo-400 w-8 h-8" /></div>
              <h4 className="font-bold text-2xl mb-4 tracking-tight text-white">Semantic Search</h4>
              <p className="text-slate-400 text-sm leading-relaxed">Uses high-dimensional embeddings to find skills that might be worded differently but share the same conceptual meaning.</p>
          </div>
          <div className="premium-card p-10 bg-slate-900/40">
             <div className="bg-blue-600/20 w-14 h-14 rounded-2xl flex items-center justify-center mb-8"><Target className="text-blue-400 w-8 h-8" /></div>
              <h4 className="font-bold text-2xl mb-4 tracking-tight text-white">Contextual Scoring</h4>
              <p className="text-slate-400 text-sm leading-relaxed">Weights are dynamically adjusted based on the job description requirements to prioritize the most critical competencies.</p>
          </div>
      </section>

      <footer className="container mx-auto px-4 pt-12 pb-8 border-t border-white/5 text-center">
         <div className="flex items-center justify-center gap-2 mb-6">
            <Cpu className="w-5 h-5 text-primary-500" />
            <span className="font-bold tracking-tight text-slate-300">HireSense AI</span>
         </div>
         <p className="text-slate-600 text-xs uppercase tracking-[0.3em]">Built for Modern Talent Acquisition</p>
         <div className="mt-8 text-slate-800 text-[10px]">© 2026 HireSense Systems Group. All rights reserved.</div>
      </footer>
    </div>
  );
};

export default Home;
