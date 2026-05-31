#!/usr/bin/env node
// Tests for src/mcp-servers/caveman-shrink/compress.js — pure-Node prose compressor.
// Run: node tests/test_mcp_shrink.js

const path = require('path');
const assert = require('assert');
const { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const SHRINK_DIR = path.join(ROOT, 'src', 'mcp-servers', 'caveman-shrink');
const { compress, compressDescriptionsInPlace, looksStructured } = require(
  path.join(SHRINK_DIR, 'compress.js')
);

// Spawn the proxy (index.js) wrapping a fake upstream that emits a single
// JSON-RPC response line, and return the proxy's transformed stdout parsed.
function proxyRoundtrip(upstreamResponseObj, env) {
  const upstreamScript =
    'process.stdout.write(' +
    JSON.stringify(JSON.stringify(upstreamResponseObj)) +
    " + '\\n')";
  const out = execFileSync(
    process.execPath,
    [path.join(SHRINK_DIR, 'index.js'), process.execPath, '-e', upstreamScript],
    { input: '', encoding: 'utf8', env: { ...process.env, ...env } }
  );
  return JSON.parse(out.trim().split('\n').filter(Boolean).pop());
}

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ✓ ${name}`);
  } catch (e) {
    failed++;
    console.error(`  ✗ ${name}\n    ${e.message}`);
  }
}

console.log('mcp-shrink compress tests\n');

test('drops articles', () => {
  const { compressed } = compress('The user is the owner of an account');
  assert.match(compressed, /User is owner of account/i);
  // No leftover lone "the" / "an" / "a"
  assert.doesNotMatch(compressed, /\bthe\b/i);
  assert.doesNotMatch(compressed, /\ban\b/i);
});

test('drops filler and pleasantries', () => {
  const { compressed } = compress('Sure, this just basically returns the value');
  assert.doesNotMatch(compressed, /sure/i);
  assert.doesNotMatch(compressed, /just/i);
  assert.doesNotMatch(compressed, /basically/i);
});

test('drops hedging and "I will" leaders', () => {
  const { compressed } = compress('I will perhaps connect to the database');
  assert.doesNotMatch(compressed, /perhaps/i);
  assert.doesNotMatch(compressed, /^I will/i);
  assert.match(compressed, /database/i);
});

test('preserves fenced code blocks verbatim', () => {
  const input = 'Run the example: ```\nthe just sure return 1;\n``` and also more text';
  const { compressed } = compress(input);
  // Inside the fence, "the just sure" must survive untouched.
  assert.match(compressed, /```\nthe just sure return 1;\n```/);
});

test('preserves inline code verbatim', () => {
  const input = 'Use `the just basically API` for fetching';
  const { compressed } = compress(input);
  assert.match(compressed, /`the just basically API`/);
});

test('preserves URLs verbatim', () => {
  const input = 'See the docs at https://example.com/the/just/api';
  const { compressed } = compress(input);
  assert.match(compressed, /https:\/\/example\.com\/the\/just\/api/);
});

test('preserves filesystem paths verbatim', () => {
  const input = 'Read just the file at /tmp/the/just/file.txt';
  const { compressed } = compress(input);
  assert.match(compressed, /\/tmp\/the\/just\/file\.txt/);
});

test('preserves identifiers in CONST_CASE / dotted form', () => {
  const input = 'Set the API_KEY_VALUE on the just config.api.endpoint()';
  const { compressed } = compress(input);
  assert.match(compressed, /API_KEY_VALUE/);
  assert.match(compressed, /config\.api\.endpoint\(\)/);
});

test('compresses real MCP-style description', () => {
  const input = 'Get the current weather for a given location. ' +
    'Returns the temperature in Fahrenheit. ' +
    'Please make sure to provide the location as a city name.';
  const { compressed, before, after } = compress(input);
  assert.ok(after < before, `expected size reduction, got ${before}→${after}`);
  // ~30% reduction is the floor; descriptions like this should compress well.
  assert.ok((before - after) / before > 0.15, `wanted >15% savings, got ${(before - after) / before}`);
  // Substance preserved
  assert.match(compressed, /weather/i);
  assert.match(compressed, /Fahrenheit/i);
  assert.match(compressed, /city name/i);
});

test('handles empty / null input gracefully', () => {
  assert.deepStrictEqual(compress(''), { compressed: '', before: 0, after: 0 });
  const r = compress(null);
  assert.strictEqual(r.compressed, null);
});

test('compressDescriptionsInPlace walks nested tools/list response', () => {
  const payload = {
    result: {
      tools: [
        { name: 'get_weather', description: 'The function returns the current weather for a city.' },
        { name: 'send_email', description: 'Sends an email to a given recipient.' },
      ]
    }
  };
  compressDescriptionsInPlace(payload.result, ['description']);
  assert.ok(!payload.result.tools[0].description.match(/\bthe\b/i),
    `expected 'the' stripped, got: ${payload.result.tools[0].description}`);
  assert.match(payload.result.tools[0].description, /weather/i);
  assert.match(payload.result.tools[1].description, /email/i);
});

test('compressDescriptionsInPlace skips non-string description fields', () => {
  const obj = { description: { not: 'a string' }, name: 'x' };
  // Should not throw.
  compressDescriptionsInPlace(obj, ['description']);
  assert.deepStrictEqual(obj.description, { not: 'a string' });
});

// --- looksStructured guard ---

test('looksStructured: skips JSON / array / short / base64 / tabular', () => {
  assert.ok(looksStructured('{"key": "value", "n": 1, "ok": true, "list": [1,2]}'));
  assert.ok(looksStructured('[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]'));
  assert.ok(looksStructured('short text'));
  assert.ok(looksStructured('a,b,c\n1,2,3\n4,5,6\n7,8,9'));
  assert.ok(looksStructured('aGVsbG8gd29ybGQgdGhpcyBpcyBhIGxvbmcgYmFzZTY0IGJsb2IgdGhhdCBnb2VzIG9u'));
});

test('looksStructured: passes real prose through to compression', () => {
  const prose = 'The function returns the current weather for a given city. ' +
    'Please make sure to provide a valid location name before calling it.';
  assert.ok(!looksStructured(prose), 'prose should NOT be flagged structured');
});

// --- tools/call result compression (integration via proxy) ---

test('proxy compresses prose text in tools/call result', () => {
  const resp = {
    jsonrpc: '2.0', id: 1,
    result: { content: [{ type: 'text',
      text: 'The handler will basically just connect to the database and ' +
            'then return the current value for a given user account.' }] },
  };
  const out = proxyRoundtrip(resp);
  const text = out.result.content[0].text;
  assert.doesNotMatch(text, /\bthe\b/i, `expected 'the' stripped, got: ${text}`);
  assert.doesNotMatch(text, /basically/i);
  assert.match(text, /database/i);
  assert.match(text, /account/i);
  assert.ok(text.length < resp.result.content[0].text.length, 'should shrink');
});

test('proxy passes structured (JSON) tool-result text through unchanged', () => {
  const payload = '{"temp": 72, "unit": "F", "city": "the springs", "ok": true}';
  const resp = {
    jsonrpc: '2.0', id: 2,
    result: { content: [{ type: 'text', text: payload }] },
  };
  const out = proxyRoundtrip(resp);
  assert.strictEqual(out.result.content[0].text, payload, 'JSON must be byte-identical');
});

test('proxy leaves non-text content (image) untouched', () => {
  const resp = {
    jsonrpc: '2.0', id: 3,
    result: { content: [{ type: 'image', data: 'BASE64', mimeType: 'image/png' }] },
  };
  const out = proxyRoundtrip(resp);
  assert.deepStrictEqual(out.result.content[0], resp.result.content[0]);
});

test('proxy preserves paths/code inside compressed tool-result prose', () => {
  const resp = {
    jsonrpc: '2.0', id: 4,
    result: { content: [{ type: 'text',
      text: 'The config file lives at /etc/app/the.conf and the ' +
            '`parseConfig()` function will read it on startup.' }] },
  };
  const out = proxyRoundtrip(resp);
  const text = out.result.content[0].text;
  assert.match(text, /\/etc\/app\/the\.conf/, 'path must survive');
  assert.match(text, /`parseConfig\(\)`/, 'inline code must survive');
});

test('CAVEMAN_SHRINK_RESULTS=0 disables tool-result compression', () => {
  const original = 'The handler will basically just connect to the database here for sure.';
  const resp = {
    jsonrpc: '2.0', id: 5,
    result: { content: [{ type: 'text', text: original }] },
  };
  const out = proxyRoundtrip(resp, { CAVEMAN_SHRINK_RESULTS: '0' });
  assert.strictEqual(out.result.content[0].text, original, 'must be untouched when disabled');
});

test('proxy compresses NESTED inputSchema param descriptions on tools/list', () => {
  // Regression: transformResponse used to gate the nested walk on "nothing
  // matched at top level", so a tool's param descriptions (the bulk of a large
  // schema, sent every tools/list) were never compressed.
  const resp = {
    jsonrpc: '2.0', id: 6,
    result: { tools: [{
      name: 'search',
      description: 'Search the database for records that match the query.',
      inputSchema: { type: 'object', properties: {
        query: { type: 'string',
          description: 'The query string that you would like to search for in the index.' },
        limit: { type: 'number',
          description: 'The maximum number of results that will be returned to the caller.' },
      } },
    }] },
  };
  const before = resp.result.tools[0].inputSchema.properties.query.description;
  const out = proxyRoundtrip(resp);
  const props = out.result.tools[0].inputSchema.properties;
  assert.ok(props.query.description.length < before.length,
    `nested param description should shrink, got: ${props.query.description}`);
  assert.doesNotMatch(props.query.description, /\bthe\b/i, 'articles stripped in nested desc');
  assert.doesNotMatch(props.limit.description, /\bthe\b/i);
  assert.match(out.result.tools[0].description, /database/i, 'top-level desc still compressed');
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
