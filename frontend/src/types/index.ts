export * from './auth';
export * from './workspace';
export * from './channel';
export * from './message';

export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}