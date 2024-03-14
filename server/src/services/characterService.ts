import { Character, Contest } from "@prisma/client";
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
  count: number,
  mode: "active" | "all"
): Promise<(Character & { points: number })[]> => {
  const allCharacters = await prismaWithPoints.character.findMany({
    where: {
      contestId: contest.id,
      isActive: mode === "active" ? true : undefined,
    },
  });
  allCharacters.sort((a, b) => b.points - a.points);
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

export const addKeywordsToCharacter = async (characterId: number, keywords: string[]) => {
  return prisma.$transaction(async (tx): Promise<any> => {
    const character = await tx.character.findUnique({
      where: {
        id: characterId,
      },
    });
    if (!character) return;
    const oldKeywords = new Set<string>(character.keywords);
    keywords.forEach((k) => oldKeywords.add(k));
    await tx.character.update({
      where: {
        id: character.id,
      },
      data: {
        keywords: Array.from(oldKeywords),
      },
    });
  });
};
