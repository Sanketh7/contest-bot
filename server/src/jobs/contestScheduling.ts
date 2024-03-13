import { refreshContestSchedule } from "../services/contestService";
import { Job } from "../types";

export const contestScheduleJob: Job = {
  schedule: { second: 0 }, // once a minute
  async onTick() {
    await refreshContestSchedule();
  },
};
