/*
  Warnings:

  - You are about to drop the column `imageUrl` on the `Submission` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Submission" RENAME COLUMN "imageUrl" TO "proofUrl";
ALTER TABLE "Submission" ADD COLUMN     "extraProofUrls" TEXT[];
