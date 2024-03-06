export function buildProcessCustomId(processName: string, componentName: string) {
  return `process#${processName}#${componentName}`;
}
