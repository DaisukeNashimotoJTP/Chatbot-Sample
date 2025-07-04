// Jest型定義の拡張
/// <reference types="jest" />

declare global {
  const jest: typeof import('@jest/globals')['jest'];
  const describe: typeof import('@jest/globals')['describe'];
  const test: typeof import('@jest/globals')['test'];
  const it: typeof import('@jest/globals')['it'];
  const expect: typeof import('@jest/globals')['expect'];
  const beforeEach: typeof import('@jest/globals')['beforeEach'];
  const afterEach: typeof import('@jest/globals')['afterEach'];
  const beforeAll: typeof import('@jest/globals')['beforeAll'];
  const afterAll: typeof import('@jest/globals')['afterAll'];
}
