// Jest setup file
import 'jest-environment-jsdom';

// localStorage のモック
const localStorageMock = {
  getItem: () => null,
  setItem: () => {},
  removeItem: () => {},
  clear: () => {},
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

// console.error を抑制（テスト時のログを見やすくする）
const originalConsoleError = console.error;
console.error = (...args) => {
  if (
    args.length &&
    typeof args[0] === 'string' &&
    (args[0].includes('Not implemented: navigation') ||
      args[0].includes('WebSocket error'))
  ) {
    return;
  }
  originalConsoleError(...args);
};

// console.log を抑制（テスト時のログを見やすくする）
const originalConsoleLog = console.log;
console.log = (...args) => {
  if (
    args.length &&
    typeof args[0] === 'string' &&
    (args[0].includes('WebSocket') || args[0].includes('Attempting'))
  ) {
    return;
  }
  originalConsoleLog(...args);
};
