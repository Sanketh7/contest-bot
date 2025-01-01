import { RotmgClass } from "@prisma/client";
import { Client, Guild, GuildEmoji, Role, TextChannel, User } from "discord.js";
import { readFileSync } from "fs";
import { ROTMG_CLASSES } from "./constants";

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
    door: string;
  };
  classEmojis: Record<RotmgClass, string>;
  channels: {
    signUp: string;
    submission: string;
    leaderboard: string;
    staffLeaderboard: string;
    log: string;
  };
  pointsRefUrl: string;
};

type ResolvedData = {
  botOwner?: User;
  guild?: Guild;
  roles?: {
    admin?: Role;
    moderator?: Role;
    contestStaff?: Role;
    contestant?: Role;
  };
  generalEmojis?: {
    accept?: string;
    reject?: string;
    edit?: string;
    grave?: GuildEmoji;
    door?: string;
  };
  classEmojis?: Partial<Record<RotmgClass, GuildEmoji>>;
  channels?: {
    signUp?: TextChannel;
    submission?: TextChannel;
    leaderboard?: TextChannel;
    staffLeaderboard?: TextChannel;
    log?: TextChannel;
  };
  pointsRefUrl?: string;
};

export class Settings {
  private static instance: Settings;
  private readonly data: ResolvedData;

  private constructor() {
    this.data = {};
  }

  static getInstance(): Settings {
    if (!this.instance) {
      this.instance = new Settings();
    }
    return this.instance;
  }

  get<T extends keyof ResolvedData>(key: T): NonNullable<ResolvedData[T]> {
    const ret = this.data[key];
    if (!ret) {
      console.error(`failed to fetch setting ${key}`);
      throw new Error(`failed to fetch setting ${key}`);
    }
    return ret;
  }

  private set<T extends keyof ResolvedData>(key: T, value: ResolvedData[T] | null | undefined) {
    if (!value) {
      console.error(`failed to set setting ${key}`);
      throw new Error(`failed to set setting ${key}`);
    }
    this.data[key] = value;
  }

  getRole<T extends keyof Required<ResolvedData>["roles"]>(
    key: T
  ): NonNullable<Required<ResolvedData>["roles"][T]> {
    const ret = this.data.roles?.[key];
    if (!ret) {
      console.error(`failed to fetch role ${key} from settings`);
      throw new Error(`failed to fetch role ${key} from settings`);
    }
    return ret;
  }

  private setRole<T extends keyof Required<ResolvedData>["roles"]>(
    key: T,
    value: Required<ResolvedData>["roles"][T] | null | undefined
  ) {
    if (!value) {
      console.error(`failed to set role ${key} in settings`);
      throw new Error(`failed to set role ${key} in settings`);
    }
    if (!this.data.roles) this.data.roles = {};
    this.data.roles[key] = value;
  }

  getGeneralEmoji<T extends keyof Required<ResolvedData>["generalEmojis"]>(
    key: T
  ): NonNullable<Required<ResolvedData>["generalEmojis"][T]> {
    const ret = this.data.generalEmojis?.[key];
    if (!ret) {
      console.error(`failed to fetch general emoji ${key} from settings`);
      throw new Error(`failed to fetch general emoji ${key} from settings`);
    }
    return ret;
  }

  private setGeneralEmoji<T extends keyof Required<ResolvedData>["generalEmojis"]>(
    key: T,
    value: Required<ResolvedData>["generalEmojis"][T] | null | undefined
  ) {
    if (!value) {
      console.error(`failed to set general emoji ${key} in settings`);
      throw new Error(`failed to set general emoji ${key} in settings`);
    }
    if (!this.data.generalEmojis) this.data.generalEmojis = {};
    this.data.generalEmojis[key] = value;
  }

  getClassEmoji<T extends keyof Required<ResolvedData>["classEmojis"]>(
    key: T
  ): NonNullable<Required<ResolvedData>["classEmojis"][T]> {
    const ret = this.data.classEmojis?.[key];
    if (!ret) {
      console.error(`failed to fetch class emoji ${key} from settings`);
      throw new Error(`failed to fetch class emoji ${key} from settings`);
    }
    return ret;
  }

  private setClassEmoji<T extends keyof Required<ResolvedData>["classEmojis"]>(
    key: T,
    value: Required<ResolvedData>["classEmojis"][T] | null | undefined
  ) {
    if (!value) {
      console.error(`failed to set class emoji ${key} in settings`);
      throw new Error(`failed to set class emoji ${key} in settings`);
    }
    if (!this.data.classEmojis) this.data.classEmojis = {};
    this.data.classEmojis[key] = value;
  }

  getChannel<T extends keyof Required<ResolvedData>["channels"]>(
    key: T
  ): NonNullable<Required<ResolvedData>["channels"][T]> {
    const ret = this.data.channels?.[key];
    if (!ret) {
      console.error(`failed to fetch channel ${key} from settings`);
      throw new Error(`failed to fetch channel ${key} from settings`);
    }
    return ret;
  }

  private setChannel<T extends keyof Required<ResolvedData>["channels"]>(
    key: T,
    value: Required<ResolvedData>["channels"][T] | null | undefined
  ) {
    if (!value) {
      console.error(`failed to set channl ${key} in settings`);
      throw new Error(`failed to set channel ${key} in settings`);
    }
    if (!this.data.channels) this.data.channels = {};
    this.data.channels[key] = value;
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
      await this.loadMisc(jsonData);
    } catch (err) {
      console.error(err);
    }
  }

  private async loadBotOwner(client: Client, jsonData: JsonData) {
    this.set("botOwner", await client.users.fetch(jsonData.botOwner));
  }

  private async loadGuild(client: Client, jsonData: JsonData) {
    this.set("guild", await client.guilds.fetch(jsonData.guild));
  }

  private async loadRoles(jsonData: JsonData) {
    const guild = this.get("guild");

    for (const name of ["admin", "contestStaff", "moderator", "contestant"] as const) {
      const role = guild.roles.cache.find((r) => r.name === jsonData.roles[name]);
      this.setRole(name, role);
    }
  }

  private async loadEmojis(jsonData: JsonData) {
    const guild = this.get("guild");

    for (const name of ["accept", "reject", "edit", "door"] as const) {
      this.setGeneralEmoji(name, jsonData.generalEmojis[name]);
    }
    this.setGeneralEmoji(
      "grave",
      guild.emojis.cache.find((e) => e.name === jsonData.generalEmojis.grave)
    );

    for (const name of ROTMG_CLASSES) {
      this.setClassEmoji(
        name,
        guild.emojis.cache.find((e) => e.name === jsonData.classEmojis[name])
      );
    }
  }

  private async loadChannels(jsonData: JsonData) {
    const guild = this.get("guild");

    const byName = (name: string): TextChannel | null => {
      const channel = guild.channels.cache.find((c) => c.name === name);
      if (channel && channel instanceof TextChannel) {
        return channel;
      }
      return null;
    };

    for (const name of [
      "signUp",
      "submission",
      "leaderboard",
      "staffLeaderboard",
      "log",
    ] as const) {
      this.setChannel(name, byName(jsonData.channels[name]));
    }
  }

  private async loadMisc(jsonData: JsonData) {
    this.set("pointsRefUrl", jsonData.pointsRefUrl);
  }
}
