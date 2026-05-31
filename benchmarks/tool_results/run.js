#!/usr/bin/env node
// Run the tool-result corpus through the EXACT proxy gate+compress logic
// (looksStructured → compress) and write before/after pairs for measure.py.
//
// This is the JS half of the harness, mirroring the evals split: Node
// produces the compressed text using the real caveman-shrink code, Python
// (measure.py) counts tokens with tiktoken. No API calls, no cost.
//
// Run: node benchmarks/tool_results/run.js

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const { compress, looksStructured } = require(
  path.join(ROOT, 'src', 'mcp-servers', 'caveman-shrink', 'compress.js')
);

const corpusPath = path.join(__dirname, 'corpus.json');
const outPath = path.join(__dirname, 'results-raw.json');

const corpus = JSON.parse(fs.readFileSync(corpusPath, 'utf8'));

const results = corpus.items.map(item => {
  const skipped = looksStructured(item.text);
  const after = skipped ? item.text : compress(item.text).compressed;
  return {
    id: item.id,
    kind: item.kind,
    skipped,
    before: item.text,
    after,
    before_chars: item.text.length,
    after_chars: after.length,
  };
});

const out = {
  generated_note: "Produced by benchmarks/tool_results/run.js using the real "
    + "caveman-shrink compress()/looksStructured(). Token counts added by measure.py.",
  n_items: results.length,
  results,
};

fs.writeFileSync(outPath, JSON.stringify(out, null, 2));

// Quick char-level preview (token-accurate numbers come from measure.py).
const totBefore = results.reduce((a, r) => a + r.before_chars, 0);
const totAfter = results.reduce((a, r) => a + r.after_chars, 0);
const pct = ((1 - totAfter / totBefore) * 100).toFixed(1);
console.log(`Wrote ${outPath}`);
console.log(`Char-level blended reduction: ${totBefore}→${totAfter} (${pct}%)`);
console.log(`(${results.filter(r => r.skipped).length}/${results.length} items skipped as structured)`);
console.log(`Run measure.py for token-accurate numbers.`);
