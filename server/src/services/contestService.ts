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
  const msg = await Settings.getInstance()
    .getChannel("signUp")
    .send({
      ...buildContestPost(contest),
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

export const refreshContestPost = async (contest: Contest) => {
  const msg = contest.postId
    ? await Settings.getInstance()
        .getChannel("signUp")
        .messages.fetch(contest.postId)
        .catch((err) => {
          console.warn(err);
          return null;
        })
    : null;
  if (msg) {
    await msg.edit({
      ...buildContestPost(contest),
    });
  } else {
    await Settings.getInstance()
      .getChannel("signUp")
      .send({
        ...buildContestPost(contest),
      });
  }
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
    const msg = await Settings.getInstance().getChannel("signUp").messages.fetch(contest.postId);
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

const buildContestPost = (
  contest: Contest
): { embeds: EmbedBuilder[]; components: ActionRowBuilder<ButtonBuilder>[] } => {
  const embed = new EmbedBuilder()
    .setTitle("A New PPE Contest Has Started!")
    .setDescription(`Ends on ${displayDatetimeString(contest.endTime)} (UTC)`)
    .addFields({
      name: "Instructions",
      value: `**Sign Up:** Sign up for this contest. (Lets you view all the channels and submit.)
    **Sign Out:** Sign out of the contest. This will hide all channels. Note that your characters and submissions will NOT be deleted.
    **New Character:** Start a new character. Completing this will STOP your previous character (so you can't edit it anymore).
    **Edit Character:** Edit your current character. This will add items/achievements to your current character.

    Helpful commands:
    \`/profile\` to view all your characters for this contest.
    \`/submit\` to edit your current character. Does the same thing as the "Edit Character" button below but this command can be used anywhere.
    `,
    });
  const signUpButton = new ButtonBuilder()
    .setCustomId(CONTEST_POST_BUTTON_CUSTOM_IDS.signUp)
    .setStyle(ButtonStyle.Primary)
    .setEmoji(Settings.getInstance().getGeneralEmoji("accept"))
    .setLabel("Sign Up");
  const signOutButton = new ButtonBuilder()
    .setCustomId(CONTEST_POST_BUTTON_CUSTOM_IDS.signOut)
    .setStyle(ButtonStyle.Secondary)
    .setEmoji(Settings.getInstance().getGeneralEmoji("door"))
    .setLabel("Sign Out");
  const newCharacterButton = new ButtonBuilder()
    .setCustomId(CONTEST_POST_BUTTON_CUSTOM_IDS.newCharacter)
    .setStyle(ButtonStyle.Success)
    .setEmoji(Settings.getInstance().getGeneralEmoji("grave").id)
    .setLabel("New Character");
  const editCharacterButton = new ButtonBuilder()
    .setCustomId(CONTEST_POST_BUTTON_CUSTOM_IDS.editCharacter)
    .setStyle(ButtonStyle.Success)
    .setEmoji(Settings.getInstance().getGeneralEmoji("edit"))
    .setLabel("Edit Character");

  return {
    embeds: [embed],
    components: [
      new ActionRowBuilder<ButtonBuilder>().addComponents(
        signUpButton,
        signOutButton,
        newCharacterButton,
        editCharacterButton
      ),
    ],
  };
};
