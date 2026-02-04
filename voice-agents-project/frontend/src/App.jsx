/**
 * App Component - Main application with agent selection and voice interface
 */
import { useState, useEffect } from 'react';
import { Mic, Sparkles, Zap, Globe2, ChevronRight, Loader2 } from 'lucide-react';
import { AgentCard, VoiceInterface } from './components';
import { fetchAgents } from './utils/api';

function App() {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [isVoiceInterfaceOpen, setIsVoiceInterfaceOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeCategory, setActiveCategory] = useState('All');

  // Fetch agents on mount
  useEffect(() => {
    const loadAgents = async () => {
      try {
        const data = await fetchAgents();
        setAgents(data);
      } catch (err) {
        setError('Failed to load agents. Please check if the server is running.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadAgents();
  }, []);

  // Get unique categories
  const categories = ['All', ...new Set(agents.map(a => a.category))];

  // Filter agents by category
  const filteredAgents = activeCategory === 'All' 
    ? agents 
    : agents.filter(a => a.category === activeCategory);

  // Handle agent selection
  const handleSelectAgent = (agent) => {
    setSelectedAgent(agent);
  };

  // Start session with selected agent
  const handleStartSession = () => {
    if (selectedAgent) {
      setIsVoiceInterfaceOpen(true);
    }
  };

  // Close voice interface
  const handleCloseVoiceInterface = () => {
    setIsVoiceInterfaceOpen(false);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Animated background */}
      <div className="animated-bg" />

      {/* Header */}
      <header className="sticky top-0 z-40 glass border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500">
                <Mic className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="font-display font-bold text-xl">Voice Agents</h1>
                <p className="text-xs text-gray-500">AI-Powered Learning & Practice</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-2 text-sm text-gray-400">
                <Zap className="w-4 h-4 text-primary-400" />
                <span>Powered by Google ADK</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Hero section */}
        <section className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-light mb-6">
            <Sparkles className="w-4 h-4 text-primary-400" />
            <span className="text-sm text-gray-300">Real-time Voice AI Agents</span>
          </div>
          
          <h2 className="font-display font-bold text-4xl md:text-5xl lg:text-6xl mb-6">
            Practice & Learn with
            <span className="text-gradient block mt-2">AI Voice Agents</span>
          </h2>
          
          <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-8">
            Engage in real-time voice conversations with specialized AI agents. 
            Practice interviews, debates, grammar, and more with instant feedback.
          </p>

          {selectedAgent && (
            <button
              onClick={handleStartSession}
              className="btn-primary inline-flex items-center gap-3 px-8 py-4 text-lg"
            >
              <Mic className="w-5 h-5" />
              Start Session with {selectedAgent.name}
              <ChevronRight className="w-5 h-5" />
            </button>
          )}
        </section>

        {/* Category filters */}
        <section className="mb-8">
          <div className="flex flex-wrap gap-2 justify-center">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setActiveCategory(category)}
                className={`
                  px-4 py-2 rounded-full text-sm font-medium transition-all
                  ${activeCategory === category
                    ? 'bg-primary-500 text-white'
                    : 'glass-light text-gray-400 hover:text-white hover:bg-white/10'
                  }
                `}
              >
                {category}
              </button>
            ))}
          </div>
        </section>

        {/* Loading state */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 text-primary-400 animate-spin mb-4" />
            <p className="text-gray-400">Loading agents...</p>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="max-w-md mx-auto p-6 rounded-2xl bg-red-500/10 border border-red-500/30 text-center">
            <Globe2 className="w-10 h-10 text-red-400 mx-auto mb-4" />
            <p className="text-red-400 mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="btn-secondary"
            >
              Retry
            </button>
          </div>
        )}

        {/* Agents grid */}
        {!isLoading && !error && (
          <section>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredAgents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  onSelect={handleSelectAgent}
                  isSelected={selectedAgent?.id === agent.id}
                />
              ))}
            </div>

            {filteredAgents.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500">No agents found in this category.</p>
              </div>
            )}
          </section>
        )}

        {/* Features section */}
        <section className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass-light rounded-2xl p-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center mx-auto mb-4">
              <Mic className="w-6 h-6 text-primary-400" />
            </div>
            <h3 className="font-display font-semibold text-lg mb-2">Real-time Voice</h3>
            <p className="text-sm text-gray-400">
              Natural voice conversations with ultra-low latency streaming
            </p>
          </div>
          
          <div className="glass-light rounded-2xl p-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-accent-500/20 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-6 h-6 text-accent-400" />
            </div>
            <h3 className="font-display font-semibold text-lg mb-2">AI Evaluation</h3>
            <p className="text-sm text-gray-400">
              Get detailed feedback and scores on your performance
            </p>
          </div>
          
          <div className="glass-light rounded-2xl p-6 text-center">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center mx-auto mb-4">
              <Globe2 className="w-6 h-6 text-emerald-400" />
            </div>
            <h3 className="font-display font-semibold text-lg mb-2">Multi-language</h3>
            <p className="text-sm text-gray-400">
              Support for English, Hindi, and Hinglish conversations
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 mt-20">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-500">
              Built with Google ADK, FastAPI & React
            </p>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span>Voice Agents Demo</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Voice Interface Modal */}
      {isVoiceInterfaceOpen && selectedAgent && (
        <VoiceInterface
          agent={selectedAgent}
          onClose={handleCloseVoiceInterface}
        />
      )}
    </div>
  );
}

export default App;
