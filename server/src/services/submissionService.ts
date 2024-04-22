import { Character, Submission } from "@prisma/client";
import { prisma } from "../prisma";
import { modifyCharacterKeywords } from "./characterService";

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

export const getSubmission = async (submissionId: number): Promise<Submission | null> => {
  return prisma.submission.findUnique({
    where: {
      id: submissionId,
    },
  });
};

export const getSubmissionsForCharacter = async (characterId: number): Promise<Submission[]> => {
  return prisma.submission.findMany({
    where: {
      characterId,
    },
  });
};

export const acceptSubmission = async (submission: Submission) => {
  await prisma.submission.update({
    where: {
      id: submission.id,
    },
    data: {
      isAccepted: true,
    },
  });
  await modifyCharacterKeywords(submission.characterId, submission.keywords, "add");
};
