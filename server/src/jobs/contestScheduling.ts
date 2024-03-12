import { getActiveContest, shouldContestEnd } from "../services/contestService";
import { Job } from "../types";

export const contestScheduleJob: Job = {
  schedule: { second: 0 }, // once a minute
  async onTick() {
    const contest = await getActiveContest();
    if (contest) {
      if (shouldContestEnd(contest)) {
      }
    } else {
    }
  },
};
