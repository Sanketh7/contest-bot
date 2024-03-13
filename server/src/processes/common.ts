import { Character } from "@prisma/client";
import { ColorResolvable, EmbedBuilder, userMention } from "discord.js";
import { formatKeywordsForDisplay } from "../util";

export const buildSubmissionEmbed = (
  color: ColorResolvable,
  submissionId: number | null,
  data: {
    userId: string;
    character: Character | undefined;
    acceptedKeywords: string[];
    pointsAdded: number;
    imageUrl: string;
  }
): EmbedBuilder => {
  const embed = new EmbedBuilder()
    .setTitle("Submission" + (submissionId ? ` (ID: ${submissionId})` : ""))
    .setColor(color)
    .addFields(
      {
        name: "Character",
        value: `${userMention(data.userId)}'s ${data.character?.rotmgClass}`,
        inline: true,
      },
      {
        name: "Modifiers",
        value: formatKeywordsForDisplay(data.character?.modifiers),
        inline: true,
      },
      {
        name: "Items/Achievements",
        value: formatKeywordsForDisplay(data.acceptedKeywords),
      },
      { name: "Points Added", value: (data.pointsAdded ?? 0).toString(), inline: true },
      { name: "Proof", value: data.imageUrl, inline: true }
    )
    .setImage(data.imageUrl ?? null)
    .setFooter(submissionId ? { text: submissionId.toString() } : null);
  return embed;
};
