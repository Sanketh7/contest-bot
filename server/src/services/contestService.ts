import { Contest } from "@prisma/client";
import { prisma } from "../prisma";

export const getActiveContest = async (): Promise<Contest | null> => {
  return prisma.contest.findFirst({
    where: {
      isActive: true,
    },
  });
};

export const getReadyContest = async (): Promise<Contest | null> => {
  const currTime = new Date();
  const activeContest = await getActiveContest();
  if (activeContest) {
    return null;
  }
  return prisma.contest.findFirst({
    where: {
      startTime: {
        lte: currTime,
      },
      endTime: {
        gte: currTime,
      },
    },
  });
};

export const shouldContestEnd = (contest: Contest): boolean => {
  const currTime = new Date();
  return currTime >= contest.endTime;
};

export const endContest = async (contest: Contest) => {
  await prisma.contest.update({
    where: {
      id: contest.id,
    },
    data: {
      isActive: false,
    },
  });

  // TODO: handle contest post
};
