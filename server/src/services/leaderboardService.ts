import { Contest } from "@prisma/client";
import { EmbedBuilder } from "discord.js";
import { table } from "table";
import { client } from "../client";
import { Settings } from "../settings";
import { truncateEllipses } from "../util";
import { getTopCharacters } from "./characterService";
import { getBanList } from "./guildService";

const NUM_TABLE_LIMIT = 5;
const NUM_ROWS_PER_TABLE_LIMIT = 11;

export const cleanLeaderboardChannel = async () => {
  const channel = Settings.getInstance().getChannel("leaderboard");
  if (!channel) return;
  try {
    const messages = await channel.messages.fetch({
      limit: 20,
    });
    const botMessages = messages.filter((m) => m.author.bot && m.bulkDeletable);
    channel.bulkDelete(botMessages);
  } catch (err) {
    console.error(err);
  }
};

export const generateTopCharactersLeaderboard = async (
  contest: Contest,
  mode: "active" | "all" | "top",
  count: number | "inf"
): Promise<string[][]> => {
  const guild = Settings.getInstance().get("guild");
  const characters = await getTopCharacters(contest, count, mode);
  const bans = await getBanList(guild);
  const tableData = [["Rank", "Player", "Points", "Class"]];
  if (mode === "all") {
    tableData[0].push("Active?");
  }
  let currRank = 0;
  let prevPoints = Number.POSITIVE_INFINITY;

  const members = await guild.members.fetch({
    user: characters.map((c) => c.userId),
  });

  for (const character of characters) {
    if (bans.includes(character.userId)) {
      continue;
    }
    const member = members.get(character.userId);
    let ign: string;
    if (member) {
      ign = truncateEllipses(member.nickname ?? member.displayName, 20);
    } else {
      const user = await client.users.fetch(character.userId);
      if (user) {
        ign = "@" + user.username;
      } else {
        ign = character.userId;
      }
    }
    if (character.points.total < prevPoints) {
      currRank++;
    }
    prevPoints = character.points.total;

    const row = [currRank.toString(), ign, character.points.total.toFixed(0), character.rotmgClass];
    if (mode === "all") {
      row.push(character.isActive ? Settings.getInstance().getGeneralEmoji("accept") + " " : "");
    }
    tableData.push(row);
  }

  return tableData;
};

export const displayTopCharactersLeaderboard = async (contest: Contest, mode: "active" | "all") => {
  const tableData = await generateTopCharactersLeaderboard(
    contest,
    mode,
    NUM_TABLE_LIMIT * NUM_ROWS_PER_TABLE_LIMIT
  );
  const embed = new EmbedBuilder()
    .setTitle(mode === "active" ? "Top Active Characters" : "Top Characters")
    .setDescription("Updated every 2 minutes during a contest.");
  const contents: string[] = [];
  for (let i = 0; i < tableData.length; i += NUM_ROWS_PER_TABLE_LIMIT) {
    contents.push(
      "```" +
        table(tableData.slice(i, Math.min(tableData.length, i + NUM_ROWS_PER_TABLE_LIMIT))) +
        "```"
    );
  }
  await Settings.getInstance()
    .getChannel("leaderboard")
    .send({
      embeds: [embed],
    });
  for (const content of contents) {
    await Settings.getInstance().getChannel("leaderboard").send({
      content,
    });
  }
};
