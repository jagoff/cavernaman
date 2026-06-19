#!/usr/bin/env node
// Regression tests for caveman-mode-tracker.js token output.

const fs = require('fs');
const path = require('path');
const os = require('os');
const assert = require('assert');
const { execFileSync } = require('child_process');
const test = require('node:test');

const ROOT = path.resolve(__dirname, '..');
const TRACKER = path.join(ROOT, 'src', 'hooks', 'caveman-mode-tracker.js');

test('ordinary prompts do not emit a reinforcement payload', () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'caveman-tracker-test-'));
  try {
    const claudeDir = path.join(tmp, '.claude');
    fs.mkdirSync(claudeDir, { recursive: true });
    fs.writeFileSync(path.join(claudeDir, '.cavernaman-active'), 'full');

    const out = execFileSync(process.execPath, [TRACKER], {
      encoding: 'utf8',
      env: { ...process.env, HOME: tmp, CLAUDE_CONFIG_DIR: claudeDir },
      input: JSON.stringify({ prompt: 'what is the status' }),
    });

    assert.strictEqual(out.trim(), '');
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
