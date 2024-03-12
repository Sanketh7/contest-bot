import { Character, Submission } from "@prisma/client";
import { prisma } from "../prisma";

export const createSubmission = async (
  character: Character,
  data: {
    keywords: string[];
    imageUrl: string;
  }
): Promise<Submission> => {
  return prisma.submission.create({
    data: {
      characterId: character.id,
      keywords: data.keywords,
      imageUrl: data.imageUrl,
    },
  });
};
