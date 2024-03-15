import dayjs from "dayjs";
import customParseFormat from "dayjs/plugin/customParseFormat";
import utc from "dayjs/plugin/utc";
import { Client, Collection, GatewayIntentBits } from "discord.js";
import { readdirSync } from "fs";
import * as schedule from "node-schedule";
import path, { join } from "path";
import { ENV } from "./env";
import { contestScheduleJob, refreshLeaderboardJob } from "./jobs/contestScheduling";
import { PointsManager } from "./pointsManager";
import { createGuild } from "./services/guildService";
import { Settings } from "./settings";
import { SlashCommand } from "./types";

dayjs.extend(customParseFormat);
dayjs.extend(utc);

process.on("unhandledRejection", console.error);
process.on("uncaughtException", console.error);

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.GuildEmojisAndStickers,
    GatewayIntentBits.GuildMessageReactions,
    GatewayIntentBits.DirectMessageReactions,
  ],
});

client.slashCommands = new Collection<string, SlashCommand>();
client.cooldowns = new Collection<string, number>();

client.once("ready", async (client) => {
  console.log(`${client.user?.tag} connected`);
  schedule.scheduleJob(contestScheduleJob.schedule, contestScheduleJob.onTick);
  schedule.scheduleJob(refreshLeaderboardJob.schedule, refreshLeaderboardJob.onTick);
});

(async () => {
  await PointsManager.getInstance().loadCsv(path.resolve(__dirname, "..", "..", "ppe_data.csv"));
  await client.login(ENV.DISCORD_TOKEN);
  await Settings.getInstance().loadAll(
    path.resolve(__dirname, "..", "..", ENV.SETTINGS_FILENAME),
    client
  );
  await createGuild({ discordId: Settings.getInstance().get("guild").id });

  const handlersDir = join(__dirname, "./handlers");
  readdirSync(handlersDir).forEach((handler) => {
    if (handler.endsWith(".js")) {
      require(`${handlersDir}/${handler}`)(client);
    }
  });
})();
