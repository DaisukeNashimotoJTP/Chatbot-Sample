import { useWorkspaceStore } from '@/stores/workspaceStore';

export const useWorkspace = () => {
  const {
    workspaces,
    currentWorkspace,
    isLoading,
    error,
    fetchWorkspaces,
    createWorkspace,
    getWorkspace,
    getWorkspaceBySlug,
    updateWorkspace,
    deleteWorkspace,
    joinWorkspace,
    leaveWorkspace,
    setCurrentWorkspace,
    clearError,
  } = useWorkspaceStore();

  return {
    workspaces,
    currentWorkspace,
    isLoading,
    error,
    fetchWorkspaces,
    createWorkspace,
    getWorkspace,
    getWorkspaceBySlug,
    updateWorkspace,
    deleteWorkspace,
    joinWorkspace,
    leaveWorkspace,
    setCurrentWorkspace,
    clearError,
  };
};