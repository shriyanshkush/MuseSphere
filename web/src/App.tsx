import { useState } from 'react'

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <div className="min-h-screen relative overflow-hidden bg-background text-foreground">
      {/* Background gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] opacity-30 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/30 to-purple-500/30 blur-[100px] rounded-full mix-blend-screen" />
      </div>

      {/* Navigation */}
      <nav className="relative z-50 flex items-center justify-between px-6 py-4 max-w-7xl mx-auto animate-fade-in-up">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
            <span className="text-white font-bold text-xl leading-none font-display">M</span>
          </div>
          <span className="font-display font-bold text-xl tracking-tight">MuseSphere</span>
        </div>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
          <a href="#exhibitions" className="hover:text-foreground transition-colors">Exhibitions</a>
          <a href="#events" className="hover:text-foreground transition-colors">Events</a>
          <a href="#ai" className="hover:text-foreground transition-colors">AI Assistant</a>
        </div>

        <div className="hidden md:flex items-center gap-4">
          <button className="text-sm font-medium px-4 py-2 hover:bg-secondary rounded-full transition-colors">
            Log in
          </button>
          <button className="text-sm font-medium px-5 py-2 bg-primary text-primary-foreground rounded-full hover:opacity-90 transition-opacity shadow-lg shadow-primary/25">
            Book Tickets
          </button>
        </div>

        <button 
          className="md:hidden p-2"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-32 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/20 bg-primary/10 text-primary text-sm font-medium mb-8 animate-fade-in-up" style={{animationDelay: '0.1s'}}>
          <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse"></span>
          Now featuring Gemini AI 1.5 Flash
        </div>
        
        <h1 className="text-5xl md:text-7xl font-display font-bold tracking-tight mb-8 animate-fade-in-up" style={{animationDelay: '0.2s'}}>
          The future of <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-400">
            museum exploration.
          </span>
        </h1>
        
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-12 animate-fade-in-up" style={{animationDelay: '0.3s'}}>
          Experience art and history like never before with our intelligent RAG assistant, dynamic digital QR ticketing, and personalized recommendations.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up" style={{animationDelay: '0.4s'}}>
          <button className="w-full sm:w-auto px-8 py-4 bg-foreground text-background font-medium rounded-full hover:scale-105 transition-transform shadow-xl">
            Explore Exhibitions
          </button>
          <button className="w-full sm:w-auto px-8 py-4 glass-panel font-medium rounded-full hover:bg-white/80 dark:hover:bg-black/60 transition-colors">
            Chat with AI Guide
          </button>
        </div>

        {/* Dashboard Preview Mockup */}
        <div className="mt-24 relative mx-auto max-w-5xl animate-fade-in-up" style={{animationDelay: '0.6s'}}>
          <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent z-20 pointer-events-none" />
          <div className="glass-panel rounded-2xl p-2 md:p-4 border border-border/50 shadow-2xl relative z-10 transform perspective-1000 rotateX-12 scale-95 hover:rotate-0 hover:scale-100 transition-all duration-700 ease-out">
            <div className="bg-card rounded-xl overflow-hidden border border-border flex flex-col md:flex-row">
              {/* Sidebar */}
              <div className="hidden md:block w-64 border-r border-border p-6 space-y-6">
                <div className="w-24 h-4 bg-secondary rounded-full animate-pulse" />
                <div className="space-y-3">
                  <div className="w-full h-8 bg-secondary rounded-md" />
                  <div className="w-3/4 h-8 bg-secondary/50 rounded-md" />
                  <div className="w-4/5 h-8 bg-secondary/50 rounded-md" />
                </div>
              </div>
              {/* Main Content */}
              <div className="flex-1 p-6 space-y-8">
                <div className="flex justify-between items-center">
                  <div className="w-48 h-8 bg-secondary rounded-lg animate-pulse" />
                  <div className="w-10 h-10 bg-primary/20 rounded-full" />
                </div>
                {/* Tickets Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="h-40 rounded-xl border border-border bg-gradient-to-br from-card to-secondary/30 p-4 flex flex-col justify-between">
                    <div className="w-16 h-16 bg-white rounded shadow-sm border border-border self-end" />
                    <div className="w-32 h-4 bg-foreground/20 rounded" />
                  </div>
                  <div className="h-40 rounded-xl border border-border bg-card p-4 flex flex-col justify-end">
                     <div className="w-24 h-4 bg-muted-foreground/20 rounded mb-2" />
                     <div className="w-40 h-4 bg-muted-foreground/20 rounded" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
