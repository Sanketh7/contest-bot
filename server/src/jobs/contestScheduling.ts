import { getActiveContest, refreshContestSchedule } from "../services/contestService";
import {
  cleanLeaderboardChannel,
  displayTopCharactersLeaderboard,
} from "../services/leaderboardService";
import { Job } from "../types";

export const contestScheduleJob: Job = {
  schedule: { second: 0 }, // once a minute
  async onTick() {
    await refreshContestSchedule();
  },
};

export const refreshLeaderboardJob: Job = {
  schedule: "0 */2 * * * *", // every 2 minutes
  async onTick() {
    const contest = await getActiveContest();
    if (contest) {
      await cleanLeaderboardChannel();
      await displayTopCharactersLeaderboard(contest, "all");
      await displayTopCharactersLeaderboard(contest, "active");
    }
  },
};
