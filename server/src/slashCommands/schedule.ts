import { Contest } from "@prisma/client";
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
import { SlashCommand, SlashCommandDescriptions } from "../types";
import { displayDatetimeString, parseDatetimeString } from "../util";

const descriptions = {
  description: "Manage and view the contest schedule.",
  subcommands: {
    add: {
      description: "Add a contest to the schedule.",
      options: {
        start: "Start of contest (UTC) in format: YYYY-MM-DD HH:mm",
        end: "End of contest (UTC) in format: YYYY-MM-DD HH:mm",
      },
    },
    remove: {
      description: "Remove a contest from the schedule.",
      options: {
        contestId: "Contest ID",
      },
    },
    view: {
      description: "View the upcoming contest schedule.",
    },
    history: {
      description: "View the contest schedule history.",
    },
    refresh: {
      description: "Force-refresh the contest schedule.",
    },
  },
} satisfies SlashCommandDescriptions;

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

const createScheduleTable = (schedule: Contest[]): string[][] => {
  const tableData: string[][] = [["ID", "Start", "End"]];
  for (const contest of schedule) {
    tableData.push([
      contest.id.toString(),
      displayDatetimeString(contest.startTime),
      displayDatetimeString(contest.endTime),
    ]);
  }
  return tableData;
};

const handleScheduleView = async (interaction: ChatInputCommandInteraction) => {
  const schedule = await getContestsAfter(new Date());
  if (schedule.length === 0) {
    return interaction.reply({
      content: "No upcoming contests.",
    });
  }
  return await interaction.reply({
    content:
      "**Upcoming Contests**\nAll times are in UTC.\n```" +
      table(createScheduleTable(schedule)) +
      "```",
  });
};

const handleScheduleHistory = async (interaction: ChatInputCommandInteraction) => {
  const schedule = await getContestsAfter(new Date(0));
  if (schedule.length === 0) {
    return interaction.reply({
      content: "No contests.",
    });
  }
  const tableStr = table(createScheduleTable(schedule));
  if (tableStr.length > 1800) {
    return await interaction.reply({
      content: "**Schedule History**\nAll times are in UTC.",
      files: [
        {
          attachment: Buffer.from(tableStr),
          name: "schedule-history.txt",
        },
      ],
    });
  } else {
    return await interaction.reply({
      content:
        "**Schedule History**\nAll times are in UTC.\n```" +
        table(createScheduleTable(schedule)) +
        "```",
    });
  }
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
    add: ["Moderator"],
    remove: ["Moderator"],
    view: ["Contest Staff"],
    history: ["Contest Staff"],
    refresh: ["Contest Staff"],
  },
  descriptions,
  command: new SlashCommandBuilder()
    .setName("schedule")
    .setDescription(descriptions.description)
    .addSubcommand((subcommand) =>
      subcommand
        .setName("add")
        .setDescription(descriptions.subcommands.add.description)
        .addStringOption((option) =>
          option
            .setName("start")
            .setDescription(descriptions.subcommands.add.options.start)
            .setRequired(true)
        )
        .addStringOption((option) =>
          option
            .setName("end")
            .setDescription(descriptions.subcommands.add.options.end)
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("remove")
        .setDescription(descriptions.subcommands.remove.description)
        .addNumberOption((option) =>
          option
            .setName("contest-id")
            .setDescription(descriptions.subcommands.remove.options.contestId)
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand.setName("view").setDescription(descriptions.subcommands.view.description)
    )
    .addSubcommand((subcommand) =>
      subcommand.setName("history").setDescription(descriptions.subcommands.history.description)
    )
    .addSubcommand((subcommand) =>
      subcommand.setName("refresh").setDescription(descriptions.subcommands.refresh.description)
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
      case "history":
        return await handleScheduleHistory(interaction);
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
