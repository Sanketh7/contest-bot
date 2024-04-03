import {
  CacheType,
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  messageLink,
} from "discord.js";
import { AddRemoveKeywordsProcess } from "../processes/addRemoveKeywords";
import { getCharacter } from "../services/characterService";
import { SlashCommand, SlashCommandDescriptions } from "../types";

const descriptions = {
  description: "Manage a character's keywords.",
  subcommands: {
    add: {
      description: "Add keywords to a character.",
      options: {
        characterId: "Character ID",
      },
    },
    remove: {
      description: "Remove keywords from a character.",
      options: {
        characterId: "Character ID",
      },
    },
  },
} satisfies SlashCommandDescriptions;

const handleKeywordsAddRemove = async (
  interaction: ChatInputCommandInteraction,
  action: "add" | "remove"
) => {
  const characterId = interaction.options.getNumber("character-id", true);
  const character = await getCharacter(characterId);
  if (!character) {
    return await interaction.reply({
      content: "Character not found.",
    });
  }

  const message = await interaction.user.send({
    content: "Loading...",
  });
  await interaction.reply({
    content: messageLink(message.channel.id, message.id),
  });
  const process = new AddRemoveKeywordsProcess(interaction.user, message, character, action);
  return await process.start();
};

const command: SlashCommand = {
  defaultAcl: ["Admin"],
  subcommandAcl: {
    add: ["Contest Staff"],
    remove: ["Contest Staff"],
  },
  descriptions,
  command: new SlashCommandBuilder()
    .setName("keywords")
    .setDescription(descriptions.description)
    .addSubcommand((subcommand) =>
      subcommand
        .setName("add")
        .setDescription(descriptions.subcommands.add.description)
        .addNumberOption((option) =>
          option
            .setName("character-id")
            .setDescription(descriptions.subcommands.add.options.characterId)
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("remove")
        .setDescription(descriptions.subcommands.remove.description)
        .addNumberOption((option) =>
          option
            .setName("character-id")
            .setDescription(descriptions.subcommands.remove.options.characterId)
            .setRequired(true)
        )
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "add":
        return await handleKeywordsAddRemove(interaction, "add");
      case "remove":
        return await handleKeywordsAddRemove(interaction, "remove");
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
