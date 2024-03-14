import * as dotenv from "dotenv";
import { bool, cleanEnv, str, url } from "envalid";
dotenv.config();

export const ENV = cleanEnv(process.env, {
  DATABASE_URL: url(),
  DIRECT_URL: url(),
  DISCORD_TOKEN: str(),
  RELOAD_SLASH_COMMANDS: bool({ default: false }),
});
