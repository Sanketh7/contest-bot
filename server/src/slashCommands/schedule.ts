import {
  CacheType,
  ChatInputCommandInteraction,
  EmbedBuilder,
  SlashCommandBuilder,
} from "discord.js";
import { table } from "table";
import {
  createContest,
  deleteContest,
  getContest,
  getContestsAfter,
  refreshContestSchedule,
} from "../services/contestService";
import { SlashCommand } from "../types";
import { displayDatetimeString, parseDatetimeString } from "../util";

const handleScheduleAdd = async (interaction: ChatInputCommandInteraction) => {
  const startInput = interaction.options.getString("start", true);
  const endInput = interaction.options.getString("end", true);

  const start = parseDatetimeString(startInput);
  const end = parseDatetimeString(endInput);
  if (!start) {
    return await interaction.reply({
      ephemeral: true,
      content: "Invalid format for start",
    });
  }
  if (!end) {
    return await interaction.reply({
      ephemeral: true,
      content: "Invalid format for end",
    });
  }

  const contest = await createContest({ startTime: start, endTime: end });
  const embed = new EmbedBuilder()
    .setTitle("Created Contest")
    .setColor("Green")
    .addFields(
      { name: "ID", value: contest.id.toString() },
      { name: "Start", value: displayDatetimeString(contest.startTime) },
      { name: "End", value: displayDatetimeString(contest.endTime) }
    );
  return await interaction.reply({
    embeds: [embed],
  });
};

const handleScheduleRemove = async (interaction: ChatInputCommandInteraction) => {
  const contestId = interaction.options.getNumber("contest-id", true);

  const contest = await getContest(contestId);
  if (!contest) {
    return await interaction.reply({
      ephemeral: true,
      content: "Contest does not exist.",
    });
  }
  if (contest.isActive) {
    return await interaction.reply({
      ephemeral: true,
      content: "Cannot delete an active contest.",
    });
  }

  await deleteContest(contest);
  const embed = new EmbedBuilder()
    .setTitle("Deleted Contest")
    .setColor("Red")
    .addFields(
      { name: "ID", value: contest.id.toString() },
      { name: "Start", value: displayDatetimeString(contest.startTime) },
      { name: "End", value: displayDatetimeString(contest.endTime) }
    );
  return await interaction.reply({
    embeds: [embed],
  });
};

const handleScheduleView = async (interaction: ChatInputCommandInteraction) => {
  const schedule = await getContestsAfter(new Date());
  if (schedule.length === 0) {
    return interaction.reply({
      content: "No upcoming contests.",
    });
  }
  const tableData: string[][] = [["ID", "Start", "End"]];
  for (const contest of schedule) {
    tableData.push([
      contest.id.toString(),
      displayDatetimeString(contest.startTime),
      displayDatetimeString(contest.endTime),
    ]);
  }
  const embed = new EmbedBuilder()
    .setTitle("Upcoming Contests")
    .setDescription("All times are in UTC.")
    .setColor("Blue")
    .addFields({ name: "Schedule", value: "```" + table(tableData) + "```" });
  return await interaction.reply({
    embeds: [embed],
  });
};

export const handleScheduleRefresh = async (interaction: ChatInputCommandInteraction) => {
  await refreshContestSchedule();
  return await interaction.reply({
    content: "Refreshed contest schedule.",
  });
};

const command: SlashCommand = {
  defaultAcl: ["Admin"],
  subcommandAcl: {
    add: ["Admin"],
    remove: ["Admin"],
    view: ["Contest Staff"],
    refresh: ["Contest Staff"],
  },
  command: new SlashCommandBuilder()
    .setName("schedule")
    .setDescription("Manage and view the contest schedule.")
    .addSubcommand((subcommand) =>
      subcommand
        .setName("add")
        .setDescription("Add a contest to the schedule.")
        .addStringOption((option) =>
          option
            .setName("start")
            .setDescription("Start of contest (UTC) in format: YYYY-MM-DD HH:mm")
            .setRequired(true)
        )
        .addStringOption((option) =>
          option
            .setName("end")
            .setDescription("End of contest (UTC) in format: YYYY-MM-DD HH:mm")
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("remove")
        .setDescription("Remove a contest from the schedule.")
        .addNumberOption((option) =>
          option.setName("contest-id").setDescription("Contest ID").setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand.setName("view").setDescription("View the upcoming contest schedule.")
    )
    .addSubcommand((subcommand) =>
      subcommand.setName("refresh").setDescription("Force-refresh the contest schedule.")
    ),
  async execute(interaction: ChatInputCommandInteraction<CacheType>) {
    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "add":
        return await handleScheduleAdd(interaction);
      case "remove":
        return await handleScheduleRemove(interaction);
      case "view":
        return await handleScheduleView(interaction);
      case "refresh":
        return await handleScheduleRefresh(interaction);
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
