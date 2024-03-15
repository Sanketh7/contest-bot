-- CreateTable
CREATE TABLE "Guild" (
    "id" SERIAL NOT NULL,
    "discordId" TEXT NOT NULL,
    "bannedUserIds" TEXT[],

    CONSTRAINT "Guild_pkey" PRIMARY KEY ("id")
);
