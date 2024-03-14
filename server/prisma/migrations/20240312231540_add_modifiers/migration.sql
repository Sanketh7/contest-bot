-- CreateEnum
CREATE TYPE "Modifiers" AS ENUM ('No_Pet', 'Crucible', 'UT_ST_Only', 'Duo');

-- AlterTable
ALTER TABLE "Character" ADD COLUMN     "modifiers" "Modifiers"[];
