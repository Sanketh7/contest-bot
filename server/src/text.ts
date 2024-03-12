export const formatKeywordsForDisplay = (keywords: string[] | undefined | null) => {
  if (!keywords) {
    return "`[]`";
  } else {
    return `\`[${keywords.join(", ")}]\``;
  }
};
