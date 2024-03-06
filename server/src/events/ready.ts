import { Client } from "discord.js";
import { Event } from "../types";

const event: Event = {
  name: "ready",
  once: true,
  async execute(client: Client) {
    console.log(`${client.user?.tag} connected`);
  },
};

export default event;
