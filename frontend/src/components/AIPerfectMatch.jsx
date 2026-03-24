import React from 'react';
import { Sparkles, CheckCircle2, Target, GraduationCap, Briefcase } from 'lucide-react';
import { motion } from 'framer-motion';

const AIPerfectMatch = ({ idealResume }) => {
  if (!idealResume) return null;

  return (
    <div className="space-y-12 mt-12">
      {/* Header */}
      <div className="flex items-center gap-4">
         <div className="p-3 bg-primary-600 rounded-2xl shadow-xl shadow-primary-500/20">
            <Sparkles className="text-white w-8 h-8" />
         </div>
         <div>
            <h3 className="text-3xl font-black text-white tracking-tight">AI Generated <span className="text-primary-400">Ideal Resume</span></h3>
            <p className="text-slate-500 text-xs uppercase tracking-widest font-black">Blueprint for the Perfect Match</p>
         </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column: Summary & Skills */}
        <div className="lg:col-span-1 space-y-8">
           <motion.div 
             initial={{ opacity: 0, x: -20 }}
             animate={{ opacity: 1, x: 0 }}
             className="premium-card p-8 bg-slate-900/60 border-white/5"
           >
              <h4 className="text-lg font-bold mb-4 flex items-center gap-2 text-primary-400">
                <Target size={18} />
                Professional Summary
              </h4>
              <p className="text-slate-300 text-sm leading-relaxed italic">
                "{idealResume.summary}"
              </p>
           </motion.div>

           <motion.div 
             initial={{ opacity: 0, x: -20 }}
             animate={{ opacity: 1, x: 0 }}
             transition={{ delay: 0.1 }}
             className="premium-card p-8 bg-slate-900/60 border-white/5"
           >
              <h4 className="text-lg font-bold mb-6 text-white">Top Skills to Highlight</h4>
              <div className="flex flex-wrap gap-2">
                {idealResume.top_skills?.map((skill, idx) => (
                  <span key={idx} className="bg-primary-500/10 text-primary-400 px-3 py-1 rounded-full text-xs font-bold border border-primary-500/20 uppercase tracking-wider">
                    {skill}
                  </span>
                ))}
              </div>
           </motion.div>
        </div>

        {/* Right Column: Experience & Education */}
        <div className="lg:col-span-2 space-y-8">
           <motion.div 
             initial={{ opacity: 0, y: 20 }}
             animate={{ opacity: 1, y: 0 }}
             className="premium-card p-8 bg-slate-900/40 border-primary-500/10"
           >
              <h4 className="text-xl font-bold mb-8 flex items-center gap-3">
                 <div className="p-2 bg-primary-600/20 rounded-lg text-primary-400"><Briefcase size={20} /></div>
                 Critical Experience Bullets
              </h4>
              <ul className="space-y-6">
                {idealResume.experience_focus?.map((bullet, idx) => (
                  <li key={idx} className="flex gap-4">
                    <CheckCircle2 className="text-primary-500 shrink-0 mt-1" size={18} />
                    <p className="text-slate-300 leading-relaxed">{bullet}</p>
                  </li>
                ))}
              </ul>
           </motion.div>

           <motion.div 
             initial={{ opacity: 0, y: 20 }}
             animate={{ opacity: 1, y: 0 }}
             transition={{ delay: 0.2 }}
             className="premium-card p-8 bg-slate-900/80 border-indigo-500/10"
           >
              <h4 className="text-xl font-bold mb-4 flex items-center gap-3">
                 <div className="p-2 bg-indigo-600/20 rounded-lg text-indigo-400"><GraduationCap size={20} /></div>
                 Education Target
              </h4>
              <p className="text-slate-300 font-medium">
                {idealResume.education_target}
              </p>
           </motion.div>
        </div>
      </div>
    </div>
  );
};

export default AIPerfectMatch;
