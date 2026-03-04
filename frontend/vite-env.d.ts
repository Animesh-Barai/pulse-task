/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly mode: 'development' | 'production'
}

interface ImportMeta {
  readonly glob: string[]
  readonly file: string
}

declare const env: ImportMetaEnv

export default env
