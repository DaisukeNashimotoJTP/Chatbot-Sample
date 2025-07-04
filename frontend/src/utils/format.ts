/**
 * 日付をフォーマットする関数
 */
export function formatDate(
  date: string | Date,
  options?: Intl.DateTimeFormatOptions
): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  };

  return dateObj.toLocaleDateString('ja-JP', { ...defaultOptions, ...options });
}

/**
 * 相対時間を表示する関数
 */
export function formatRelativeTime(
  date: string | Date,
  currentTime?: Date
): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = currentTime || new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return '今';
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes}分前`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours}時間前`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays}日前`;
  }

  return formatDate(dateObj, { month: 'short', day: 'numeric' });
}

/**
 * ファイルサイズをフォーマットする関数
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * メンバー数をフォーマットする関数
 */
export function formatMemberCount(count: number): string {
  if (count === 1) {
    return '1人のメンバー';
  }
  return `${count}人のメンバー`;
}

/**
 * チャンネル名をフォーマットする関数
 */
export function formatChannelName(
  name: string,
  type: 'public' | 'private'
): string {
  if (type === 'private') {
    return `🔒 ${name}`;
  }
  return `# ${name}`;
}

/**
 * ユーザー表示名をフォーマットする関数
 */
export function formatUserDisplayName(user: {
  display_name?: string;
  username: string;
}): string {
  return user.display_name || user.username;
}

/**
 * テキストを切り詰める関数
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.slice(0, maxLength) + '...';
}

/**
 * URLからドメインを抽出する関数
 */
export function extractDomain(url: string): string {
  try {
    const parsedUrl = new URL(url);
    return parsedUrl.hostname;
  } catch {
    return url;
  }
}
