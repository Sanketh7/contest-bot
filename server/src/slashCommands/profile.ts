import {
  CacheType,
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  channelMention,
  userMention,
} from "discord.js";
import { buildCharacterEmbed } from "../processes/common";
import { getActiveCharacterByUserId, getCharactersByUserId } from "../services/characterService";
import { getActiveContest } from "../services/contestService";
import { SlashCommand, SlashCommandDescriptions } from "../types";

const descriptions = {
  description: "View profile for current contest.",
  subcommands: {
    active: {
      description: "Include only active characters.",
      options: {
        target: "User to get profile for.",
      },
    },
    all: {
      description: "Include all characters (active and non-active).",
      options: {
        target: "User to get profile for.",
      },
    },
  },
} satisfies SlashCommandDescriptions;

const handleProfile = async (interaction: ChatInputCommandInteraction, mode: "active" | "all") => {
  const contest = await getActiveContest();
  if (!contest) {
    return await interaction.reply({
      ephemeral: true,
      content: "No active contest.",
    });
  }

  await interaction.deferReply({ephemeral: true});
  const user = interaction.options.getUser("target", true);
  const characters =
    mode === "all"
      ? await getCharactersByUserId(user.id, contest)
      : [await getActiveCharacterByUserId(user.id, contest)];
  const headerMsg = await interaction.user.send({
    content: `${userMention(user.id)}'s ${mode === "active" ? "Active " : ""}Characters:`,
  });
  for (const c of characters) {
    if (c) {
      await headerMsg.reply({
        embeds: [buildCharacterEmbed("Blue", "truncate", c)],
      });
    }
  }
  await interaction.editReply({
    content: channelMention(headerMsg.channelId),
  });
};

const command: SlashCommand = {
  defaultAcl: ["Contestant"],
  subcommandAcl: {
    active: ["Contestant"],
    all: ["Contestant"],
  },
  descriptions,
  command: new SlashCommandBuilder()
    .setName("profile")
    .setDescription(descriptions.description)
    .addSubcommand((subcommad) =>
      subcommad
        .setName("active")
        .setDescription(descriptions.subcommands.active.description)
        .addUserOption((option) =>
          option
            .setName("target")
            .setDescription(descriptions.subcommands.active.options.target)
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("all")
        .setDescription(descriptions.subcommands.all.description)
        .addUserOption((option) =>
          option
            .setName("target")
            .setDescription(descriptions.subcommands.all.options.target)
            .setRequired(true)
        )
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "active":
        return await handleProfile(interaction, "active");
      case "all":
        return await handleProfile(interaction, "all");
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
