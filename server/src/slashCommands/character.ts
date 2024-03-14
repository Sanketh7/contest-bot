import {
  CacheType,
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  User,
  channelMention,
  userMention,
} from "discord.js";
import { buildCharacterEmbed } from "../processes/common";
import { getCharactersByUserId } from "../services/characterService";
import { getActiveContest } from "../services/contestService";
import { SlashCommand } from "../types";

const handleProfile = async (interaction: ChatInputCommandInteraction, user: User) => {
  const contest = await getActiveContest();
  if (!contest) {
    return await interaction.reply({
      ephemeral: true,
      content: "No active contest.",
    });
  }

  const characters = await getCharactersByUserId(user.id, contest);
  const headerMsg = await interaction.user.send({
    content: `${userMention(user.id)}'s Characters:`,
  });
  for (const c of characters) {
    await headerMsg.reply({
      embeds: [buildCharacterEmbed("Blue", "truncate", c)],
    });
  }
  await interaction.reply({
    ephemeral: true,
    content: channelMention(headerMsg.channelId),
  });
};

const command: SlashCommand = {
  defaultAcl: ["Admin"],
  subcommandAcl: null,
  command: new SlashCommandBuilder()
    .setName("character")
    .setDescription("View profile for current contest.")
    .addSubcommand((subcommad) => subcommad.setName("me").setDescription("Get my profile."))
    .addSubcommand((subcommand) =>
      subcommand
        .setName("other")
        .setDescription("Get the profile for someone else.")
        .addUserOption((option) =>
          option.setName("target").setDescription("User to get profile for.").setRequired(true)
        )
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "me":
        return await handleProfile(interaction, interaction.user);
      case "other":
        const user = interaction.options.getUser("target", true);
        return await handleProfile(interaction, user);
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
