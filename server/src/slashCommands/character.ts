import {
  CacheType,
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  channelLink,
  hideLinkEmbed,
  hyperlink,
} from "discord.js";
import { PointsManager } from "../pointsManager";
import { buildCharacterEmbed } from "../processes/common";
import { getCharacter } from "../services/characterService";
import { getSubmissionsForCharacter } from "../services/submissionService";
import { SlashCommand, SlashCommandDescriptions } from "../types";
import { formatKeywordsForDisplay, formatPointsForDisplay } from "../util";

const descriptions = {
  description: "Character info.",
  subcommands: {
    view: {
      description: "View full character info.",
      options: {
        characterId: "Character ID.",
      },
    },
    submissions: {
      description: "View character submissions.",
      options: {
        characterId: "Character ID.",
        last: "Last X character submissions."
      }
    },
    allSubmissions: {
      description: "View all character submissions.",
      options: {
        characterId: "Character ID."
      },
    },
  },
} satisfies SlashCommandDescriptions;

const handleCharacterView = async (interaction: ChatInputCommandInteraction) => {
  await interaction.deferReply();
  const characterId = interaction.options.getNumber("character-id", true);
  const character = await getCharacter(characterId);
  if (!character) {
    return await interaction.editReply({
      content: "Character not found.",
    });
  } else {
    return await interaction.editReply({
      embeds: [buildCharacterEmbed("Blue", "all", character)],
    });
  }
};

const handleCharacterSubmissions = async (interaction: ChatInputCommandInteraction, listAll: boolean) => {
  await interaction.deferReply({ ephemeral: true });
  const characterId = interaction.options.getNumber("character-id", true);
  const last = listAll ? undefined : interaction.options.getNumber("last", true);
  const character = await getCharacter(characterId);
  if (!character) {
    return await interaction.editReply({
      content: "Character not found.",
    });
  }
  const submissions = await getSubmissionsForCharacter(characterId, last);
  if (submissions.length === 0) {
    return await interaction.editReply({
      content: "No submissions.",
    });
  }

  const textParts = submissions.map((submission) => {
    const points = PointsManager.getInstance().getPointsForAll(
      submission.keywords,
      character.rotmgClass,
      character.modifiers
    );
    return (
      `**Submission ID: ${submission.id}**${submission.isAccepted ? " (Accepted)" : ""}\n` +
      `Keywords: ${formatKeywordsForDisplay(submission.keywords)}\n` +
      `Points: \`${formatPointsForDisplay(points)}\`\n` +
      `${hyperlink("Proof", hideLinkEmbed(submission.imageUrl))}`
    );
  });
  let textBuf = "";
  for (const part of textParts) {
    if (textBuf.length + part.length > 1800) {
      if (textBuf.length === 0) {
        await interaction.user.send({
          content: "Submission skipped (this should not happen).",
        });
        continue;
      }
      await interaction.user.send({
        content: textBuf,
      });
      textBuf = "";
    }
    textBuf += part + "\n\n";
  }
  if (textBuf.length > 0) {
    await interaction.user.send({
      content: textBuf,
    });
  }
  await interaction.editReply({
    content: interaction.user.dmChannel ? channelLink(interaction.user.dmChannel.id) : "Check DMs",
  });
};

const command: SlashCommand = {
  defaultAcl: ["Admin"],
  subcommandAcl: {
    view: ["Contestant"],
    submissions: ["Contestant"],
  },
  descriptions,
  command: new SlashCommandBuilder()
    .setName("character")
    .setDescription(descriptions.description)
    .addSubcommand((subcommand) =>
      subcommand
        .setName("view")
        .setDescription(descriptions.subcommands.view.description)
        .addNumberOption((option) =>
          option
            .setName("character-id")
            .setDescription(descriptions.subcommands.view.options.characterId)
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("submissions")
        .setDescription(descriptions.subcommands.submissions.description)
        .addNumberOption((option) =>
          option
            .setName("character-id")
            .setDescription(descriptions.subcommands.submissions.options.characterId)
            .setRequired(true)
        )
        .addNumberOption((option) =>
          option
            .setName("last")
            .setDescription(descriptions.subcommands.submissions.options.last)
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("all-submissions")
        .setDescription(descriptions.subcommands.allSubmissions.description)
        .addNumberOption((option) =>
          option
            .setName("character-id")
            .setDescription(descriptions.subcommands.allSubmissions.options.characterId)
            .setRequired(true)
        )
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "view":
        return await handleCharacterView(interaction);
      case "all-submissions":
        return await handleCharacterSubmissions(interaction, true);
      case "submissions":
        return await handleCharacterSubmissions(interaction, false);
      default:
        return await interaction.reply({
          ephemeral: true,
          content: "Invalid subcommand.",
        });
    }
  },
  cooldown: 10,
};

export default command;
