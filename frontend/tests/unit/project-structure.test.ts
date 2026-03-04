import { describe, it, expect, beforeEach } from 'vitest'
import { existsSync, readFileSync, unlinkSync } from 'fs'
import { join } from 'path'

// Test configuration
const PROJECT_ROOT = join(process.cwd(), 'frontend')
const SRC_DIR = join(PROJECT_ROOT, 'src')

describe('Project Structure - Task 01', () => {
  beforeEach(() => {
    // Setup before each test
  })

  describe('Directory Structure', () => {
    it('should have src directory', () => {
      expect(existsSync(SRC_DIR)).toBe(true)
    })

    it('should have src/components directory', () => {
      expect(existsSync(join(SRC_DIR, 'components'))).toBe(true)
    })

    it('should have src/pages directory', () => {
      expect(existsSync(join(SRC_DIR, 'pages'))).toBe(true)
    })

    it('should have src/hooks directory', () => {
      expect(existsSync(join(SRC_DIR, 'hooks'))).toBe(true)
    })

    it('should have src/store directory', () => {
      expect(existsSync(join(SRC_DIR, 'store'))).toBe(true)
    })

    it('should have src/services directory', () => {
      expect(existsSync(join(SRC_DIR, 'services'))).toBe(true)
    })

    it('should have src/types directory', () => {
      expect(existsSync(join(SRC_DIR, 'types'))).toBe(true)
    })

    it('should have src/utils directory', () => {
      expect(existsSync(join(SRC_DIR, 'utils'))).toBe(true)
    })

    it('should have src/styles directory', () => {
      expect(existsSync(join(SRC_DIR, 'styles'))).toBe(true)
    })
  })

  describe('Configuration Files', () => {
    it('should have package.json', () => {
      expect(existsSync(join(PROJECT_ROOT, 'package.json'))).toBe(true)
    })

    it('should have tsconfig.json', () => {
      expect(existsSync(join(PROJECT_ROOT, 'tsconfig.json'))).toBe(true)
    })

    it('should have vite.config.ts', () => {
      expect(existsSync(join(PROJECT_ROOT, 'vite.config.ts'))).toBe(true)
    })

    it('should have vite-env.d.ts', () => {
      expect(existsSync(join(PROJECT_ROOT, 'vite-env.d.ts'))).toBe(true)
    })

    it('should have .env file', () => {
      expect(existsSync(join(PROJECT_ROOT, '.env'))).toBe(true)
    })

    it('should have index.html in public', () => {
      expect(existsSync(join(PROJECT_ROOT, 'public', 'index.html'))).toBe(true)
    })

    it('should have manifest.json in public', () => {
      expect(existsSync(join(PROJECT_ROOT, 'public', 'manifest.json'))).toBe(true)
    })

    it('should have favicon.ico in public', () => {
      expect(existsSync(join(PROJECT_ROOT, 'public', 'favicon.ico'))).toBe(true)
    })
  })

  describe('TypeScript Configuration', () => {
    it('should have src/types/index.ts', () => {
      expect(existsSync(join(SRC_DIR, 'types', 'index.ts'))).toBe(true)
    })

    it('should have strict type checking enabled', () => {
      const tsconfig = JSON.parse(readFileSync(join(PROJECT_ROOT, 'tsconfig.json'), 'utf-8'))
      expect(tsconfig.compilerOptions?.strict).toBe(true)
    })
  })
})
