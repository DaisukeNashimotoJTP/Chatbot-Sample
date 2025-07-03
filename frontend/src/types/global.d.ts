// グローバル型定義
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NEXT_PUBLIC_API_URL?: string;
    }
  }

  var process: {
    env: {
      NEXT_PUBLIC_API_URL?: string;
      NODE_ENV?: string;
    };
  };
}

export {};
