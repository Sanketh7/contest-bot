"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildProcessCustomId = void 0;
function buildProcessCustomId(processName, componentName) {
  return `process#${processName}#${componentName}`;
}
exports.buildProcessCustomId = buildProcessCustomId;
