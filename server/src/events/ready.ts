import { Client } from "discord.js";
import * as schedule from "node-schedule";
import { contestScheduleJob } from "../jobs/contestScheduling";
import { Event } from "../types";

const event: Event = {
  name: "ready",
  once: true,
  async execute(client: Client) {
    console.log(`${client.user?.tag} connected`);
    schedule.scheduleJob(contestScheduleJob.schedule, contestScheduleJob.onTick);
  },
};

export default event;
