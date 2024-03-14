import { RotmgClass } from "@prisma/client";
import pgPromise from "pg-promise";
import { prisma } from "../prisma";

const pgp = pgPromise();
const oldDb = pgp(process.env.OLD_DB_URI ?? "");

function capitalizeFirstLetter(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

const main = async () => {
  await prisma.character.deleteMany();
  await prisma.contest.deleteMany();

  const contests = await oldDb.any('SELECT * FROM "public"."contest"');
  console.log(`fetched ${contests.length} contests`);
  const contestData = [];
  for (const contest of contests) {
    contestData.push({
      id: contest["id"],
      isActive: contest["is_active"],
      startTime: new Date(contest["start_time"]),
      endTime: new Date(contest["end_time"]),
      postId: contest["post_id"]?.toString(),
      bannedUserIds: contest["banned_users"],
      forceEnded: false,
    });
  }
  await prisma.contest.createMany({
    data: contestData,
  });

  const characters = await oldDb.any('SELECT * FROM "public"."character"');
  console.log(`fetched ${characters.length} characters`);
  const charData = [];
  for (const char of characters) {
    charData.push({
      id: char["id"],
      userId: char["user_id"],
      isActive: char["is_active"],
      rotmgClass: capitalizeFirstLetter(char["rotmg_class"]) as RotmgClass,
      modifiers: [],
      keywords: char["keywords"],
      contestId: char["contest"],
    });
  }
  await prisma.character.createMany({
    data: charData,
  });

  const submissions = await oldDb.any('SELECT * FROM "public"."submission"');
  console.log(`fetched ${submissions.length} submissions`);
  const subData = [];
  for (const sub of submissions) {
    subData.push({
      id: sub["id"],
      isAccepted: sub["is_accepted"],
      keywords: sub["keywords"],
      imageUrl: sub["img_url"],
      characterId: sub["character"],
    });
  }
  await prisma.submission.createMany({
    data: subData,
  });
};

main().then((_) => pgp.end());
