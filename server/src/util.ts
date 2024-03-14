import dayjs from "dayjs";

export function buildProcessCustomId(processName: string, componentName: string) {
  return `process#${processName}#${componentName}`;
}

export function buildGlobalCustomId(scope: string, componentName: string) {
  return `global#${scope}#${componentName}`;
}

export const formatKeywordsForDisplay = (keywords: string[] | undefined | null) => {
  if (!keywords) {
    return "`[]`";
  } else {
    return `\`[${keywords.join(", ")}]\``;
  }
};

export const truncateEllipses = (str: string, length: number) => {
  if (str.length > length) {
    return str.substring(0, Math.max(length - 3, 0)) + "...";
  } else {
    return str;
  }
};

export const parseDatetimeString = (input: string): Date | null => {
  const ret = dayjs.utc(input, "YYYY-MM-DD HH:mm", true);
  return ret.isValid() ? ret.toDate() : null;
};

export const displayDatetimeString = (input: Date): string => {
  return dayjs.utc(input).format("YYYY-MM-DD HH:mm");
};
