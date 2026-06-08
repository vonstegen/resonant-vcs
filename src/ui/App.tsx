import { useState, useEffect, useCallback } from 'react';
import { 
  GitBranch, GitCommit, Plus, File, FolderOpen, Clock, 
  Zap, Eye, Upload, Trash2, Check, X, ChevronRight,
  Sparkles, MessageSquare, BookOpen
} from 'lucide-react';
import { api, Version, Status, Change } from './api';

// Icons as simple SVG components
const Icons = {
  GitBranch: () => <GitBranch size={16} />,
  GitCommit: () => <GitCommit size={16} />,
  Plus: () => <Plus size={16} />,
  File: () => <File size={16} />,
  FolderOpen: () => <FolderOpen size={16} />,
  Clock: () => <Clock size={16} />,
  Zap: () => <Zap size={16} />,
  Eye: () => <Eye size={16} />,
  Upload: () => <Upload size={16} />,
  Trash: () => <Trash2 size={16} />,
  Check: () => <Check size={16} />,
  X: () => <X size={16} />,
  Chevron: () => <ChevronRight size={16} />,
  Sparkles: () => <Sparkles size={16} />,
  Message: () => <MessageSquare size={16} />,
  Book: () => <BookOpen size={16} />,
};

type Mode = 'simple' | 'advanced';

function App() {
  const [mode, setMode] = useState<Mode>('simple');
  const [repoPath, setRepoPath] = useState('/tmp/avcs-test');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<Status | null>(null);
  const [versions, setVersions] = useState<Version[]>([]);
  const [changes, setChanges] = useState<Change[]>([]);
  const [commitMessage, setCommitMessage] = useState('');
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [aiThinking, setAiThinking] = useState(false);
  const [story, setStory] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Initialize API with repo path
  useEffect(() => {
    api.setRepoPath(repoPath);
    loadData();
  }, [repoPath]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statusData, logData, diffData] = await Promise.all([
        api.getStatus().catch(() => null),
        api.getLog(20).catch(() => []),
        api.getDiff().catch(() => ({ changes: [] })),
      ]);
      setStatus(statusData);
      setVersions(logData);
      setChanges(diffData.changes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    }
    setLoading(false);
  };

  const handleSuggest = async () => {
    setAiThinking(true);
    try {
      const data = await api.suggestCommit();
      setSuggestion(data.suggestion);
    } catch {
      // Silently fail
    }
    setAiThinking(false);
  };

  const handleExplain = async () => {
    setAiThinking(true);
    try {
      const data = await api.explainChanges();
      alert(data.explanation);
    } catch (err) {
      alert('Could not explain changes. Make sure files are staged.');
    }
    setAiThinking(false);
  };

  const handleStory = async () => {
    setAiThinking(true);
    try {
      const data = await api.tellStory(10);
      setStory(data.story);
    } catch (err) {
      alert('Could not generate story. Make sure there are commits.');
    }
    setAiThinking(false);
  };

  const handleCommit = async () => {
    if (!commitMessage.trim()) return;
    setLoading(true);
    try {
      await api.commit(commitMessage);
      setCommitMessage('');
      setSuggestion(null);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Commit failed');
    }
    setLoading(false);
  };

  const handleStageAll = async () => {
    setLoading(true);
    try {
      await api.addFiles(['.']);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Stage failed');
    }
    setLoading(false);
  };

  const handleInit = async () => {
    setLoading(true);
    try {
      await api.init(repoPath);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Init failed');
    }
    setLoading(false);
  };

  return (
    <div className={`app ${mode === 'simple' ? 'simple-mode' : ''}`}>
      {/* Header */}
      <header className="header">
        <div className="logo">
          <div className="logo-icon">
            <Icons.GitCommit />
          </div>
          <span>AugmentedVCS</span>
        </div>
        
        <div className="mode-toggle">
          <button 
            className={`mode-btn ${mode === 'simple' ? 'active' : ''}`}
            onClick={() => setMode('simple')}
          >
            Simple
          </button>
          <button 
            className={`mode-btn ${mode === 'advanced' ? 'active' : ''}`}
            onClick={() => setMode('advanced')}
          >
            Advanced
          </button>
        </div>

        <div className="branch-badge">
          <Icons.GitBranch />
          {status?.branch || 'main'}
        </div>
      </header>

      <div className="main-content">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="card">
            <div className="card-header">
              <span className="card-title">Files</span>
              <button className="btn btn-secondary" onClick={handleStageAll} disabled={loading}>
                <Icons.Plus /> Add All
              </button>
            </div>
            
            <div className="file-list">
              {status?.initialized && (
                <>
                  {changes.filter(c => c.type === 'modified').map(c => (
                    <div key={c.path} className="file-item">
                      <span className="file-icon"><Icons.File /></span>
                      <span className="file-name">{c.path}</span>
                      <span className="file-status modified">Changed</span>
                    </div>
                  ))}
                  {changes.filter(c => c.type === 'added').map(c => (
                    <div key={c.path} className="file-item">
                      <span className="file-icon"><Icons.File /></span>
                      <span className="file-name">{c.path}</span>
                      <span className="file-status new">New</span>
                    </div>
                  ))}
                  {(!changes.length) && (
                    <div className="empty-state">
                      <p className="empty-state-text">No changes to track</p>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {mode === 'advanced' && (
            <div className="card">
              <div className="card-header">
                <span className="card-title">Branches</span>
              </div>
              <div className="file-list">
                <div className="file-item">
                  <Icons.GitBranch />
                  <span className="file-name">main</span>
                </div>
                <div className="file-item">
                  <Icons.GitBranch />
                  <span className="file-name">feature-shopping</span>
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Main Content */}
        <main className="content">
          {error && (
            <div className="card" style={{ borderColor: 'var(--accent-red)', marginBottom: 16 }}>
              <p style={{ color: 'var(--accent-red)' }}>{error}</p>
            </div>
          )}

          {/* Status Panel */}
          <div className="status-panel">
            <div className="status-item">
              <div className="status-value">{versions.length}</div>
              <div className="status-label">Versions</div>
            </div>
            <div className="status-item">
              <div className="status-value">{changes.length}</div>
              <div className="status-label">Changes</div>
            </div>
            <div className="status-item">
              <div className="status-value">{status?.staged.length || 0}</div>
              <div className="status-label">Staged</div>
            </div>
          </div>

          {/* Quick Actions */}
          {mode === 'simple' && (
            <div className="card" style={{ marginBottom: 24 }}>
              <h3 style={{ marginBottom: 16 }}>Quick Actions</h3>
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                <button className="btn btn-primary" onClick={handleStageAll}>
                  <Icons.Upload /> Save Current Version
                </button>
                <button className="btn btn-secondary" onClick={handleExplain} disabled={aiThinking}>
                  <Icons.Eye /> Explain Changes
                </button>
                <button className="btn btn-secondary" onClick={handleStory} disabled={aiThinking}>
                  <Icons.Book /> Tell Me the Story
                </button>
              </div>
            </div>
          )}

          {/* Commit Form */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">
                {mode === 'simple' ? 'Save Your Changes' : 'Create Commit'}
              </span>
              <button 
                className="btn btn-secondary" 
                onClick={handleSuggest}
                disabled={aiThinking || !changes.length}
              >
                {aiThinking ? (
                  <><div className="spinner" /> Thinking...</>
                ) : (
                  <><Icons.Sparkles /> Suggest Message</>
                )}
              </button>
            </div>

            {suggestion && (
              <div className="commit-suggestion" onClick={() => setCommitMessage(suggestion)}>
                <div className="suggestion-label">💡 Suggested:</div>
                <div>{suggestion}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>
                  Click to use this message
                </div>
              </div>
            )}

            <div className="commit-form">
              <textarea
                className="commit-input"
                placeholder={
                  mode === 'simple' 
                    ? 'Describe what you changed (e.g., "Updated my shopping list")'
                    : 'Enter commit message...'
                }
                value={commitMessage}
                onChange={(e) => setCommitMessage(e.target.value)}
              />
              <button 
                className="btn btn-primary" 
                onClick={handleCommit}
                disabled={loading || !commitMessage.trim()}
              >
                {loading ? (
                  <><div className="spinner" /> Saving...</>
                ) : (
                  <><Icons.Check /> Save Version</>
                )}
              </button>
            </div>
          </div>

          {/* Timeline */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">
                {mode === 'simple' ? 'Version History' : 'Commit Log'}
              </span>
            </div>

            {versions.length > 0 ? (
              <div className="timeline">
                {versions.map((v, i) => (
                  <div key={v.id} className="timeline-item">
                    <div className="timeline-dot" />
                    <div className="timeline-content">
                      <div className="timeline-header">
                        <span className="timeline-id">{v.id.slice(0, 8)}</span>
                        <span className="timeline-date">
                          {new Date(v.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="timeline-message">{v.message}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon"><Icons.Clock /></div>
                <div className="empty-state-title">No versions yet</div>
                <div className="empty-state-text">
                  {mode === 'simple' 
                    ? 'Save your first version to start tracking changes'
                    : 'Create your first commit to see the history'
                  }
                </div>
              </div>
            )}
          </div>

          {/* Story Mode */}
          {story && (
            <div className="card">
              <div className="card-header">
                <span className="card-title">📖 Your Project Story</span>
                <button className="btn btn-secondary" onClick={() => setStory(null)}>
                  <Icons.X /> Close
                </button>
              </div>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                {story}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
