import { useState, useEffect } from 'react';
import { 
  Plus, File, Folder, FolderOpen, 
  FileText, Code, Image, Trash2, ChevronRight, ChevronDown,
  Circle, GitMerge, Loader2
} from 'lucide-react';
import { api, Version, Status, Change } from './api';

// Types
interface FileNode {
  name: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  path: string;
}

// ViewMode type removed (unused)

// Icons
const Icons = {
  File: () => <File size={16} />,
  Folder: () => <Folder size={16} />,
  FolderOpen: () => <FolderOpen size={16} />,
  Text: () => <FileText size={16} />,
  Code: () => <Code size={16} />,
  Image: () => <Image size={16} />,
  Trash: () => <Trash2 size={16} />,
  Chevron: () => <ChevronRight size={14} />,
  ChevronDown: () => <ChevronDown size={14} />,
  Circle: () => <Circle size={12} />,
  Merge: () => <GitMerge size={16} />,
  Plus: () => <Plus size={16} />,
  Loading: () => <Loader2 size={16} className="animate-spin" />,
};

function App() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<Status | null>(null);
  const [versions, setVersions] = useState<Version[]>([]);
  const [changes, setChanges] = useState<Change[]>([]);
  const [commitMessage, setCommitMessage] = useState('');
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [aiThinking, setAiThinking] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [repoPath] = useState('/tmp/avcs-test');
  const [error, setError] = useState<string | null>(null);

  // Load data
  useEffect(() => {
    api.setRepoPath(repoPath);
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statusData, logData, diffData] = await Promise.all([
        api.getStatus().catch(() => null),
        api.getLog(30).catch(() => []),
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

  const handleSuggest = async () => {
    setAiThinking(true);
    try {
      const data = await api.suggestCommit();
      setSuggestion(data.suggestion);
    } catch {}
    setAiThinking(false);
  };

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  // Build file tree from changes
  const buildFileTree = (): FileNode[] => {
    const root: FileNode[] = [];
    const pathMap = new Map<string, FileNode>();

    changes.forEach(change => {
      const parts = change.path.split('/');
      let currentPath = '';
      
      parts.forEach((part, i) => {
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        const isLast = i === parts.length - 1;
        
        if (!pathMap.has(currentPath)) {
          const node: FileNode = {
            name: part,
            type: isLast ? 'file' : 'folder',
            path: change.path,
            children: isLast ? undefined : [],
          };
          pathMap.set(currentPath, node);
          
          if (i === 0) {
            root.push(node);
          } else {
            const parentPath = parts.slice(0, i).join('/');
            const parent = pathMap.get(parentPath);
            if (parent?.children) {
              parent.children.push(node);
            }
          }
        }
      });
    });

    return root;
  };

  const fileTree = buildFileTree();

  const getFileIcon = (name: string) => {
    const ext = name.split('.').pop()?.toLowerCase();
    if (['md', 'txt', 'doc', 'docx'].includes(ext || '')) return <Icons.Text />;
    if (['js', 'ts', 'py', 'rs', 'go', 'java'].includes(ext || '')) return <Icons.Code />;
    if (['png', 'jpg', 'jpeg', 'gif', 'svg'].includes(ext || '')) return <Icons.Image />;
    return <Icons.File />;
  };

  const getChangeIcon = (type: string) => {
    switch (type) {
      case 'added': return <span style={{ color: '#22c55e' }}>+</span>;
      case 'modified': return <span style={{ color: '#eab308' }}>~</span>;
      case 'deleted': return <span style={{ color: '#ef4444' }}>-</span>;
      default: return <span style={{ color: '#666' }}>?</span>;
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="logo">
          <div className="logo-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 2v6M12 16v6M2 12h6M16 12h6" />
            </svg>
          </div>
          <span>AugmentedVCS</span>
        </div>
        
        <div className="header-center">
          <div className="branch-selector">
            <Icons.File />
            <span>{status?.branch || 'main'}</span>
            <Icons.Chevron />
          </div>
        </div>

        <div className="header-right">
          <button className="btn-icon" title="Sync">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12a9 9 0 0 1-9 9m0 0a9 9 0 0 1-9-9m9 9V3m0 0l-4 4m4-4l4 4" />
            </svg>
          </button>
          <button className="btn-icon" title="Settings">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
            </svg>
          </button>
        </div>
      </header>

      <div className="main-container">
        {/* Left Panel - Commit Graph (GitKraken style) */}
        <div className="graph-panel">
          <div className="panel-header">
            <span>Commits</span>
            <button className="btn-icon-sm" title="Refresh" onClick={loadData}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8" />
                <path d="M21 3v5h-5" />
              </svg>
            </button>
          </div>
          
          <div className="graph-content">
            {loading && <div className="loading"><Icons.Loading /></div>}
            
            {versions.length === 0 && !loading ? (
              <div className="empty-state">
                <p>No commits yet</p>
                <p className="hint">Create your first commit</p>
              </div>
            ) : (
              <div className="commit-graph">
                {/* Graph lines */}
                <svg className="graph-lines" width="60" height="100%">
                  <line x1="30" y1="0" x2="30" y2="100%" stroke="#333" strokeWidth="2" />
                </svg>
                
                {/* Commits */}
                <div className="commits-list">
                  {versions.map((v) => (
                    <div key={v.id} className="commit-item">
                      <div className="commit-dot" />
                      <div className="commit-info">
                        <div className="commit-message">{v.message}</div>
                        <div className="commit-meta">
                          <span className="commit-hash">{v.id.slice(0, 7)}</span>
                          <span className="commit-date">{new Date(v.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Center Panel - Workspace */}
        <div className="workspace-panel">
          {/* Tabs */}
          <div className="workspace-tabs">
            <button className="tab active">Changes</button>
            <button className="tab">Diff</button>
            <button className="tab">Commit</button>
          </div>

          <div className="workspace-content">
            {/* Stage All Button */}
            <div className="stage-bar">
              <button className="btn btn-primary" onClick={handleStageAll} disabled={loading}>
                <Icons.Plus /> Stage All
              </button>
              <span className="stage-count">{changes.length} changes</span>
            </div>

            {/* Commit Form */}
            <div className="commit-form-mini">
              <textarea
                className="commit-input"
                placeholder="Commit message..."
                value={commitMessage}
                onChange={(e) => setCommitMessage(e.target.value)}
              />
              <div className="commit-actions">
                <button 
                  className="btn btn-secondary btn-sm" 
                  onClick={handleSuggest}
                  disabled={aiThinking || !changes.length}
                >
                  {aiThinking ? <Icons.Loading /> : null}
                  {aiThinking ? 'Thinking...' : 'Suggest'}
                </button>
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={handleCommit}
                  disabled={loading || !commitMessage.trim()}
                >
                  Commit
                </button>
              </div>
              {suggestion && (
                <div className="suggestion" onClick={() => setCommitMessage(suggestion)}>
                  💡 {suggestion}
                </div>
              )}
            </div>

            {/* Files List - GitKraken style */}
            <div className="files-list-mini">
              <div className="files-header">
                <span>Staged Files</span>
              </div>
              {changes.length === 0 ? (
                <div className="empty-files">
                  <p>No changes detected</p>
                  <p className="hint">Edit some files and they'll appear here</p>
                </div>
              ) : (
                changes.map(change => (
                  <div 
                    key={change.path} 
                    className="file-item-mini"
                    onClick={() => setSelectedFile(change.path)}
                  >
                    <span className="file-change-icon">{getChangeIcon(change.type)}</span>
                    {getFileIcon(change.path)}
                    <span className="file-name">{change.path}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Panel - File Explorer */}
        <div className="explorer-panel">
          <div className="panel-header">
            <span>File Explorer</span>
            <button className="btn-icon-sm" title="New File">
              <Icons.Plus />
            </button>
          </div>

          <div className="explorer-content">
            {/* Quick Actions */}
            <div className="explorer-actions">
              <button className="action-btn" title="New File">
                <Icons.Plus />
              </button>
              <button className="action-btn" title="Refresh">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8" />
                  <path d="M21 3v5h-5" />
                </svg>
              </button>
            </div>

            {/* File Tree */}
            <div className="file-tree">
              {fileTree.map(node => (
                <div key={node.path} className="tree-node">
                  <div className="tree-item" onClick={() => node.children && toggleFolder(node.path)}>
                    {node.type === 'folder' ? (
                      <>
                        <span className="tree-toggle">
                          {expandedFolders.has(node.path) ? <Icons.ChevronDown /> : <Icons.Chevron />}
                        </span>
                        {expandedFolders.has(node.path) ? <Icons.FolderOpen /> : <Icons.Folder />}
                      </>
                    ) : (
                      <>
                        <span className="tree-toggle" />
                        {getFileIcon(node.name)}
                      </>
                    )}
                    <span className="tree-name">{node.name}</span>
                    {node.type === 'file' && (
                      <span className="tree-status">
                        {getChangeIcon(changes.find(c => c.path === node.path)?.type || '')}
                      </span>
                    )}
                  </div>
                  
                  {node.type === 'folder' && node.children && expandedFolders.has(node.path) && (
                    <div className="tree-children">
                      {node.children.map(child => (
                        <div key={child.path} className="tree-node">
                          <div className="tree-item">
                            <span className="tree-toggle" />
                            {getFileIcon(child.name)}
                            <span className="tree-name">{child.name}</span>
                            <span className="tree-status">
                              {getChangeIcon(changes.find(c => c.path === child.path)?.type || '')}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* File Details */}
          {selectedFile && (
            <div className="file-details">
              <div className="details-header">
                <span>{selectedFile.split('/').pop()}</span>
                <button className="btn-icon-sm" onClick={() => setSelectedFile(null)}>×</button>
              </div>
              <div className="details-meta">
                <span>Path: {selectedFile}</span>
                <span>Status: {changes.find(c => c.path === selectedFile)?.type || 'unchanged'}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error Toast */}
      {error && (
        <div className="error-toast" onClick={() => setError(null)}>
          {error}
        </div>
      )}
    </div>
  );
}

export default App;
