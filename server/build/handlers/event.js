"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = require("fs");
const path_1 = require("path");
module.exports = (client) => {
  const eventsDir = (0, path_1.join)(__dirname, "../events");
  (0, fs_1.readdirSync)(eventsDir).forEach((file) => {
    if (file.endsWith(".js")) {
      const event = require(`${eventsDir}/${file}`).default;
      if (event.once) {
        client.once(event.name, (...args) => event.execute(...args));
      } else {
        client.on(event.name, (...args) => event.execute(...args));
      }
      console.log(`Loaded event ${event.name}`);
    }
  });
};
