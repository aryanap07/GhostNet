import React, { useEffect, useState } from 'react';

interface TrustScoreProps {
  score: number;
  riskLevel: string;
  size?: number;
  strokeWidth?: number;
}

export const TrustScore: React.FC<TrustScoreProps> = ({
  score,
  riskLevel,
  size = 180,
  strokeWidth = 14
}) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  
  // Count-up effect on score change
  useEffect(() => {
    setAnimatedScore(0);
    const duration = 1200; // ms
    const startTime = performance.now();
    
    let animationFrameId: number;
    
    const animate = (currentTime: number) => {
      const elapsedTime = currentTime - startTime;
      const progress = Math.min(elapsedTime / duration, 1);
      
      // Easing function (easeOutQuad)
      const easeProgress = progress * (2 - progress);
      const currentVal = Math.round(easeProgress * score);
      
      setAnimatedScore(currentVal);
      
      if (progress < 1) {
        animationFrameId = requestAnimationFrame(animate);
      }
    };
    
    animationFrameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameId);
  }, [score]);

  // Determine indicator color based on score/risk
  let color = '#EF4444'; // default danger red
  let shadowGlow = 'rgba(239, 68, 68, 0.3)';

  if (score >= 80) {
    color = '#22C55E'; // Success green
    shadowGlow = 'rgba(34, 197, 94, 0.3)';
  } else if (score >= 60) {
    color = '#3B82F6'; // Info blue
    shadowGlow = 'rgba(59, 130, 246, 0.3)';
  } else if (score >= 40) {
    color = '#F59E0B'; // Warning yellow/orange
    shadowGlow = 'rgba(245, 158, 11, 0.3)';
  }

  // Calculate SVG circular parameters
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (animatedScore / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      {/* Outer shadow glow */}
      <div 
        className="absolute inset-2 rounded-full blur-xl transition-all duration-700 opacity-20"
        style={{ background: color }}
      />
      
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background Circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#18181b"
          strokeWidth={strokeWidth}
        />
        {/* Animated Progress Circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{
            transition: 'stroke-dashoffset 0.1s ease-out, stroke 0.5s ease'
          }}
        />
      </svg>
      
      {/* Inner Label Container */}
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span 
          className="text-4xl md:text-5xl font-bold font-mono tracking-tight transition-all"
          style={{ color: color, textShadow: `0 0 10px ${shadowGlow}` }}
        >
          {animatedScore}
        </span>
        <span className="text-xs uppercase tracking-widest text-slate-400 font-semibold mt-1">
          Trust Score
        </span>
        <span 
          className="text-xs font-semibold px-2 py-0.5 rounded-full mt-2 border"
          style={{
            borderColor: color + '40',
            backgroundColor: color + '15',
            color: color
          }}
        >
          {riskLevel}
        </span>
      </div>
    </div>
  );
};
export default TrustScore;
