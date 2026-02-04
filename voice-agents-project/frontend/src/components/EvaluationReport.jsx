/**
 * EvaluationReport Component - Displays the agent's evaluation report
 */
import { X, Star, TrendingUp, Award, BookOpen, Mic2, MessageSquare } from 'lucide-react';

// Score circle component
function ScoreCircle({ score, maxScore = 10, size = 80, label }) {
  const percentage = (score / maxScore) * 100;
  const circumference = 2 * Math.PI * 35;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  
  // Color based on score
  const getColor = () => {
    if (score >= 8) return '#10b981'; // green
    if (score >= 6) return '#0ea5e9'; // blue
    if (score >= 4) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  return (
    <div className="flex flex-col items-center">
      <div className="score-circle" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 80 80">
          <circle className="bg" cx="40" cy="40" r="35" />
          <circle 
            className="progress" 
            cx="40" 
            cy="40" 
            r="35"
            style={{
              stroke: getColor(),
              strokeDasharray: circumference,
              strokeDashoffset: strokeDashoffset,
            }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-white">{score}</span>
        </div>
      </div>
      {label && (
        <span className="mt-2 text-xs text-gray-400 text-center">{label}</span>
      )}
    </div>
  );
}

// Category icons mapping
const categoryIcons = {
  linguistic_agility: Mic2,
  structural_integrity: BookOpen,
  lexical_precision: MessageSquare,
  acoustic_clarity: TrendingUp,
  confidence: Star,
  star_method: Award,
  grammar: BookOpen,
  relevance: Star,
  clarity: MessageSquare,
  evidence: TrendingUp,
  parts_of_speech_accuracy: BookOpen,
  grammar_logic: TrendingUp,
  vocabulary_usage: MessageSquare,
};

// Feedback card component
function FeedbackCard({ title, score, feedback, icon: Icon }) {
  return (
    <div className="glass-light rounded-xl p-4">
      <div className="flex items-start gap-4">
        <div className="p-2 rounded-lg bg-primary-500/20">
          <Icon className="w-5 h-5 text-primary-400" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-white">{title}</h4>
            <div className="flex items-center gap-1">
              <span className="text-lg font-bold text-primary-400">{score}</span>
              <span className="text-xs text-gray-500">/10</span>
            </div>
          </div>
          <p className="text-sm text-gray-400">{feedback}</p>
        </div>
      </div>
    </div>
  );
}

// Vocabulary improvement item
function VocabularyImprovement({ original, improved, reason }) {
  return (
    <div className="glass-light rounded-lg p-3">
      <div className="flex items-center gap-2 mb-2">
        <span className="px-2 py-1 text-xs rounded bg-red-500/20 text-red-400 line-through">
          {original}
        </span>
        <span className="text-gray-500">→</span>
        <span className="px-2 py-1 text-xs rounded bg-emerald-500/20 text-emerald-400">
          {improved}
        </span>
      </div>
      <p className="text-xs text-gray-500">{reason}</p>
    </div>
  );
}

export function EvaluationReport({ report, onClose }) {
  if (!report) return null;

  // Extract overall score and summary
  const overall = report.overall || {};
  const vocabularyImprovements = report.vocabulary_improvements || [];

  // Get all score categories (excluding 'overall' and 'vocabulary_improvements')
  const scoreCategories = Object.entries(report).filter(
    ([key]) => key !== 'overall' && key !== 'vocabulary_improvements'
  );

  // Calculate average score
  const scores = scoreCategories.map(([, value]) => value.score);
  const averageScore = scores.length > 0 
    ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length * 10) / 10
    : overall.score || 0;

  // Format category title
  const formatTitle = (key) => {
    return key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm">
      <div className="w-full max-w-2xl max-h-[90vh] glass rounded-3xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500">
              <Award className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="font-display font-bold text-xl text-white">
                Session Report
              </h2>
              <p className="text-sm text-gray-400">Your performance evaluation</p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-white/10 transition-colors"
          >
            <X className="w-6 h-6 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Overall Score */}
          <div className="flex items-center justify-center gap-8 p-6 glass-light rounded-2xl">
            <ScoreCircle 
              score={overall.score || averageScore} 
              size={100}
              label="Overall Score"
            />
            <div className="flex-1">
              <h3 className="font-display font-semibold text-lg text-white mb-2">
                Summary
              </h3>
              <p className="text-sm text-gray-400">
                {overall.summary || 'Great job completing this session!'}
              </p>
            </div>
          </div>

          {/* Score Breakdown */}
          {scoreCategories.length > 0 && (
            <div>
              <h3 className="font-display font-semibold text-lg text-white mb-4">
                Detailed Feedback
              </h3>
              <div className="space-y-3">
                {scoreCategories.map(([key, value]) => {
                  const Icon = categoryIcons[key] || Star;
                  return (
                    <FeedbackCard
                      key={key}
                      title={formatTitle(key)}
                      score={value.score}
                      feedback={value.feedback}
                      icon={Icon}
                    />
                  );
                })}
              </div>
            </div>
          )}

          {/* Vocabulary Improvements */}
          {vocabularyImprovements.length > 0 && (
            <div>
              <h3 className="font-display font-semibold text-lg text-white mb-4">
                Vocabulary Improvements
              </h3>
              <div className="space-y-2">
                {vocabularyImprovements.map((improvement, index) => (
                  <VocabularyImprovement
                    key={index}
                    original={improvement.original}
                    improved={improvement.improved}
                    reason={improvement.reason}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-white/10">
          <button
            onClick={onClose}
            className="w-full btn-primary py-3"
          >
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
}

export default EvaluationReport;
