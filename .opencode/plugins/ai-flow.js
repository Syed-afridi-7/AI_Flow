/**
 * AI_Flow OpenCode Plugin
 * Exposes AI_Flow metadata and registers all 30 standardized Agentic Skills.
 */

const fs = require('fs');
const path = require('path');

const plugin = {
  name: 'ai-flow',
  version: '1.0.0',
  description: 'Production-grade framework of 30 standardized Agentic Skills and 60 dual-agent personas with from-scratch pure Python Hybrid Neuro-Symbolic AI engine.',
  author: 'Syed Afridi',
  homepage: 'https://github.com/Syed-afridi-7/AI_Flow',
  repository: 'https://github.com/Syed-afridi-7/AI_Flow',
  skillsPath: path.resolve(__dirname, '../../skills'),

  /**
   * Returns list of available skills and their metadata.
   */
  getSkills() {
    let resolvedPath = this.skillsPath;
    if (!fs.existsSync(resolvedPath)) {
      const adjacentSkills = path.resolve(__dirname, '../skills');
      if (fs.existsSync(adjacentSkills)) {
        resolvedPath = adjacentSkills;
      }
    }
    if (!fs.existsSync(resolvedPath)) {
      return [];
    }
    return fs.readdirSync(resolvedPath, { withFileTypes: true })
      .filter((dirent) => dirent.isDirectory() || dirent.isSymbolicLink())
      .map((dirent) => ({
        name: dirent.name,
        path: path.join(resolvedPath, dirent.name),
        skillFile: path.join(resolvedPath, dirent.name, 'SKILL.md'),
      }));
  },

  /**
   * OpenCode plugin lifecycle hook
   */
  async activate(context) {
    const skills = this.getSkills();
    if (context && typeof context.registerSkill === 'function') {
      for (const skill of skills) {
        context.registerSkill(skill);
      }
    }
    return {
      name: this.name,
      skillsCount: skills.length,
    };
  },
};

module.exports = plugin;
module.exports.default = plugin;
