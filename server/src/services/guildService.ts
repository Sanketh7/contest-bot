import { Guild as PrismaGuild } from "@prisma/client";
import { Guild, User } from "discord.js";
import { prisma } from "../prisma";

export const createGuild = async (data: { discordId: string }): Promise<PrismaGuild> => {
  const existingGuild = await prisma.guild.findUnique({
    where: {
      discordId: data.discordId,
    },
  });
  if (existingGuild) return existingGuild;
  return prisma.guild.create({
    data: {
      discordId: data.discordId,
    },
  });
};

export const updateBanList = async (
  guild: Guild,
  action: "ban" | "unban",
  user: User
): Promise<boolean> => {
  const guildData = await prisma.guild.findUnique({
    where: {
      discordId: guild.id,
    },
  });
  if (!guildData) return false;
  const bans = new Set<string>(guildData.bannedUserIds);
  if (action === "ban") {
    bans.add(user.id);
  } else if (action === "unban") {
    bans.delete(user.id);
  }
  await prisma.guild.update({
    where: {
      discordId: guild.id,
    },
    data: {
      bannedUserIds: Array.from(bans),
    },
  });
  return true;
};

export const getBanList = async (guild: Guild): Promise<string[]> => {
  const bans = await prisma.guild
    .findUnique({
      where: {
        discordId: guild.id,
      },
      select: {
        bannedUserIds: true,
      },
    })
    .then((data) => data?.bannedUserIds);
  return bans ?? [];
};
