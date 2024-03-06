"use strict";
var __awaiter =
  (this && this.__awaiter) ||
  function (thisArg, _arguments, P, generator) {
    function adopt(value) {
      return value instanceof P
        ? value
        : new P(function (resolve) {
            resolve(value);
          });
    }
    return new (P || (P = Promise))(function (resolve, reject) {
      function fulfilled(value) {
        try {
          step(generator.next(value));
        } catch (e) {
          reject(e);
        }
      }
      function rejected(value) {
        try {
          step(generator["throw"](value));
        } catch (e) {
          reject(e);
        }
      }
      function step(result) {
        result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected);
      }
      step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
  };
Object.defineProperty(exports, "__esModule", { value: true });
const discord_js_1 = require("discord.js");
const fs_1 = require("fs");
const path_1 = require("path");
const env_1 = require("./env");
const client = new discord_js_1.Client({
  intents: [
    discord_js_1.GatewayIntentBits.Guilds,
    discord_js_1.GatewayIntentBits.GuildMembers,
    discord_js_1.GatewayIntentBits.GuildMessages,
    discord_js_1.GatewayIntentBits.MessageContent,
    discord_js_1.GatewayIntentBits.DirectMessages,
    discord_js_1.GatewayIntentBits.GuildEmojisAndStickers,
    discord_js_1.GatewayIntentBits.GuildMessageReactions,
    discord_js_1.GatewayIntentBits.DirectMessageReactions,
  ],
});
client.slashCommands = new discord_js_1.Collection();
client.cooldowns = new discord_js_1.Collection();
(() =>
  __awaiter(void 0, void 0, void 0, function* () {
    yield client.login(env_1.ENV.DISCORD_TOKEN);
    const handlersDir = (0, path_1.join)(__dirname, "./handlers");
    (0, fs_1.readdirSync)(handlersDir).forEach((handler) => {
      if (handler.endsWith(".js")) {
        require(`${handlersDir}/${handler}`)(client);
      }
    });
  }))();
