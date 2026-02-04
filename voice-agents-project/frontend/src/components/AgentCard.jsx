/**
 * AgentCard Component - Displays an agent's information with selection capability
 */
import { Mic, BookOpen, Target, Globe } from 'lucide-react';

const categoryIcons = {
  'Communication Skills': Mic,
  'Career Preparation': Target,
  'Language Learning': BookOpen,
  'Grammar': BookOpen,
};

export function AgentCard({ agent, onSelect, isSelected }) {
  const IconComponent = categoryIcons[agent.category] || Globe;

  return (
    <button
      onClick={() => onSelect(agent)}
      className={`
        w-full text-left p-6 rounded-2xl transition-all duration-300 card-hover
        ${isSelected 
          ? 'bg-gradient-to-br from-primary-500/20 to-accent-500/20 border-2 border-primary-500/50' 
          : 'glass border border-white/5 hover:border-primary-500/30'
        }
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{agent.icon}</span>
          <div>
            <h3 className="font-display font-semibold text-lg text-white">
              {agent.name}
            </h3>
            <span className="text-xs text-primary-400 font-medium">
              {agent.category}
            </span>
          </div>
        </div>
        <span className={`
          px-2 py-1 text-xs rounded-full
          ${agent.language === 'English' 
            ? 'bg-emerald-500/20 text-emerald-400' 
            : 'bg-amber-500/20 text-amber-400'
          }
        `}>
          {agent.language}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-400 mb-4 line-clamp-2">
        {agent.description}
      </p>

      {/* Features */}
      <div className="flex flex-wrap gap-2">
        {agent.features.map((feature, index) => (
          <span
            key={index}
            className="px-2 py-1 text-xs rounded-lg bg-white/5 text-gray-300"
          >
            {feature}
          </span>
        ))}
      </div>

      {/* Selection indicator */}
      {isSelected && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center gap-2 text-primary-400">
            <div className="w-2 h-2 rounded-full bg-primary-400 animate-pulse" />
            <span className="text-sm font-medium">Selected</span>
          </div>
        </div>
      )}
    </button>
  );
}

export default AgentCard;
