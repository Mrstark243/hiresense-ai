import React from 'react';
import {
  Radar, RadarChart, PolarGrid, 
  PolarAngleAxis, ResponsiveContainer
} from 'recharts';

const SkillRadar = ({ categories }) => {
  // categories = [{ category: 'Technical', score: 85 }, ...]
  
  return (
    <div className="premium-card p-10 bg-slate-900/40 border-primary-500/10 h-[400px]">
      <h3 className="text-2xl font-black mb-8 text-white uppercase tracking-tight">
        Competency <span className="text-primary-400">Spectrum</span>
      </h3>
      
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={categories}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis 
            dataKey="category" 
            tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 'bold' }} 
          />
          <Radar
            name="Skills"
            dataKey="score"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.5}
            animationBegin={500}
            animationDuration={1500}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SkillRadar;
