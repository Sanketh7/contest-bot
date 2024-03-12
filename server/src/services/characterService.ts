import { Character } from "@prisma/client";
import { prisma } from "../prisma";

export const getCharacter = async (id: number): Promise<Character | null> => {
  return prisma.character.findUnique({
    where: {
      id,
    },
  });
};

export const getActiveCharacterByUserId = async (userId: string): Promise<Character | null> => {
  return prisma.character.findFirst({
    where: {
      userId,
      isActive: true,
    },
  });
};
