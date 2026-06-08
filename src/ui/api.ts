// API client for AugmentedVCS

const API_BASE = '/api';

interface Version {
  id: string;
  message: string;
  created_at: string;
  author: string;
}

interface Branch {
  name: string;
  head_version_id: string | null;
}

interface Status {
  initialized: boolean;
  branch: string | null;
  staged: Array<[string, string]>;
  modified: string[];
  new_staged: string[];
  deleted: string[];
}

interface Change {
  path: string;
  type: 'added' | 'modified' | 'deleted';
}

interface FileItem {
  name: string;
  path: string;
  type: 'file' | 'folder';
  size: number | null;
}

class ApiClient {
  private repoPath: string = '';

  setRepoPath(path: string) {
    this.repoPath = encodeURIComponent(path);
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE}${path}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async getStatus(): Promise<Status> {
    return this.request<Status>(`/repositories/${this.repoPath}/status`);
  }

  async getLog(count: number = 20): Promise<Version[]> {
    return this.request<Version[]>(`/repositories/${this.repoPath}/log?count=${count}`);
  }

  async getBranches(): Promise<Branch[]> {
    return this.request<Branch[]>(`/repositories/${this.repoPath}/branches`);
  }

  async getDiff(): Promise<{ changes: Change[] }> {
    return this.request<{ changes: Change[] }>(`/repositories/${this.repoPath}/diff`);
  }

  async getFiles(): Promise<FileItem[]> {
    return this.request<FileItem[]>(`/repositories/${this.repoPath}/files`);
  }

  async addFiles(files: string[]): Promise<{ staged: string[]; count: number }> {
    return this.request(`/repositories/${this.repoPath}/add`, {
      method: 'POST',
      body: JSON.stringify({ files }),
    });
  }

  async commit(message: string, author: string = 'user'): Promise<Version> {
    return this.request<Version>(`/repositories/${this.repoPath}/commit`, {
      method: 'POST',
      body: JSON.stringify({ message, author }),
    });
  }

  async unstage(file: string): Promise<{ message: string }> {
    return this.request(`/repositories/${this.repoPath}/unstage/${encodeURIComponent(file)}`, {
      method: 'DELETE',
    });
  }

  async createBranch(name: string): Promise<{ message: string }> {
    return this.request(`/repositories/${this.repoPath}/branches`, {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  async checkout(branch?: string, version?: string): Promise<{ message: string }> {
    return this.request(`/repositories/${this.repoPath}/checkout`, {
      method: 'POST',
      body: JSON.stringify({ branch, version }),
    });
  }

  async suggestCommit(): Promise<{ suggestion: string }> {
    return this.request<{ suggestion: string }>(`/repositories/${this.repoPath}/ai/suggest`, {
      method: 'POST',
    });
  }

  async explainChanges(): Promise<{ explanation: string }> {
    return this.request<{ explanation: string }>(`/repositories/${this.repoPath}/ai/explain`, {
      method: 'POST',
    });
  }

  async tellStory(count: number = 10): Promise<{ story: string }> {
    return this.request<{ story: string }>(`/repositories/${this.repoPath}/ai/story`, {
      method: 'POST',
      body: JSON.stringify({ count }),
    });
  }

  async getAiStatus(): Promise<Record<string, { available: boolean; model?: string }>> {
    return this.request<Record<string, { available: boolean; model?: string }>>(
      `/repositories/${this.repoPath}/ai/status`
    );
  }

  async init(path: string, description?: string): Promise<{ message: string; path: string }> {
    return this.request(`/repositories`, {
      method: 'POST',
      body: JSON.stringify({ path, description }),
    });
  }
}

export const api = new ApiClient();
export type { Version, Branch, Status, Change, FileItem };
