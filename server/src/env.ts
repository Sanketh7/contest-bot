import * as dotenv from "dotenv";
import { cleanEnv, str, url } from "envalid";
dotenv.config();

export const ENV = cleanEnv(process.env, {
  DATABASE_URL: url(),
  DIRECT_URL: url(),
  DISCORD_TOKEN: str(),
  OWNER_USER_ID: str(),
});
