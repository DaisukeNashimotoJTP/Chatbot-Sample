/**
 * バリデーション関連のユーティリティ関数
 */

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * メールアドレスのバリデーション
 */
export function validateEmail(email: string): ValidationResult {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!email) {
    return { isValid: false, error: 'メールアドレスを入力してください' };
  }
  
  if (!emailRegex.test(email)) {
    return { isValid: false, error: '有効なメールアドレスを入力してください' };
  }
  
  return { isValid: true };
}

/**
 * パスワードのバリデーション
 */
export function validatePassword(password: string): ValidationResult {
  if (!password) {
    return { isValid: false, error: 'パスワードを入力してください' };
  }
  
  if (password.length < 8) {
    return { isValid: false, error: 'パスワードは8文字以上で入力してください' };
  }
  
  if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
    return { 
      isValid: false, 
      error: 'パスワードは大文字・小文字・数字を含む必要があります' 
    };
  }
  
  return { isValid: true };
}

/**
 * ユーザー名のバリデーション
 */
export function validateUsername(username: string): ValidationResult {
  if (!username) {
    return { isValid: false, error: 'ユーザー名を入力してください' };
  }
  
  if (username.length < 3 || username.length > 30) {
    return { isValid: false, error: 'ユーザー名は3文字以上30文字以下で入力してください' };
  }
  
  if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
    return { 
      isValid: false, 
      error: 'ユーザー名は英数字、ハイフン、アンダースコアのみ使用できます' 
    };
  }
  
  return { isValid: true };
}

/**
 * 表示名のバリデーション
 */
export function validateDisplayName(displayName: string): ValidationResult {
  if (!displayName) {
    return { isValid: false, error: '表示名を入力してください' };
  }
  
  if (displayName.length < 1 || displayName.length > 50) {
    return { isValid: false, error: '表示名は1文字以上50文字以下で入力してください' };
  }
  
  return { isValid: true };
}

/**
 * ワークスペース名のバリデーション
 */
export function validateWorkspaceName(name: string): ValidationResult {
  if (!name) {
    return { isValid: false, error: 'ワークスペース名を入力してください' };
  }
  
  if (name.length < 1 || name.length > 80) {
    return { isValid: false, error: 'ワークスペース名は1文字以上80文字以下で入力してください' };
  }
  
  return { isValid: true };
}

/**
 * ワークスペーススラッグのバリデーション
 */
export function validateWorkspaceSlug(slug: string): ValidationResult {
  if (!slug) {
    return { isValid: false, error: 'ワークスペースURLを入力してください' };
  }
  
  if (slug.length < 3 || slug.length > 50) {
    return { isValid: false, error: 'ワークスペースURLは3文字以上50文字以下で入力してください' };
  }
  
  if (!/^[a-z0-9-]+$/.test(slug)) {
    return { 
      isValid: false, 
      error: 'ワークスペースURLは小文字の英数字とハイフンのみ使用できます' 
    };
  }
  
  if (slug.startsWith('-') || slug.endsWith('-')) {
    return { isValid: false, error: 'ワークスペースURLはハイフンで始まったり終わったりできません' };
  }
  
  return { isValid: true };
}

/**
 * チャンネル名のバリデーション
 */
export function validateChannelName(name: string): ValidationResult {
  if (!name) {
    return { isValid: false, error: 'チャンネル名を入力してください' };
  }
  
  if (name.length < 1 || name.length > 80) {
    return { isValid: false, error: 'チャンネル名は1文字以上80文字以下で入力してください' };
  }
  
  if (!/^[a-z0-9-_]+$/.test(name)) {
    return { 
      isValid: false, 
      error: 'チャンネル名は小文字の英数字、ハイフン、アンダースコアのみ使用できます' 
    };
  }
  
  return { isValid: true };
}

/**
 * メッセージ内容のバリデーション
 */
export function validateMessage(content: string): ValidationResult {
  if (!content.trim()) {
    return { isValid: false, error: 'メッセージを入力してください' };
  }
  
  if (content.length > 4000) {
    return { isValid: false, error: 'メッセージは4000文字以下で入力してください' };
  }
  
  return { isValid: true };
}

/**
 * 招待コードのバリデーション
 */
export function validateInviteCode(code: string): ValidationResult {
  if (!code) {
    return { isValid: false, error: '招待コードを入力してください' };
  }
  
  if (code.length !== 8) {
    return { isValid: false, error: '招待コードは8文字である必要があります' };
  }
  
  if (!/^[A-Z0-9]+$/.test(code)) {
    return { isValid: false, error: '招待コードは大文字の英数字のみ使用できます' };
  }
  
  return { isValid: true };
}

/**
 * URLのバリデーション
 */
export function validateUrl(url: string): ValidationResult {
  if (!url) {
    return { isValid: true }; // URLは任意の場合が多い
  }
  
  try {
    new URL(url);
    return { isValid: true };
  } catch {
    return { isValid: false, error: '有効なURLを入力してください' };
  }
}

/**
 * 複数のバリデーション結果をまとめる
 */
export function combineValidationResults(...results: ValidationResult[]): ValidationResult {
  for (const result of results) {
    if (!result.isValid) {
      return result;
    }
  }
  return { isValid: true };
}
