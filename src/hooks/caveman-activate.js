#!/usr/bin/env node
// caveman — Claude Code SessionStart activation hook
//
// Runs on every session start:
//   1. Writes flag file at $CLAUDE_CONFIG_DIR/.cavernaman-active (statusline reads this)
//   2. Emits caveman ruleset as hidden SessionStart context
//   3. Detects missing statusline config and emits setup nudge

const fs = require('fs');
const path = require('path');
const os = require('os');
const { getDefaultMode, safeWriteFlag } = require('./caveman-config');
let getSessionPrompt = null;
try {
  ({ getSessionPrompt } = require('./caveman-session-prompt'));
} catch (e) {
  // Standalone fallback path still works without the compiled helper.
}

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.cavernaman-active');
const settingsPath = path.join(claudeDir, 'settings.json');

const mode = getDefaultMode();

// "off" mode — skip activation entirely, don't write flag or emit rules
if (mode === 'off') {
  try { fs.unlinkSync(flagPath); } catch (e) {}
  process.stdout.write('OK');
  process.exit(0);
}

// 1. Write flag file (symlink-safe)
safeWriteFlag(flagPath, mode);

// 2. Emit the compiled caveman ruleset for the active intensity level.
//    Keep it short: this text stays in the session context every turn.

// Modes that have their own independent skill files — not caveman intensity levels.
// For these, emit a short activation line; the skill itself handles behavior.
const INDEPENDENT_MODES = new Set(['commit', 'review', 'compress']);

if (INDEPENDENT_MODES.has(mode)) {
  process.stdout.write('CAVERNAMAN MODE ACTIVE — level: ' + mode + '. Behavior defined by /caveman-' + mode + ' skill.');
  process.exit(0);
}

// Resolve the canonical label for wenyan alias
const modeLabel = mode === 'wenyan' ? 'wenyan-full' : mode;

let output;

try {
  output = getSessionPrompt(modeLabel);
} catch (e) {
  // Fallback when the compiled prompt helper is not available.
  output =
    'CAVERNAMAN MODE ACTIVE — level: ' + modeLabel + '\n\n' +
    'Respond terse, technical, no fluff.\n\n' +
    'Persistence: active every response until user says "stop cavernaman" or "normal mode".\n\n' +
    `Current level: **${modeLabel}**. Switch: /cavernaman lite|full|ultra.\n\n` +
    'Rules: keep substance; drop filler, hedging, pleasantries. Fragments OK. Exact code and errors. Code/commits/PRs stay normal.\n\n' +
    'Auto-Clarity: switch to normal for security, irreversible action, or multi-step ambiguity, then resume.\n\n' +
    'Boundaries: stop only on "stop cavernaman" or "normal mode".';
}

// 3. Detect missing statusline config — nudge Claude to help set it up
try {
  let hasStatusline = false;
  if (fs.existsSync(settingsPath)) {
    const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
    if (settings.statusLine) {
      hasStatusline = true;
    }
  }

  if (!hasStatusline) {
    const isWindows = process.platform === 'win32';
    const scriptName = isWindows ? 'caveman-statusline.ps1' : 'caveman-statusline.sh';
    const scriptPath = path.join(__dirname, scriptName);
    const command = isWindows
      ? `powershell -ExecutionPolicy Bypass -File "${scriptPath}"`
      : `bash "${scriptPath}"`;
    const statusLineSnippet =
      '"statusLine": { "type": "command", "command": ' + JSON.stringify(command) + ' }';
    output += "\n\n" +
      "STATUSLINE SETUP NEEDED: add a statusLine command for the caveman badge. " +
      "Add this to " + path.join(claudeDir, 'settings.json') + ": " +
      statusLineSnippet + ". Offer to set it up.";
  }
} catch (e) {
  // Silent fail — don't block session start over statusline detection
}

process.stdout.write(output);
