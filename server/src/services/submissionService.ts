import { Character, Submission } from "@prisma/client";
import { prisma } from "../prisma";
import { modifyCharacterKeywords } from "./characterService";

export const createSubmission = async (
  character: Character,
  data: {
    keywords: string[];
    proofUrls: string[];
  }
): Promise<Submission> => {
  const extraProofUrls = data.proofUrls.length > 1 ? data.proofUrls.slice(1) : [];
  return prisma.submission.create({
    data: {
      characterId: character.id,
      keywords: data.keywords,
      proofUrl: data.proofUrls[0],
      extraProofUrls,
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

export const getSubmissionsForCharacter = async (
  characterId: number,
  last?: number
): Promise<Submission[]> => {
  const submissions = prisma.submission.findMany({
    where: {
      characterId,
    },
    orderBy: {
      id: "desc",
    },
    take: last,
  });
  return (await submissions).reverse();
};

export const acceptSubmission = async (submission: Submission, acceptedByDiscordUser: string) => {
  await prisma.submission.update({
    where: {
      id: submission.id,
    },
    data: {
      isAccepted: true,
      acceptedByDiscordUser
    },
  });
  await modifyCharacterKeywords(submission.characterId, submission.keywords, "add");
};
