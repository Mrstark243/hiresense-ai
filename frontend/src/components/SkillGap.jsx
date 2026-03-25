import React from 'react';
import { Check, X, Lightbulb, Star, AlertCircle, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';

const SkillGap = ({ strongSkills, missingSkills, suggestions, llmInsights }) => {
  const hasStrongMatches = llmInsights?.strong_matches?.length > 0;
  const hasCriticalGaps = llmInsights?.critical_gaps?.length > 0;
  const actionPlan = llmInsights?.action_plan?.length > 0 ? llmInsights.action_plan : suggestions;
  
  return (
    <div className="grid lg:grid-cols-2 gap-8 mt-12">
      {/* Strong Skills */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="premium-card p-10 bg-slate-900/40 border-green-500/10 relative overflow-hidden group"
      >
        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-20 transition-opacity">
           <Star size={80} className="text-green-500" />
        </div>
        <h3 className="text-2xl font-black mb-8 flex items-center gap-4 text-green-400">
          <div className="p-2 bg-green-500/20 rounded-xl"><Check className="w-6 h-6" /></div>
          Strong Matches
        </h3>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {hasStrongMatches ? (
            llmInsights.strong_matches.map((item, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="bg-green-500/10 p-5 rounded-3xl border border-green-500/20 shadow-lg relative"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="text-green-400 font-black text-xl">{item.skill}</div>
                  <div className="text-[10px] font-black uppercase px-2 py-1 bg-green-500/20 text-green-300 rounded-lg tracking-widest">{item.level || 'Intermediate'}</div>
                </div>
                <div className="text-green-100/80 text-sm leading-relaxed mb-3">{item.reason}</div>
                {item.evidence && (
                  <div className="text-xs bg-slate-900/50 p-2 rounded-xl text-green-200/50 italic border-l-2 border-green-500/30">
                    "{item.evidence}"
                  </div>
                )}
              </motion.div>
            ))
          ) : (
            <div className="flex flex-wrap gap-3">
              {strongSkills.map((skill, i) => (
                <span key={i} className="bg-green-500/10 text-green-400 px-5 py-2 rounded-2xl text-sm font-bold border border-green-500/20">{skill}</span>
              ))}
            </div>
          )}
        </div>
      </motion.div>

      {/* Missing Skills */}
      <motion.div 
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="premium-card p-10 bg-slate-900/40 border-red-500/10 relative overflow-hidden group"
      >
        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-20 transition-opacity">
           <AlertCircle size={80} className="text-red-500" />
        </div>
        <h3 className="text-2xl font-black mb-8 flex items-center gap-4 text-red-400">
          <div className="p-2 bg-red-500/20 rounded-xl"><X className="w-6 h-6" /></div>
          Critical Gaps
        </h3>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {hasCriticalGaps ? (
            llmInsights.critical_gaps.map((item, i) => {
              const type = item.classification || 'Explicit Gap';
              const colorClass = type.includes('Partial') ? 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20' 
                                : type.includes('Weak') ? 'text-orange-400 bg-orange-500/10 border-orange-500/20' 
                                : 'text-red-400 bg-red-500/10 border-red-500/20';
              const textPrm = type.includes('Partial') ? 'text-yellow-100/80' : type.includes('Weak') ? 'text-orange-100/80' : 'text-red-100/80';
              
              return (
                <motion.div 
                  key={i} 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className={`p-5 rounded-3xl border shadow-lg ${colorClass}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-black text-xl truncate">{item.skill}</div>
                    <div className="text-[9px] font-black uppercase px-2 py-1 bg-black/20 rounded-lg tracking-widest whitespace-nowrap">{type}</div>
                  </div>
                  <div className={`${textPrm} text-sm leading-relaxed`}>{item.explanation}</div>
                </motion.div>
              );
            })
          ) : (
            <div className="flex flex-wrap gap-3">
              {missingSkills.map((skill, i) => (
                <span key={i} className="bg-red-500/10 text-red-400 px-5 py-2 rounded-2xl text-sm font-bold border border-red-500/20">{skill}</span>
              ))}
            </div>
          )}
        </div>
      </motion.div>

      {/* Substitutable Skills & Inferred Skills */}
      {llmInsights?.substitutable_skills?.length > 0 && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2 premium-card p-10 bg-slate-800/40 border-blue-500/20 relative"
        >
          <h3 className="text-2xl font-black mb-6 text-blue-400 flex items-center gap-3">
            Substitutable Skills Identified
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            {llmInsights.substitutable_skills.map((sub, i) => (
              <div key={i} className="bg-blue-900/10 border border-blue-500/20 p-5 rounded-3xl relative overflow-hidden">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-slate-400 line-through text-sm font-bold">{sub.required}</span>
                  <span className="text-blue-400 font-black text-lg">→ {sub.candidate || sub.alternative}</span>
                  <span className="ml-auto text-xs bg-blue-500/20 text-blue-300 font-black uppercase tracking-widest px-2 py-1 rounded-md">{sub.transferability} Transfer</span>
                </div>
                <p className="text-blue-100/80 text-sm leading-relaxed pb-1"><span className="text-blue-300 font-bold block mb-1">Learning Curve:</span> {sub.learning_curve || sub.explanation}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {llmInsights?.inferred_skills?.length > 0 && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="lg:col-span-2 premium-card p-8 bg-slate-900 border-purple-500/20"
        >
          <h3 className="text-xl font-bold mb-4 text-purple-400">Inferred Hidden Strengths</h3>
          <div className="grid md:grid-cols-2 gap-4">
            {llmInsights.inferred_skills.map((item, i) => (
              <div key={i} className="bg-purple-500/10 border border-purple-500/20 p-4 rounded-2xl">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-purple-300 font-black text-lg">{item.skill}</span>
                  <span className="text-[10px] bg-purple-500/20 text-purple-200 px-2 py-1 rounded-md uppercase font-bold tracking-widest">Derived: {item.derived_from}</span>
                </div>
                <p className="text-purple-100/70 text-sm">{item.reason}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {llmInsights?.recruiter_insights?.length > 0 && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2 premium-card p-8 bg-slate-800/80 border-white/10"
        >
          <h3 className="text-xl font-black mb-4 text-white uppercase tracking-widest text-sm">Recruiter Insights</h3>
          <ul className="space-y-3">
            {llmInsights.recruiter_insights.map((insight, i) => (
              <li key={i} className="text-slate-300 text-lg border-l-4 border-primary-500 pl-4 py-1 italic">
                "{insight}"
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* Suggestions */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="lg:col-span-2 premium-card p-12 bg-gradient-to-br from-primary-900/10 via-transparent to-transparent border-primary-500/20"
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
          <h3 className="text-3xl font-black flex items-center gap-4 text-white uppercase tracking-tight">
            <div className="p-3 bg-primary-600 rounded-2xl shadow-xl shadow-primary-500/20"><Lightbulb className="w-8 h-8 text-white" /></div>
            AI Strategy <span className="text-primary-400">Roadmap</span>
          </h3>
          <div className="flex items-center gap-2 bg-primary-400/10 text-primary-400 px-4 py-2 rounded-full text-xs font-black uppercase border border-primary-400/20">
             <TrendingUp size={14} /> Optimization active
          </div>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8">
          {actionPlan.map((s, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className="p-6 rounded-3xl bg-white/5 border border-white/5 hover:border-primary-500/30 transition-all hover:bg-white/[0.08]"
            >
              {typeof s === 'string' ? (
                <div className="flex items-start gap-6">
                  <div className="bg-primary-600 text-white w-10 h-10 rounded-2xl flex items-center justify-center font-black flex-shrink-0 shadow-lg shadow-primary-500/20">{i+1}</div>
                  <p className="text-slate-200 text-base leading-relaxed font-medium">{s}</p>
                </div>
              ) : (
                <div className="flex flex-col gap-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="bg-primary-600 text-white w-8 h-8 rounded-xl flex items-center justify-center font-black flex-shrink-0 shadow-lg">{i+1}</div>
                      <h4 className="font-black text-lg text-white">{s.title}</h4>
                    </div>
                    <span className="text-[10px] uppercase font-black tracking-widest text-primary-400 bg-primary-500/10 px-2 py-1 rounded-lg">{s.type}</span>
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed">{s.description}</p>
                  <div className="bg-slate-900/50 p-3 rounded-xl border border-white/5 flex gap-3 mt-2">
                     <span className="text-primary-400 font-bold text-xs uppercase tracking-widest shrink-0">Impact</span>
                     <p className="text-slate-400 text-xs">{s.impact}</p>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default SkillGap;
