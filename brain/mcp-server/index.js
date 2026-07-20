#!/usr/bin/env node
// XC Brain MCP Server — stdio JSON-RPC, no external deps required
// Run: node index.js
// Then add as MCP connector in claude.ai Settings → Connectors

import { createInterface } from 'readline';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dir = dirname(fileURLToPath(import.meta.url));
const DATA = join(__dir, '../data');
['notes', 'journals'].forEach(d => mkdirSync(join(DATA, d), { recursive: true }));

function rj(file, def = []) {
  const p = join(DATA, file);
  if (!existsSync(p)) return def;
  try { return JSON.parse(readFileSync(p, 'utf8')); } catch { return def; }
}
function wj(file, data) { writeFileSync(join(DATA, file), JSON.stringify(data, null, 2)); }

// ── TOOL DEFINITIONS ──
const TOOLS = [
  {
    name: 'brain_capture',
    description: 'Capture a thought, idea, task, or resource into the Second Brain inbox',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Content to capture' },
        type: { type: 'string', enum: ['idea', 'task', 'resource', 'bug', 'script', 'vuln', 'quote'], default: 'idea' },
        tag: { type: 'string', description: 'Optional tag' },
      },
      required: ['text'],
    },
  },
  {
    name: 'brain_get_captures',
    description: 'Get items from the capture inbox',
    inputSchema: {
      type: 'object',
      properties: {
        processed: { type: 'boolean' },
        type: { type: 'string' },
        limit: { type: 'number', default: 20 },
      },
    },
  },
  {
    name: 'brain_create_task',
    description: 'Create a new task in the kanban board',
    inputSchema: {
      type: 'object',
      properties: {
        title: { type: 'string' },
        desc: { type: 'string', default: '' },
        priority: { type: 'string', enum: ['high', 'med', 'low'], default: 'med' },
        col: { type: 'string', enum: ['todo', 'doing', 'review', 'done'], default: 'todo' },
      },
      required: ['title'],
    },
  },
  {
    name: 'brain_get_tasks',
    description: 'Get tasks from the kanban board',
    inputSchema: {
      type: 'object',
      properties: {
        col: { type: 'string', enum: ['todo', 'doing', 'review', 'done', 'all'], default: 'all' },
        priority: { type: 'string', enum: ['high', 'med', 'low', 'all'], default: 'all' },
      },
    },
  },
  {
    name: 'brain_update_task',
    description: 'Update a task — move column, change priority, edit title/desc',
    inputSchema: {
      type: 'object',
      properties: {
        id: { type: 'number' },
        col: { type: 'string', enum: ['todo', 'doing', 'review', 'done'] },
        priority: { type: 'string', enum: ['high', 'med', 'low'] },
        title: { type: 'string' },
        desc: { type: 'string' },
      },
      required: ['id'],
    },
  },
  {
    name: 'brain_write_note',
    description: 'Write or update a note. Omit id to create new.',
    inputSchema: {
      type: 'object',
      properties: {
        title: { type: 'string' },
        content: { type: 'string', description: 'Markdown content' },
        id: { type: 'number', description: 'Note ID to update (omit = create new)' },
        tags: { type: 'array', items: { type: 'string' } },
      },
      required: ['title', 'content'],
    },
  },
  {
    name: 'brain_get_notes',
    description: 'List notes, optionally filtered by search keyword',
    inputSchema: {
      type: 'object',
      properties: {
        search: { type: 'string' },
        limit: { type: 'number', default: 20 },
      },
    },
  },
  {
    name: 'brain_log_vuln',
    description: 'Log a bug bounty vulnerability finding',
    inputSchema: {
      type: 'object',
      properties: {
        title: { type: 'string' },
        target: { type: 'string' },
        severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
        desc: { type: 'string' },
        status: { type: 'string', default: 'New' },
        cvss: { type: 'number' },
      },
      required: ['title', 'target', 'severity', 'desc'],
    },
  },
  {
    name: 'brain_get_vulns',
    description: 'Get bug bounty findings, optionally filtered by severity',
    inputSchema: {
      type: 'object',
      properties: {
        severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low', 'all'], default: 'all' },
        status: { type: 'string' },
      },
    },
  },
  {
    name: 'brain_save_journal',
    description: 'Save a daily journal entry',
    inputSchema: {
      type: 'object',
      properties: {
        date: { type: 'string', description: 'YYYY-MM-DD' },
        priorities: { type: 'string' },
        braindump: { type: 'string' },
        achieved: { type: 'string' },
        learned: { type: 'string' },
        reflection: { type: 'string' },
        mood: { type: 'number', minimum: 1, maximum: 5 },
      },
      required: ['date'],
    },
  },
  {
    name: 'brain_get_stats',
    description: 'Get Second Brain overview statistics',
    inputSchema: { type: 'object', properties: {} },
  },
  {
    name: 'brain_search',
    description: 'Search across all brain data — notes, captures, tasks, vulns',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string' },
        sources: { type: 'array', items: { type: 'string', enum: ['notes', 'captures', 'tasks', 'vulns'] } },
      },
      required: ['query'],
    },
  },
];

// ── HANDLERS ──
const H = {
  brain_capture({ text, type = 'idea', tag = '' }) {
    const list = rj('captures.json');
    const item = { id: Date.now(), text, type, tag, date: new Date().toISOString(), processed: false };
    list.push(item);
    wj('captures.json', list);
    return { success: true, id: item.id, message: `Captured: "${text.substring(0, 60)}"` };
  },

  brain_get_captures({ processed, type, limit = 20 } = {}) {
    let list = rj('captures.json');
    if (processed !== undefined) list = list.filter(c => c.processed === processed);
    if (type) list = list.filter(c => c.type === type);
    return { captures: list.slice(-limit).reverse(), total: list.length };
  },

  brain_create_task({ title, desc = '', priority = 'med', col = 'todo' }) {
    const tasks = rj('tasks.json');
    const task = { id: Date.now(), title, desc, priority, col, date: new Date().toISOString() };
    tasks.push(task);
    wj('tasks.json', tasks);
    return { success: true, id: task.id, task };
  },

  brain_get_tasks({ col = 'all', priority = 'all' } = {}) {
    let tasks = rj('tasks.json');
    if (col !== 'all') tasks = tasks.filter(t => t.col === col);
    if (priority !== 'all') tasks = tasks.filter(t => t.priority === priority);
    return { tasks, count: tasks.length };
  },

  brain_update_task({ id, col, priority, title, desc }) {
    const tasks = rj('tasks.json');
    const idx = tasks.findIndex(t => t.id === id);
    if (idx === -1) return { success: false, message: 'Task not found' };
    if (col !== undefined) tasks[idx].col = col;
    if (priority !== undefined) tasks[idx].priority = priority;
    if (title !== undefined) tasks[idx].title = title;
    if (desc !== undefined) tasks[idx].desc = desc;
    wj('tasks.json', tasks);
    return { success: true, task: tasks[idx] };
  },

  brain_write_note({ title, content, id, tags = [] }) {
    const notes = rj('notes.json');
    if (id) {
      const idx = notes.findIndex(n => n.id === id);
      if (idx >= 0) {
        notes[idx] = { ...notes[idx], title, content, tags, updated: new Date().toISOString() };
        wj('notes.json', notes);
        return { success: true, id };
      }
    }
    const note = { id: Date.now(), title, content, tags, created: new Date().toISOString(), updated: new Date().toISOString() };
    notes.unshift(note);
    wj('notes.json', notes);
    return { success: true, id: note.id };
  },

  brain_get_notes({ search, limit = 20 } = {}) {
    let notes = rj('notes.json');
    if (search) {
      const q = search.toLowerCase();
      notes = notes.filter(n => n.title?.toLowerCase().includes(q) || n.content?.toLowerCase().includes(q));
    }
    return {
      notes: notes.slice(0, limit).map(n => ({
        id: n.id, title: n.title, preview: n.content?.substring(0, 100), tags: n.tags, updated: n.updated,
      })),
      total: notes.length,
    };
  },

  brain_log_vuln({ title, target, severity, desc, status = 'New', cvss }) {
    const vulns = rj('vulns.json');
    const v = { id: Date.now(), title, target, severity, desc, status, cvss, date: new Date().toISOString() };
    vulns.push(v);
    wj('vulns.json', vulns);
    return { success: true, id: v.id };
  },

  brain_get_vulns({ severity = 'all', status } = {}) {
    let vulns = rj('vulns.json');
    if (severity !== 'all') vulns = vulns.filter(v => v.severity === severity);
    if (status) vulns = vulns.filter(v => v.status === status);
    return { vulns, count: vulns.length };
  },

  brain_save_journal({ date, priorities, braindump, achieved, learned, reflection, mood }) {
    const journals = rj('journals.json');
    const entry = { date, priorities, braindump, achieved, learned, reflection, mood, updated: new Date().toISOString() };
    const idx = journals.findIndex(j => j.date === date);
    if (idx >= 0) journals[idx] = entry; else journals.push(entry);
    wj('journals.json', journals);
    return { success: true, date };
  },

  brain_get_stats() {
    const captures = rj('captures.json');
    const tasks = rj('tasks.json');
    const notes = rj('notes.json');
    const vulns = rj('vulns.json');
    const journals = rj('journals.json');
    return {
      captures: { total: captures.length, unprocessed: captures.filter(c => !c.processed).length },
      tasks: {
        total: tasks.length,
        open: tasks.filter(t => t.col !== 'done').length,
        by_col: { todo: tasks.filter(t => t.col === 'todo').length, doing: tasks.filter(t => t.col === 'doing').length, review: tasks.filter(t => t.col === 'review').length, done: tasks.filter(t => t.col === 'done').length },
      },
      notes: { total: notes.length },
      vulns: {
        total: vulns.length,
        by_sev: { critical: vulns.filter(v => v.severity === 'critical').length, high: vulns.filter(v => v.severity === 'high').length, medium: vulns.filter(v => v.severity === 'medium').length, low: vulns.filter(v => v.severity === 'low').length },
      },
      journals: { total: journals.length, latest: journals.at(-1)?.date },
    };
  },

  brain_search({ query, sources = ['notes', 'captures', 'tasks', 'vulns'] }) {
    const q = query.toLowerCase();
    const results = [];
    if (sources.includes('notes')) {
      rj('notes.json').filter(n => n.title?.toLowerCase().includes(q) || n.content?.toLowerCase().includes(q))
        .forEach(n => results.push({ source: 'note', id: n.id, title: n.title, preview: n.content?.substring(0, 100) }));
    }
    if (sources.includes('captures')) {
      rj('captures.json').filter(c => c.text?.toLowerCase().includes(q))
        .forEach(c => results.push({ source: 'capture', id: c.id, title: c.text.substring(0, 60), type: c.type }));
    }
    if (sources.includes('tasks')) {
      rj('tasks.json').filter(t => t.title?.toLowerCase().includes(q) || t.desc?.toLowerCase().includes(q))
        .forEach(t => results.push({ source: 'task', id: t.id, title: t.title, col: t.col }));
    }
    if (sources.includes('vulns')) {
      rj('vulns.json').filter(v => v.title?.toLowerCase().includes(q) || v.desc?.toLowerCase().includes(q))
        .forEach(v => results.push({ source: 'vuln', id: v.id, title: v.title, severity: v.severity }));
    }
    return { results, count: results.length, query };
  },
};

// ── STDIO JSON-RPC ──
const rl = createInterface({ input: process.stdin, terminal: false });
const send = obj => process.stdout.write(JSON.stringify(obj) + '\n');

rl.on('line', line => {
  let req;
  try { req = JSON.parse(line.trim()); } catch { return; }
  const { id, method, params } = req;

  if (method === 'initialize') {
    send({ jsonrpc: '2.0', id, result: { protocolVersion: '2024-11-05', capabilities: { tools: {} }, serverInfo: { name: 'xcbrain', version: '1.0.0', description: 'XC Second Brain MCP Server' } } });
  } else if (method === 'notifications/initialized') {
    // no-op
  } else if (method === 'tools/list') {
    send({ jsonrpc: '2.0', id, result: { tools: TOOLS } });
  } else if (method === 'tools/call') {
    const { name, arguments: args } = params;
    const handler = H[name];
    if (!handler) { send({ jsonrpc: '2.0', id, error: { code: -32601, message: `Unknown tool: ${name}` } }); return; }
    try {
      const result = handler(args || {});
      send({ jsonrpc: '2.0', id, result: { content: [{ type: 'text', text: JSON.stringify(result) }] } });
    } catch (err) {
      send({ jsonrpc: '2.0', id, result: { content: [{ type: 'text', text: JSON.stringify({ error: err.message }) }], isError: true } });
    }
  } else if (method === 'ping') {
    send({ jsonrpc: '2.0', id, result: {} });
  } else {
    send({ jsonrpc: '2.0', id, error: { code: -32601, message: `Method not found: ${method}` } });
  }
});

process.stderr.write('XC Brain MCP Server started — listening on stdio\n');
