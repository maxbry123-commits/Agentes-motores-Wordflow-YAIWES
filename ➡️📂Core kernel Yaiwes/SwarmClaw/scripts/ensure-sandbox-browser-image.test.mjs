import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { describe, it } from 'node:test'

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

describe('ensure-sandbox-browser-image', () => {
  it('bounds docker image builds with SWARMCLAW_SANDBOX_BROWSER_BUILD_TIMEOUT_MS', () => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'swarmclaw-sandbox-browser-timeout-'))
    const fakeBin = path.join(tempDir, 'bin')
    const scriptsDir = path.join(tempDir, 'scripts')
    fs.mkdirSync(fakeBin, { recursive: true })
    fs.mkdirSync(scriptsDir, { recursive: true })
    fs.copyFileSync(
      path.join(repoRoot, 'Dockerfile.sandbox-browser'),
      path.join(tempDir, 'Dockerfile.sandbox-browser'),
    )
    fs.copyFileSync(
      path.join(repoRoot, 'scripts', 'sandbox-browser-entrypoint.sh'),
      path.join(scriptsDir, 'sandbox-browser-entrypoint.sh'),
    )

    const dockerPath = path.join(fakeBin, 'docker')
    fs.writeFileSync(
      dockerPath,
      [
        '#!/usr/bin/env node',
        'const args = process.argv.slice(2)',
        'if (args[0] === "image" && args[1] === "inspect") process.exit(1)',
        'if (args[0] === "build") setTimeout(() => process.exit(0), 5000)',
        'else process.exit(0)',
        '',
      ].join('\n'),
      'utf8',
    )
    fs.chmodSync(dockerPath, 0o755)

    try {
      const result = spawnSync(
        process.execPath,
        [path.join(repoRoot, 'scripts', 'ensure-sandbox-browser-image.mjs'), '--required'],
        {
          cwd: tempDir,
          env: {
            ...process.env,
            PATH: `${fakeBin}${path.delimiter}${process.env.PATH || ''}`,
            SWARMCLAW_SANDBOX_BROWSER_BUILD_TIMEOUT_MS: '50',
          },
          encoding: 'utf8',
        },
      )
      const combinedOutput = `${result.stdout || ''}\n${result.stderr || ''}`
      assert.notEqual(result.status, 0)
      assert.match(combinedOutput, /Build timed out after 50ms/)
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true })
    }
  })
})
