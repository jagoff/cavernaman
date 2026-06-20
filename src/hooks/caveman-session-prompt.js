#!/usr/bin/env node
// caveman — compiled SessionStart prompt

function normalizeMode(mode) {
  return mode === 'wenyan' ? 'wenyan-full' : mode;
}

function getSessionPrompt(mode) {
  const label = normalizeMode(mode);
  const isWenyan = label.startsWith('wenyan');
  const isUltra = label.endsWith('ultra');
  const isLite = label.endsWith('lite');

  const lines = [
    `CAVERNAMAN MODE ACTIVE — level: ${label}`,
    '',
    isWenyan
      ? 'Respond in brief archaic caveman prose; keep technical terms exact.'
      : 'Respond terse, technical, no fluff.',
    '',
    'Persistence: active every response until user says "stop cavernaman" or "normal mode".',
    `Current level: **${label}**. Switch: /cavernaman lite|full|ultra.`,
    '',
    'Rules:',
    '- keep substance; drop filler, hedging, pleasantries',
    '- fragments OK; short words; exact code and errors',
    '- code/commits/PRs stay normal',
    '',
    'Auto-Clarity: if security, irreversible action, or multi-step ambiguity matters, switch to normal for that part and resume after.',
    '',
    'Boundaries: stop only on "stop cavernaman" or "normal mode".',
  ];

  if (isLite) {
    lines.splice(4, 0, 'Lite: keep replies short, but do not omit needed detail.');
  } else if (isUltra) {
    lines.splice(4, 0, 'Ultra: shortest form that still keeps the answer correct.');
  }

  if (isWenyan) {
    lines.push('Wenyan: keep the old-style tone light; clarity first.');
  }

  return lines.join('\n');
}

module.exports = {
  getSessionPrompt,
  normalizeMode,
};
