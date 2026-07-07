import React from 'react';

interface GhostCharacterProps {
  state?: 'idle' | 'scanning' | 'safe' | 'warning' | 'danger';
  size?: number;
}

export const GhostCharacter: React.FC<GhostCharacterProps> = ({ 
  state = 'idle', 
  size = 120 
}) => {
  // Determine glow colors and animations based on state
  let glowColor = 'rgba(139, 92, 246, 0.4)'; // Default purple glow
  let bodyColor = '#F8FAFC'; // Soft white
  let eyeColor = '#0F172A'; // Deep slate
  
  if (state === 'scanning') {
    glowColor = 'rgba(59, 130, 246, 0.6)'; // Blue scanning pulse
  } else if (state === 'safe') {
    glowColor = 'rgba(34, 197, 94, 0.5)'; // Green success glow
  } else if (state === 'warning') {
    glowColor = 'rgba(245, 158, 11, 0.5)'; // Orange warning glow
  } else if (state === 'danger') {
    glowColor = 'rgba(239, 68, 68, 0.6)'; // Red danger glow
  }

  // Define eyes and mouth shapes based on state
  const renderFace = () => {
    switch (state) {
      case 'scanning':
        return (
          <>
            {/* Alert/Inspecting scanning eyes */}
            <circle cx="42" cy="46" r="4.5" fill={eyeColor} />
            <circle cx="58" cy="46" r="4.5" fill={eyeColor} />
            {/* Scanner beam effect lines on eyes */}
            <line x1="38" y1="46" x2="46" y2="46" stroke="#3B82F6" strokeWidth="1.5" strokeLinecap="round" />
            <line x1="54" y1="46" x2="62" y2="46" stroke="#3B82F6" strokeWidth="1.5" strokeLinecap="round" />
            {/* Small serious mouth */}
            <path d="M 47 54 Q 50 52 53 54" stroke={eyeColor} strokeWidth="2.5" strokeLinecap="round" fill="none" />
          </>
        );
      case 'safe':
        return (
          <>
            {/* Happy eyes */}
            <path d="M 38 48 Q 42 43 46 48" stroke={eyeColor} strokeWidth="3" strokeLinecap="round" fill="none" />
            <path d="M 54 48 Q 58 43 62 48" stroke={eyeColor} strokeWidth="3" strokeLinecap="round" fill="none" />
            {/* Happy open mouth */}
            <path d="M 46 54 Q 50 58 54 54" stroke={eyeColor} strokeWidth="2.5" strokeLinecap="round" fill="none" />
          </>
        );
      case 'warning':
      case 'danger':
        return (
          <>
            {/* Worried tilted eyes */}
            <path d="M 38 44 L 46 47" stroke={eyeColor} strokeWidth="3" strokeLinecap="round" />
            <path d="M 62 44 L 54 47" stroke={eyeColor} strokeWidth="3" strokeLinecap="round" />
            <circle cx="42" cy="48" r="4" fill={eyeColor} />
            <circle cx="58" cy="48" r="4" fill={eyeColor} />
            {/* Worried mouth */}
            <path d="M 46 56 Q 50 52 54 56" stroke={eyeColor} strokeWidth="2.5" strokeLinecap="round" fill="none" />
          </>
        );
      case 'idle':
      default:
        return (
          <>
            {/* Friendly normal eyes */}
            <circle cx="40" cy="45" r="4" fill={eyeColor} />
            <circle cx="60" cy="45" r="4" fill={eyeColor} />
            {/* Soft smile */}
            <path d="M 46 53 Q 50 56 54 53" stroke={eyeColor} strokeWidth="2.5" strokeLinecap="round" fill="none" />
          </>
        );
    }
  };

  return (
    <div className="relative flex items-center justify-center select-none" style={{ width: size, height: size }}>
      {/* Background glow circle */}
      <div 
        className="absolute inset-0 rounded-full blur-xl transition-all duration-700 opacity-60"
        style={{ 
          background: glowColor,
          transform: state === 'scanning' ? 'scale(1.15)' : 'scale(1)'
        }}
      />
      
      {/* Floating Ghost SVG */}
      <svg 
        viewBox="0 0 100 100" 
        className={`w-full h-full relative z-10 transition-all duration-500 ${state === 'scanning' ? 'animate-pulse' : 'animate-float'}`}
      >
        <defs>
          <filter id="ghost-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Ghost Body */}
        <path 
          d="M 50 15 
             C 25 15, 20 40, 20 60 
             C 20 75, 25 85, 30 85 
             C 35 85, 37 77, 43 77 
             C 48 77, 50 85, 55 85 
             C 60 85, 62 77, 68 77 
             C 73 77, 75 85, 80 85 
             C 85 85, 90 75, 90 60 
             C 90 40, 85 15, 50 15 Z" 
          fill={bodyColor}
          filter="url(#ghost-glow)"
          style={{ transition: 'fill 0.5s ease' }}
        />

        {/* Interactive Face Details */}
        {renderFace()}

        {/* Cute blush cheeks (only on safe/idle) */}
        {(state === 'idle' || state === 'safe') && (
          <>
            <ellipse cx="34" cy="48" rx="3" ry="1.5" fill="rgba(236, 72, 153, 0.4)" />
            <ellipse cx="66" cy="48" rx="3" ry="1.5" fill="rgba(236, 72, 153, 0.4)" />
          </>
        )}

        {/* Small floating hands */}
        <path 
          d="M 16 54 C 12 54, 8 50, 12 44 C 14 42, 17 45, 18 48" 
          fill="none" 
          stroke={bodyColor} 
          strokeWidth="3.5" 
          strokeLinecap="round" 
        />
        <path 
          d="M 84 54 C 88 54, 92 50, 88 44 C 86 42, 83 45, 82 48" 
          fill="none" 
          stroke={bodyColor} 
          strokeWidth="3.5" 
          strokeLinecap="round" 
        />
      </svg>
    </div>
  );
};
export default GhostCharacter;
