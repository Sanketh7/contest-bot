import { Character, Contest } from "@prisma/client";
import { Points } from "../pointsManager";
import { prisma, prismaWithPoints } from "../prisma";
import { CharacterModifier, RotmgClass } from "../types";

export const getCharacter = async (id: number): Promise<Character | null> => {
  return prisma.character.findUnique({
    where: {
      id,
    },
  });
};

export const getActiveCharacterByUserId = async (
  userId: string,
  contest: Contest
): Promise<Character | null> => {
  return await prisma.character.findFirst({
    where: {
      userId,
      isActive: true,
      contestId: contest.id,
    },
  });
};

export const getCharactersByUserId = async (
  userId: string,
  contest: Contest
): Promise<Character[]> => {
  return await prisma.character.findMany({
    where: {
      userId,
      contestId: contest.id,
    },
  });
};

export const getTopCharacters = async (
  contest: Contest,
  count: number | "inf",
  mode: "active" | "all" | "top"
): Promise<(Character & { points: Points })[]> => {
  const allCharactersRaw = await prismaWithPoints.character.findMany({
    where: {
      contestId: contest.id,
      isActive: mode === "active" ? true : undefined,
    },
  });
  allCharactersRaw.sort((a, b) => b.points.total - a.points.total);
  const allCharacters = allCharactersRaw.filter((c) => c.points.total > 0);
  if (mode === "top") {
    // remove duplicate occurrences of a user
    const seenUsers = new Set<string>();
    allCharacters.reverse();
    for (let i = allCharacters.length - 1; i >= 0; i--) {
      if (seenUsers.has(allCharacters[i].userId)) {
        allCharacters.splice(i, 1);
      }
      seenUsers.add(allCharacters[i].userId);
    }
    allCharacters.reverse();
  }
  if (count === "inf") {
    return allCharacters;
  }
  return allCharacters.slice(0, Math.min(allCharacters.length, count));
};

export const updateCharacterActivity = async (character: Character, isActive: boolean) => {
  return prisma.character.update({
    where: {
      id: character.id,
    },
    data: {
      isActive,
    },
  });
};

export const createCharacter = async (
  userId: string,
  contest: Contest,
  data: {
    isActive: boolean;
    rotmgClass: RotmgClass;
    modifiers: CharacterModifier[];
  }
): Promise<Character> => {
  return prisma.character.create({
    data: {
      isActive: data.isActive,
      rotmgClass: data.rotmgClass,
      modifiers: data.modifiers,
      contestId: contest.id,
      userId: userId,
    },
  });
};

export const modifyCharacterKeywords = async (
  characterId: number,
  keywords: string[],
  action: "add" | "remove"
) => {
  const character = await prisma.character.findUnique({
    where: {
      id: characterId,
    },
  });
  if (!character) return;
  const oldKeywords = new Set<string>(character.keywords);
  if (action === "add") {
    keywords.forEach((k) => oldKeywords.add(k));
  } else if (action === "remove") {
    keywords.forEach((k) => oldKeywords.delete(k));
  }
  await prisma.character.update({
    where: {
      id: character.id,
    },
    data: {
      keywords: Array.from(oldKeywords),
    },
  });
};

export const getStaffSubmissionFrequencies = async (
  contest: Contest
): Promise<Map<string, number>> => {
  const characterIds: number[] = await prisma.character
    .findMany({
      where: {
        contestId: contest.id,
      },
      select: {
        id: true,
      },
    })
    .then((data) => data.map((c) => c.id));
  const discordIds = await prisma.submission
    .findMany({
      where: {
        characterId: { in: characterIds },
        isAccepted: true,
      },
      select: {
        acceptedByDiscordUser: true,
      },
    })
    .then((data) => data.map((s) => s.acceptedByDiscordUser));

  const freqs = new Map<string, number>();
  for (const discordId of discordIds) {
    if (!discordId) continue;
    const prev = freqs.get(discordId);
    if (prev !== undefined) {
      freqs.set(discordId, prev + 1);
    } else {
      freqs.set(discordId, 1);
    }
  }
  return freqs;
};
