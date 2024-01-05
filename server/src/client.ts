import { Client, Collection, GatewayIntentBits, Partials } from "discord.js";
import { Command } from "./commands/types";

export const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildMessageReactions,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.DirectMessageReactions,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildEmojisAndStickers,
  ],
  partials: [Partials.Channel],
});

declare module "discord.js" {
  interface Client {
    commands: Collection<string, Command>;
  }
}
