import { create } from 'zustand';
import { Workspace, WorkspaceCreate, WorkspaceUpdate } from '@/types/workspace';
import { apiClient } from '@/lib/api';

interface WorkspaceState {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  isLoading: boolean;
  error: string | null;
}

interface WorkspaceActions {
  fetchWorkspaces: () => Promise<void>;
  createWorkspace: (data: WorkspaceCreate) => Promise<Workspace>;
  getWorkspace: (workspaceId: string) => Promise<Workspace>;
  getWorkspaceBySlug: (slug: string) => Promise<Workspace>;
  updateWorkspace: (workspaceId: string, data: WorkspaceUpdate) => Promise<Workspace>;
  deleteWorkspace: (workspaceId: string) => Promise<void>;
  joinWorkspace: (inviteCode: string) => Promise<Workspace>;
  leaveWorkspace: (workspaceId: string) => Promise<void>;
  setCurrentWorkspace: (workspace: Workspace | null) => void;
  clearError: () => void;
}

type WorkspaceStore = WorkspaceState & WorkspaceActions;

export const useWorkspaceStore = create<WorkspaceStore>((set, get) => ({
  // Initial state
  workspaces: [],
  currentWorkspace: null,
  isLoading: false,
  error: null,

  // Actions
  fetchWorkspaces: async () => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiClient.getWorkspaces();
      const workspaces = response.data;

      set({
        workspaces,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to fetch workspaces',
      });
      throw error;
    }
  },

  createWorkspace: async (data: WorkspaceCreate) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiClient.createWorkspace(data);
      const workspace = response.data;

      set((state) => ({
        workspaces: [...state.workspaces, workspace],
        isLoading: false,
      }));

      return workspace;
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to create workspace',
      });
      throw error;
    }
  },

  getWorkspace: async (workspaceId: string) => {
    try {
      const response = await apiClient.getWorkspace(workspaceId);
      const workspace = response.data;

      // Update workspace in the list if it exists
      set((state) => ({
        workspaces: state.workspaces.map((w) =>
          w.id === workspaceId ? workspace : w
        ),
        currentWorkspace: workspace,
      }));

      return workspace;
    } catch (error: any) {
      set({
        error: error.message || 'Failed to get workspace',
      });
      throw error;
    }
  },

  getWorkspaceBySlug: async (slug: string) => {
    try {
      const response = await apiClient.getWorkspaceBySlug(slug);
      const workspace = response.data;

      set({
        currentWorkspace: workspace,
      });

      return workspace;
    } catch (error: any) {
      set({
        error: error.message || 'Failed to get workspace',
      });
      throw error;
    }
  },

  updateWorkspace: async (workspaceId: string, data: WorkspaceUpdate) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiClient.updateWorkspace(workspaceId, data);
      const workspace = response.data;

      set((state) => ({
        workspaces: state.workspaces.map((w) =>
          w.id === workspaceId ? workspace : w
        ),
        currentWorkspace:
          state.currentWorkspace?.id === workspaceId
            ? workspace
            : state.currentWorkspace,
        isLoading: false,
      }));

      return workspace;
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to update workspace',
      });
      throw error;
    }
  },

  deleteWorkspace: async (workspaceId: string) => {
    try {
      set({ isLoading: true, error: null });

      await apiClient.deleteWorkspace(workspaceId);

      set((state) => ({
        workspaces: state.workspaces.filter((w) => w.id !== workspaceId),
        currentWorkspace:
          state.currentWorkspace?.id === workspaceId
            ? null
            : state.currentWorkspace,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to delete workspace',
      });
      throw error;
    }
  },

  joinWorkspace: async (inviteCode: string) => {
    try {
      set({ isLoading: true, error: null });

      const response = await apiClient.joinWorkspace(inviteCode);
      const workspace = response.data;

      set((state) => ({
        workspaces: [...state.workspaces, workspace],
        isLoading: false,
      }));

      return workspace;
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to join workspace',
      });
      throw error;
    }
  },

  leaveWorkspace: async (workspaceId: string) => {
    try {
      set({ isLoading: true, error: null });

      await apiClient.leaveWorkspace(workspaceId);

      set((state) => ({
        workspaces: state.workspaces.filter((w) => w.id !== workspaceId),
        currentWorkspace:
          state.currentWorkspace?.id === workspaceId
            ? null
            : state.currentWorkspace,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Failed to leave workspace',
      });
      throw error;
    }
  },

  setCurrentWorkspace: (workspace: Workspace | null) => {
    set({ currentWorkspace: workspace });
  },

  clearError: () => set({ error: null }),
}));