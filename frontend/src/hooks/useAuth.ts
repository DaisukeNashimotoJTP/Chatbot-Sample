import { useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';

export const useAuth = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    getCurrentUser,
    clearError,
  } = useAuthStore();

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token && !user) {
        try {
          await getCurrentUser();
        } catch (error) {
          // Token is invalid, logout to clear all state
          console.error('Token validation failed:', error);
          await logout();
        }
      }
    };

    initializeAuth();
  }, [user, getCurrentUser, logout]);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
  };
};