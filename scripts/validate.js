#!/usr/bin/env node

/**
 * AI_Flow Skill Validator
 * Validates all skills in the skills/ directory against the Agent Skills Open Specification (agentskills.io).
 */

const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const skillsDir = path.join(repoRoot, 'skills');

if (!fs.existsSync(skillsDir)) {
  console.error(`Error: skills directory not found at ${skillsDir}`);
  process.exit(1);
}

const entries = fs.readdirSync(skillsDir, { withFileTypes: true });
const skillDirs = entries.filter((e) => e.isDirectory()).map((e) => e.name);

let errors = [];
let passedCount = 0;

console.log(`\x1b[36mValidating ${skillDirs.length} skills against the Agent Skills specification...\x1b[0m\n`);

for (const dirName of skillDirs) {
  const skillPath = path.join(skillsDir, dirName, 'SKILL.md');

  if (!fs.existsSync(skillPath)) {
    errors.push(`[${dirName}] Missing SKILL.md file.`);
    continue;
  }

  const content = fs.readFileSync(skillPath, 'utf8');
  const frontmatterMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);

  if (!frontmatterMatch) {
    errors.push(`[${dirName}] Missing or malformed YAML frontmatter (must be enclosed in '---').`);
    continue;
  }

  const frontmatter = frontmatterMatch[1];
  const body = frontmatterMatch[2];

  // Validate Name
  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  if (!nameMatch) {
    errors.push(`[${dirName}] Missing 'name' field in frontmatter.`);
  } else {
    const name = nameMatch[1].trim();
    if (name !== dirName) {
      errors.push(`[${dirName}] Frontmatter name '${name}' does not match directory name '${dirName}'.`);
    }
    if (!/^[a-z0-9-]+$/.test(name)) {
      errors.push(`[${dirName}] Skill name '${name}' contains invalid characters (use only lowercase letters, numbers, and hyphens).`);
    }
  }

  // Validate Description
  const descMatch = frontmatter.match(/^description:\s*([\s\S]*?)(?=\n[a-z0-9_-]+:|$)/m);
  if (!descMatch) {
    errors.push(`[${dirName}] Missing 'description' field in frontmatter.`);
  } else {
    const desc = descMatch[1].replace(/\r?\n\s*/g, ' ').trim();
    if (!/^Use when\b/i.test(desc)) {
      errors.push(`[${dirName}] Description must start with 'Use when...'. Got: "${desc.substring(0, 40)}..."`);
    }
    if (desc.length > 500) {
      errors.push(`[${dirName}] Description exceeds 500 characters (${desc.length} chars).`);
    }
  }

  // Validate Required Sections
  if (!/##\s+Overview/i.test(body)) {
    errors.push(`[${dirName}] Missing '## Overview' section in body.`);
  }
  if (!/##\s+When to Use/i.test(body)) {
    errors.push(`[${dirName}] Missing '## When to Use' section in body.`);
  }
  if (!/##\s+(Instructions|The Two-Phase Contract)/i.test(body)) {
    errors.push(`[${dirName}] Missing '## Instructions' or '## The Two-Phase Contract' section in body.`);
  }

  if (!errors.some((err) => err.startsWith(`[${dirName}]`))) {
    passedCount++;
    console.log(`  \x1b[32m✓\x1b[0m ${dirName}`);
  }
}

console.log('');

if (errors.length > 0) {
  console.error(`\x1b[31mValidation failed with ${errors.length} error(s):\x1b[0m`);
  for (const err of errors) {
    console.error(`  \x1b[31m✖\x1b[0m ${err}`);
  }
  process.exit(1);
} else {
  console.log(`\x1b[32mAll ${passedCount} skills passed validation successfully!\x1b[0m`);
}

