import { RotmgClass } from "@prisma/client";
import { Client, Emoji, Guild, Role, TextChannel, User } from "discord.js";
import { readFileSync } from "fs";

type JsonData = {
  botOwner: string;
  guild: string;
  roles: {
    admin: string;
    moderator: string;
    contestStaff: string;
    contestant: string;
  };
  generalEmojis: {
    accept: string;
    reject: string;
    edit: string;
    grave: string;
  };
  classEmojis: Record<RotmgClass, string>;
  channels: {
    signUp: string;
    submission: string;
    leaderboard: string;
    log: string;
  };
  pointsRefUrl: string;
};

type ResolvedData = {
  botOwner: User;
  guild: Guild;
  roles: {
    admin: Role;
    moderator: Role;
    contestStaff: Role;
    contestant: Role;
  };
  generalEmojis: {
    accept: string;
    reject: string;
    edit: string;
    grave: Emoji;
  };
  classEmojis: Record<RotmgClass, Emoji>;
  channels: {
    signUp: TextChannel;
    submission: TextChannel;
    leaderboard: TextChannel;
    log: TextChannel;
  };
  pointsRefUrl: string;
};

const exists = <T>(v: T | null | undefined): T => {
  if (v === null || v === undefined) {
    throw new Error();
  }
  return v;
};

export class Settings {
  private static instance: Settings;
  data: Partial<ResolvedData>;

  private constructor() {
    this.data = {};
  }

  static getInstance(): Settings {
    if (!this.instance) {
      this.instance = new Settings();
    }
    return this.instance;
  }

  async loadAll(path: string, client: Client) {
    try {
      const fileData = readFileSync(path, "utf-8");
      const jsonData: JsonData = JSON.parse(fileData);

      await this.loadBotOwner(client, jsonData);
      await this.loadGuild(client, jsonData);
      await this.loadRoles(jsonData);
      await this.loadEmojis(jsonData);
      await this.loadChannels(jsonData);
    } catch (err) {
      console.error(err);
    }
  }

  private async loadBotOwner(client: Client, jsonData: JsonData) {
    const user = await client.users.fetch(jsonData.botOwner);
    this.data.botOwner = exists(user);
  }

  private async loadGuild(client: Client, jsonData: JsonData) {
    const guild = await client.guilds.fetch(jsonData.guild);
    this.data.guild = exists(guild);
  }

  private async loadRoles(jsonData: JsonData) {
    const guild = exists(this.data.guild);

    const admin = guild.roles.cache.find((r) => r.name === jsonData.roles.admin);
    const contestStaff = guild.roles.cache.find((r) => r.name === jsonData.roles.contestStaff);
    const moderator = guild.roles.cache.find((r) => r.name === jsonData.roles.moderator);
    const contestant = guild.roles.cache.find((r) => r.name === jsonData.roles.contestant);

    this.data.roles = {
      admin: exists(admin),
      contestStaff: exists(contestStaff),
      moderator: exists(moderator),
      contestant: exists(contestant),
    };
  }

  private async loadEmojis(jsonData: JsonData) {
    const guild = exists(this.data.guild);

    const byName = (name: string): Emoji => exists(guild.emojis.cache.find((e) => e.name === name));

    const { accept, reject, edit } = jsonData.generalEmojis;
    this.data.generalEmojis = {
      accept,
      reject,
      edit,
      grave: byName(jsonData.generalEmojis.grave),
    };

    const c = jsonData.classEmojis;
    this.data.classEmojis = {
      Bard: byName(c.Bard),
      Sorcerer: byName(c.Sorcerer),
      Wizard: byName(c.Wizard),
      Samurai: byName(c.Samurai),
      Mystic: byName(c.Mystic),
      Assassin: byName(c.Assassin),
      Rogue: byName(c.Rogue),
      Archer: byName(c.Archer),
      Ninja: byName(c.Ninja),
      Priest: byName(c.Priest),
      Warrior: byName(c.Warrior),
      Trickster: byName(c.Trickster),
      Knight: byName(c.Knight),
      Necromancer: byName(c.Necromancer),
      Huntress: byName(c.Huntress),
      Paladin: byName(c.Paladin),
      Summoner: byName(c.Summoner),
      Kensei: byName(c.Kensei),
    };
  }

  private async loadChannels(jsonData: JsonData) {
    const guild = exists(this.data.guild);

    const byName = (name: string): TextChannel | null => {
      const channel = guild.channels.cache.find((c) => c.name === name);
      if (channel && channel instanceof TextChannel) {
        return channel;
      }
      return null;
    };

    const { signUp, submission, leaderboard, log } = jsonData.channels;
    this.data.channels = {
      signUp: exists(byName(signUp)),
      submission: exists(byName(submission)),
      leaderboard: exists(byName(leaderboard)),
      log: exists(byName(log)),
    };
  }

  private async loadMisc(jsonData: JsonData) {
    this.data.pointsRefUrl = exists(jsonData.pointsRefUrl);
  }
}
