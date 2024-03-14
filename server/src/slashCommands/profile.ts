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
import { SlashCommand } from "../types";

const handleProfile = async (interaction: ChatInputCommandInteraction, mode: "active" | "all") => {
  const contest = await getActiveContest();
  if (!contest) {
    return await interaction.reply({
      ephemeral: true,
      content: "No active contest.",
    });
  }

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
  await interaction.reply({
    ephemeral: true,
    content: channelMention(headerMsg.channelId),
  });
};

const command: SlashCommand = {
  command: new SlashCommandBuilder()
    .setName("profile")
    .setDescription("View profile for current contest.")
    .addSubcommand((subcommad) =>
      subcommad
        .setName("active")
        .setDescription("Include only active characters.")
        .addUserOption((option) =>
          option.setName("target").setDescription("User to get profile for.").setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("all")
        .setDescription("Include all characters (active and non-active).")
        .addUserOption((option) =>
          option.setName("target").setDescription("User to get profile for.").setRequired(true)
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
