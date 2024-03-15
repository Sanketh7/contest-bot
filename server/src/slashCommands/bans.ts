import {
  CacheType,
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  userMention,
} from "discord.js";
import { getBanList, updateBanList } from "../services/guildService";
import { Settings } from "../settings";
import { SlashCommand } from "../types";

const handleBansAddRemove = async (
  interaction: ChatInputCommandInteraction,
  action: "ban" | "unban"
) => {
  const user = interaction.options.getUser("target", true);
  const guild = Settings.getInstance().get("guild");
  await updateBanList(guild, action, user);

  if (action === "ban") {
    try {
      const member = await guild.members.fetch(user.id);
      await member.roles.remove(Settings.getInstance().getRole("contestant"));
    } catch (err) {
      console.error("failed to remove contestant role", err);
    }
  }

  return await interaction.reply({
    content: `${action === "ban" ? "Banned" : "Unbanned"} ${userMention(user.id)} from contests.`,
  });
};

const handleBansView = async (interaction: ChatInputCommandInteraction) => {
  const bans = await getBanList(Settings.getInstance().get("guild"));
  return await interaction.reply({
    content:
      bans.length === 0 ? "No banned users." : bans.map((userId) => userMention(userId)).join(", "),
  });
};

const command: SlashCommand = {
  defaultAcl: ["Admin"],
  subcommandAcl: {
    add: ["Admin"],
    remove: ["Admin"],
    view: ["Contest Staff"],
  },
  command: new SlashCommandBuilder()
    .setName("bans")
    .setDescription("Manage contest bans.")
    .addSubcommand((subcommand) =>
      subcommand
        .setName("add")
        .setDescription("Ban a user.")
        .addUserOption((option) =>
          option.setName("target").setDescription("User to ban.").setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("remove")
        .setDescription("Unban a user.")
        .addUserOption((option) =>
          option.setName("target").setDescription("User to unban.").setRequired(true)
        )
    )
    .addSubcommand((subcommand) => subcommand.setName("view").setDescription("View all bans.")),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "add":
        return await handleBansAddRemove(interaction, "ban");
      case "remove":
        return await handleBansAddRemove(interaction, "unban");
      case "view":
        return await handleBansView(interaction);
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
