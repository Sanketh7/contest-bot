import { Client, Collection, GatewayIntentBits } from "discord.js";
import { readdirSync } from "fs";
import path, { join } from "path";
import { ENV } from "./env";
import { PointsManager } from "./pointsManager";
import { Settings } from "./settings";
import { SlashCommand } from "./types";

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

(async () => {
  await PointsManager.getInstance().loadCsv(path.resolve(__dirname, "..", "..", "ppe_data.csv"));
  await client.login(ENV.DISCORD_TOKEN);
  await Settings.getInstance().loadAll(
    path.resolve(__dirname, "..", "..", "settings.json"),
    client
  );

  const handlersDir = join(__dirname, "./handlers");
  readdirSync(handlersDir).forEach((handler) => {
    if (handler.endsWith(".js")) {
      require(`${handlersDir}/${handler}`)(client);
    }
  });
})();
