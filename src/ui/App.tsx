import { useState, useEffect } from 'react';
import { 
  Home, Folder as FolderIcon, FolderOpen as FolderOpenIcon, 
  File, FileText, Save, ChevronRight, RefreshCw, Upload, 
  Search, Settings, Check, FolderInput
} from 'lucide-react';
import { api, Version, Change, FileItem } from './api';

// Types

function App() {
  const [repoPath, setRepoPath] = useState('/mnt/c/Users/andre/Documents/Developer/TEST-Repo-v01');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<'explorer' | 'changes'>('explorer');
  const [commits, setCommits] = useState<Version[]>([]);
  const [loading, setLoading] = useState(false);
  const [changes, setChanges] = useState<Change[]>([]);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [commitMessage, setCommitMessage] = useState('');
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [aiThinking, setAiThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPath, setCurrentPath] = useState('/');
  const [showPathInput, setShowPathInput] = useState(false);
  const [tempPath, setTempPath] = useState('');

  // Load data when repo changes
  useEffect(() => {
    if (repoPath) {
      api.setRepoPath(repoPath);
      loadAll();
    }
  }, [repoPath]);

  const loadAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [logData, diffData, fileData] = await Promise.all([
        api.getLog(20).catch(() => []),
        api.getDiff().catch(() => ({ changes: [] })),
        api.getFiles().catch(() => []),
      ]);
      setChanges(diffData.changes);
      setCommits(logData);
      setFiles(fileData);
    } catch (err) {
      setError('Could not load data');
    }
    setLoading(false);
  };

  const handleAddAll = async () => {
    setLoading(true);
    try {
      await api.addFiles(['.']);
      await loadAll();
    } catch (err) {
      setError('Could not stage files');
    }
    setLoading(false);
  };

  const handleCommit = async () => {
    if (!commitMessage.trim()) return;
    setLoading(true);
    try {
      await api.commit(commitMessage);
      setCommitMessage('');
      setSuggestion(null);
      await loadAll();
    } catch (err) {
      setError('Could not save');
    }
    setLoading(false);
  };

  const handleSuggest = async () => {
    setAiThinking(true);
    try {
      const data = await api.suggestCommit();
      setSuggestion(data.suggestion);
    } catch {}
    setAiThinking(false);
  };

  const handleMultiSelect = (path: string, event: React.MouseEvent) => {
    if (event.ctrlKey || event.metaKey) {
      const newSelected = new Set(selectedItems);
      if (newSelected.has(path)) {
        newSelected.delete(path);
      } else {
        newSelected.add(path);
      }
      setSelectedItems(newSelected);
    } else {
      const newSelected = new Set<string>();
      newSelected.add(path);
      setSelectedItems(newSelected);
      setSelectedFile(path);
    }
  };

  const getFileIcon = (name: string, type: 'file' | 'folder', expanded?: boolean) => {
    if (type === 'folder') {
      return expanded ? <FolderOpenIcon size={18} /> : <FolderIcon size={18} />;
    }
    const ext = name.split('.').pop()?.toLowerCase();
    if (['md', 'txt', 'doc', 'docx', 'rtf'].includes(ext || '')) {
      return <FileText size={18} />;
    }
    return <File size={18} />;
  };

  const getChangeIcon = (type: string) => {
    switch (type) {
      case 'added': return <span style={{ color: '#22c55e', fontWeight: 'bold' }}>+</span>;
      case 'modified': return <span style={{ color: '#eab308', fontWeight: 'bold' }}>~</span>;
      case 'deleted': return <span style={{ color: '#ef4444', fontWeight: 'bold' }}>-</span>;
      default: return null;
    }
  };

  return (
    <div className="explorer-app">
      {/* ===== TITLE BAR ===== */}
      <header className="title-bar">
        <div className="title-left">
          <div className="app-icon">AV</div>
          <span className="app-title">AugmentedVCS</span>
        </div>
        <div className="title-center">
          <button className="folder-btn" onClick={() => { setTempPath(repoPath); setShowPathInput(true); }} title="Change Repository">
            <FolderInput size={14} />
          </button>
          <div className="path-bar">
            <Home size={14} />
            <span>{repoPath.split('/').pop()}</span>
          </div>
        </div>
        <div className="title-right">
          <button className="icon-btn" title="Settings">
            <Settings size={18} />
          </button>
        </div>
      </header>

      {/* ===== MENU BAR ===== */}
      <nav className="menu-bar">
        <div className="menu-group">
          <button className={`menu-btn ${viewMode === 'explorer' ? 'active' : ''}`} onClick={() => setViewMode('explorer')}>
            📁 Explorer
          </button>
          <button className={`menu-btn ${viewMode === 'changes' ? 'active' : ''}`} onClick={() => setViewMode('changes')}>
            🔄 Changes
          </button>
        </div>
        <div className="menu-group">
          <button className="menu-btn" onClick={handleAddAll}>
            <Upload size={14} /> Add All
          </button>
          <button className="menu-btn primary" onClick={handleCommit} disabled={!commitMessage.trim()}>
            <Save size={14} /> Save
          </button>
        </div>
      </nav>

      {/* ===== MAIN CONTENT ===== */}
      <div className="main-content">
        {/* ----- LEFT SIDEBAR: Folders ----- */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <span>Folders</span>
            <button className="icon-btn-sm" title="Refresh" onClick={loadAll}>
              <RefreshCw size={14} />
            </button>
          </div>
          <div className="folder-list">
            {/* My Project - root */}
            <div className="folder-item" onClick={() => setCurrentPath('/')}>
              <Home size={16} />
              <span>My Project</span>
            </div>
            {/* Show folders from repository */}
            {files.filter(f => f.type === 'folder').map(folder => (
              <div 
                key={folder.path} 
                className="folder-item"
                onClick={() => setCurrentPath(folder.path)}
              >
                <FolderIcon size={16} />
                <span>{folder.name}</span>
              </div>
            ))}
            {files.filter(f => f.type === 'folder').length === 0 && (
              <div className="empty-text">No folders</div>
            )}
          </div>
          
          <div className="sidebar-header">
            <span>Recent Saves</span>
          </div>
          <div className="commit-list">
            {commits.slice(0, 5).map(commit => (
              <div key={commit.id} className="commit-preview" title={commit.message}>
                <span className="commit-hash">{commit.id.slice(0, 6)}</span>
                <span className="commit-msg">{commit.message}</span>
              </div>
            ))}
            {commits.length === 0 && (
              <div className="empty-text">No saves yet</div>
            )}
          </div>
        </aside>

        {/* ----- CENTER: FILE LIST ----- */}
        <main className="file-area">
          {/* Toolbar */}
          <div className="toolbar">
            <div className="toolbar-left">
              <button className="tool-btn" title="Go Up">
                <ChevronRight size={16} style={{ transform: 'rotate(270deg)' }} />
              </button>
            </div>
            <div className="toolbar-center">
              <div className="address-bar">
                <Home size={14} />
                <span>{repoPath.split('/').pop()}{currentPath !== '/' ? currentPath : ''}</span>
              </div>
            </div>
            <div className="toolbar-right">
              <button className="tool-btn" title="Search">
                <Search size={16} />
              </button>
              <button className="tool-btn" title="Refresh" onClick={loadAll}>
                <RefreshCw size={16} />
              </button>
            </div>
          </div>

          {/* Column Headers */}
          <div className="column-headers">
            <div className="col-name">Name</div>
            <div className="col-status">Status</div>
            <div className="col-date">Date Modified</div>
          </div>

          {/* File List */}
          <div className="file-list">
            {viewMode === 'explorer' ? (
              // Explorer view - show all files in repository
              files.length === 0 ? (
                <div className="empty-folder">
                  <FolderIcon size={48} />
                  <p>This repository is empty</p>
                  <p className="hint">Add some files to get started</p>
                </div>
              ) : (
                files.map(file => (
                  <div 
                    key={file.path}
                    className={`file-row ${selectedItems.has(file.path) ? 'selected' : ''}`}
                    onClick={(e) => handleMultiSelect(file.path, e)}
                  >
                    <div className="col-name">
                      {getFileIcon(file.name, file.type as 'file' | 'folder')}
                      <span className="file-name">{file.name}</span>
                    </div>
                    <div className="col-status">
                      {getChangeIcon(changes.find(c => c.path === file.path)?.type || 'unchanged')}
                      <span className={`status-badge ${changes.find(c => c.path === file.path)?.type || 'unchanged'}`}>
                        {changes.find(c => c.path === file.path)?.type || 'unchanged'}
                      </span>
                    </div>
                    <div className="col-date">{file.size ? `${(file.size / 1024).toFixed(1)} KB` : '—'}</div>
                  </div>
                ))
              )
            ) : (
              // Changes view
              changes.length === 0 ? (
                <div className="empty-folder">
                  <Check size={48} />
                  <p>All saved!</p>
                  <p className="hint">No pending changes</p>
                </div>
              ) : (
                changes.map(change => (
                  <div 
                    key={change.path}
                    className={`file-row ${selectedItems.has(change.path) ? 'selected' : ''}`}
                    onClick={(e) => handleMultiSelect(change.path, e)}
                  >
                    <div className="col-name">
                      {getChangeIcon(change.type)}
                      {getFileIcon(change.path.split('/').pop() || '', 'file')}
                      <span className="file-name">{change.path}</span>
                    </div>
                    <div className="col-status">
                      <span className={`status-badge ${change.type}`}>{change.type}</span>
                    </div>
                    <div className="col-date">—</div>
                  </div>
                ))
              )
            )}
          </div>
        </main>

        {/* ----- RIGHT PANEL: DETAILS & COMMIT ----- */}
        <aside className="details-panel">
          {/* Details Section */}
          <div className="panel-section">
            <div className="panel-header">Details</div>
            {selectedFile ? (
              <div className="detail-content">
                <div className="detail-icon">
                  {getFileIcon(selectedFile.split('/').pop() || '', 'file')}
                </div>
                <div className="detail-name">{selectedFile.split('/').pop()}</div>
                <div className="detail-row">
                  <span>Path:</span>
                  <span>{selectedFile}</span>
                </div>
                <div className="detail-row">
                  <span>Status:</span>
                  <span className={`status-badge ${changes.find(c => c.path === selectedFile)?.type}`}>
                    {changes.find(c => c.path === selectedFile)?.type || 'unchanged'}
                  </span>
                </div>
              </div>
            ) : (
              <div className="detail-empty">
                <p>Select a file to see details</p>
              </div>
            )}
          </div>

          {/* Commit Section */}
          <div className="panel-section commit-section">
            <div className="panel-header">Save Your Changes</div>
            <div className="commit-content">
              <textarea
                className="commit-input"
                placeholder="Describe what you changed..."
                value={commitMessage}
                onChange={(e) => setCommitMessage(e.target.value)}
              />
              
              {suggestion && (
                <div className="suggestion" onClick={() => setCommitMessage(suggestion)}>
                  💡 {suggestion}
                </div>
              )}
              
              <div className="commit-buttons">
                <button 
                  className="btn btn-secondary btn-sm"
                  onClick={handleSuggest}
                  disabled={aiThinking || changes.length === 0}
                >
                  {aiThinking ? 'Thinking...' : 'Suggest'}
                </button>
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={handleCommit}
                  disabled={loading || !commitMessage.trim()}
                >
                  <Save size={14} /> Save
                </button>
              </div>
            </div>
          </div>

          {/* Status Bar */}
          <div className="status-bar">
            <span>{changes.length} changes</span>
            <span>{selectedItems.size} selected</span>
          </div>
        </aside>
      </div>

      {/* Error Toast */}
      {error && (
        <div className="error-toast" onClick={() => setError(null)}>
          {error}
        </div>
      )}

      {/* Path Input Modal */}
      {showPathInput && (
        <div className="modal-overlay" onClick={() => setShowPathInput(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <span>Open Repository</span>
              <button className="modal-close" onClick={() => setShowPathInput(false)}>×</button>
            </div>
            <div className="modal-body">
              <label>Repository Path:</label>
              <input
                type="text"
                className="path-input"
                value={tempPath}
                onChange={(e) => setTempPath(e.target.value)}
                placeholder="Enter repository path..."
                autoFocus
              />
              <p className="path-hint">Example: /mnt/c/Users/you/project or ~/project</p>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowPathInput(false)}>Cancel</button>
              <button 
                className="btn btn-primary" 
                onClick={() => {
                  if (tempPath.trim()) {
                    setRepoPath(tempPath.trim());
                    setShowPathInput(false);
                  }
                }}
              >
                Open
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
