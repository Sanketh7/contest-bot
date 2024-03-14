import { Contest } from "@prisma/client";
import { ActionRowBuilder, ButtonBuilder, ButtonStyle, EmbedBuilder } from "discord.js";
import { CONTEST_POST_BUTTON_CUSTOM_IDS } from "../constants";
import { prisma } from "../prisma";
import { Settings } from "../settings";
import { displayDatetimeString } from "../util";

export const getContest = async (contestId: number): Promise<Contest | null> => {
  return prisma.contest.findUnique({
    where: {
      id: contestId,
    },
  });
};

export const getContestsAfter = async (time: Date): Promise<Contest[]> => {
  return prisma.contest.findMany({
    where: {
      startTime: {
        gte: time,
      },
    },
    orderBy: {
      startTime: "asc",
    },
  });
};

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
      forceEnded: {
        equals: false,
      },
    },
  });
};

export const startContest = async (contest: Contest) => {
  const embed = new EmbedBuilder()
    .setTitle("A New PPE Contest Has Started!")
    .setDescription(`Ends on ${displayDatetimeString(contest.endTime)} (UTC)`)
    .addFields({
      name: "Instructions",
      value: `**Sign Up:** Sign up for this contest. (Lets you view all the channels and submit.)
    **New Character:** Start a new character. Completing this will STOP your previous character (so you can't edit it anymore).
    **Edit Character:** Edit your current character. This will add items/achievements to your current character.

    Use the command \`/profile\` to view all your characters for this contest.
    `,
    });
  const signUpButton = new ButtonBuilder()
    .setCustomId(CONTEST_POST_BUTTON_CUSTOM_IDS.signUp)
    .setStyle(ButtonStyle.Primary)
    .setEmoji(Settings.getInstance().data.generalEmojis!.accept)
    .setLabel("Sign Up");
  const newCharacterButton = new ButtonBuilder()
    .setCustomId(CONTEST_POST_BUTTON_CUSTOM_IDS.newCharacter)
    .setStyle(ButtonStyle.Success)
    .setEmoji(Settings.getInstance().data.generalEmojis!.grave.id)
    .setLabel("New Character");
  const editCharacterButton = new ButtonBuilder()
    .setCustomId(CONTEST_POST_BUTTON_CUSTOM_IDS.editCharacter)
    .setStyle(ButtonStyle.Success)
    .setEmoji(Settings.getInstance().data.generalEmojis!.edit)
    .setLabel("Edit Character");

  const msg = await Settings.getInstance().data.channels?.signUp.send({
    embeds: [embed],
    components: [
      new ActionRowBuilder<ButtonBuilder>().addComponents(
        signUpButton,
        newCharacterButton,
        editCharacterButton
      ),
    ],
  });

  await prisma.contest.update({
    where: {
      id: contest.id,
    },
    data: {
      isActive: true,
      postId: msg?.id,
    },
  });
};

export const createContest = async (data: { startTime: Date; endTime: Date }): Promise<Contest> => {
  return prisma.contest.create({
    data: {
      startTime: data.startTime,
      endTime: data.endTime,
    },
  });
};

export const deleteContest = async (contest: Contest): Promise<Contest> => {
  return prisma.contest.delete({
    where: {
      id: contest.id,
    },
  });
};

export const shouldContestEnd = (contest: Contest): boolean => {
  const currTime = new Date();
  return currTime >= contest.endTime;
};

export const endContest = async (contest: Contest, opts?: { force: boolean }) => {
  await prisma.contest.update({
    where: {
      id: contest.id,
    },
    data: {
      isActive: false,
      forceEnded: opts?.force ?? undefined,
    },
  });

  if (contest.postId) {
    const msg = await Settings.getInstance().data.channels?.signUp.messages.fetch(contest.postId);
    await msg?.delete();
  }
};

export const refreshContestSchedule = async () => {
  const contest = await getActiveContest();
  if (contest) {
    if (shouldContestEnd(contest)) {
      await endContest(contest);
    }
  } else {
    const readyContest = await getReadyContest();
    if (readyContest) {
      await startContest(readyContest);
    }
  }
};
