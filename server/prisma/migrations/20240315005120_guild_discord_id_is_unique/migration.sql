/*
  Warnings:

  - A unique constraint covering the columns `[discordId]` on the table `Guild` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "Guild_discordId_key" ON "Guild"("discordId");
