/*
  Warnings:

  - The `modifiers` column on the `Character` table would be dropped and recreated. This will lead to data loss if there is data in the column.

*/
-- CreateEnum
CREATE TYPE "CharacterModifier" AS ENUM ('No_Pet', 'Crucible', 'UT_ST_Only', 'Duo');

-- AlterTable
ALTER TABLE "Character" DROP COLUMN "modifiers",
ADD COLUMN     "modifiers" "CharacterModifier"[];

-- DropEnum
DROP TYPE "Modifier";
