import { Character } from "@prisma/client";
import { ColorResolvable, EmbedBuilder, userMention } from "discord.js";
import { Points, PointsManager } from "../pointsManager";
import { Settings } from "../settings";
import { formatKeywordsForDisplay, formatPointsForDisplay, truncateEllipses } from "../util";

export const buildSubmissionEmbed = (
  color: ColorResolvable,
  submissionId: number | null,
  data: {
    userId: string;
    character: Character | undefined;
    acceptedKeywords: string[];
    pointsAdded: Points | undefined;
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
      { name: "Points Added", value: formatPointsForDisplay(data.pointsAdded), inline: true },
      { name: "Proof", value: data.imageUrl, inline: true }
    )
    .setImage(data.imageUrl ?? null)
    .setFooter(submissionId ? { text: submissionId.toString() } : null);
  return embed;
};

export const buildCharacterEmbed = (
  color: ColorResolvable,
  keywordsDisplayMode: "truncate" | "all",
  character: Character
): EmbedBuilder => {
  const embed = new EmbedBuilder()
    .setTitle(`Character (ID: ${character.id})`)
    .setColor(color)
    .addFields(
      {
        name: "Character",
        value: `${userMention(character.userId)}'s ${character.rotmgClass}`,
        inline: true,
      },
      { name: "Modifiers", value: formatKeywordsForDisplay(character.modifiers), inline: true },
      {
        name: "Active?",
        value: character.isActive
          ? Settings.getInstance().getGeneralEmoji("accept")
          : Settings.getInstance().getGeneralEmoji("reject"),
        inline: true,
      },
      {
        name: "Points",
        value: formatPointsForDisplay(
          PointsManager.getInstance().getPointsForAll(
            character.keywords,
            character.rotmgClass,
            character.modifiers
          )
        ),
        inline: true,
      }
    );

  if (character.keywords.length > 0) {
    if (keywordsDisplayMode === "truncate") {
      const keywordsStr = truncateEllipses(formatKeywordsForDisplay(character.keywords), 800);
      embed.addFields({
        name: "Items/Achievements",
        value: `${keywordsStr}

        To view all keywords, use \`/character ${character.id}\`.
        `,
      });
    } else {
      let currStrLength = 0; // approximate
      const keywordsSplit: string[][] = [[]];
      for (const kw of character.keywords) {
        if (currStrLength + kw.length + 3 >= 800) {
          keywordsSplit.push([]);
        }
        keywordsSplit[keywordsSplit.length - 1].push(kw);
        currStrLength += kw.length + 3;
      }
      for (let i = 0; i < keywordsSplit.length; i++) {
        const name = i === 0 ? "Items/Achievements" : "More Items/Achievements";
        embed.addFields({ name, value: formatKeywordsForDisplay(keywordsSplit[i]) });
      }
    }
  }

  return embed;
};
