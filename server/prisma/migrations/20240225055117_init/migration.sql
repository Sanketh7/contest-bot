-- CreateEnum
CREATE TYPE "RotmgClass" AS ENUM ('Knight', 'Warrior', 'Paladin', 'Assassin', 'Rogue', 'Trickster', 'Archer', 'Huntress', 'Mystic', 'Wizard', 'Necromancer', 'Ninja', 'Samurai', 'Priest', 'Sorcerer', 'Bard', 'Summoner', 'Kensei');

-- CreateTable
CREATE TABLE "Contest" (
    "id" SERIAL NOT NULL,
    "isActive" BOOLEAN NOT NULL DEFAULT false,
    "startTime" TIMESTAMP(3) NOT NULL,
    "endTime" TIMESTAMP(3) NOT NULL,
    "bannedUserIds" TEXT[],

    CONSTRAINT "Contest_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Character" (
    "id" SERIAL NOT NULL,
    "userId" TEXT NOT NULL,
    "isActive" BOOLEAN NOT NULL,
    "rotmgClass" "RotmgClass" NOT NULL,
    "keywords" TEXT[],
    "contestId" INTEGER NOT NULL,

    CONSTRAINT "Character_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Submission" (
    "id" SERIAL NOT NULL,
    "isAccepted" BOOLEAN NOT NULL DEFAULT false,
    "keywords" TEXT[],
    "imageUrl" TEXT NOT NULL,
    "characterId" INTEGER NOT NULL,

    CONSTRAINT "Submission_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "Character" ADD CONSTRAINT "Character_contestId_fkey" FOREIGN KEY ("contestId") REFERENCES "Contest"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Submission" ADD CONSTRAINT "Submission_characterId_fkey" FOREIGN KEY ("characterId") REFERENCES "Character"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
