"use strict";
var __awaiter =
  (this && this.__awaiter) ||
  function (thisArg, _arguments, P, generator) {
    function adopt(value) {
      return value instanceof P
        ? value
        : new P(function (resolve) {
            resolve(value);
          });
    }
    return new (P || (P = Promise))(function (resolve, reject) {
      function fulfilled(value) {
        try {
          step(generator.next(value));
        } catch (e) {
          reject(e);
        }
      }
      function rejected(value) {
        try {
          step(generator["throw"](value));
        } catch (e) {
          reject(e);
        }
      }
      function step(result) {
        result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected);
      }
      step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
  };
Object.defineProperty(exports, "__esModule", { value: true });
exports.NewCharacterProcess = void 0;
const discord_js_1 = require("discord.js");
const constants_1 = require("../constants");
const util_1 = require("../util");
class NewCharacterProcess {
  constructor(user, message) {
    this.user = user;
    this.message = message;
    this.state = {};
  }
  start() {
    return __awaiter(this, void 0, void 0, function* () {
      yield this.doSelectClassMenu();
    });
  }
  doSelectClassMenu() {
    return __awaiter(this, void 0, void 0, function* () {
      const menuCustomId = (0, util_1.buildProcessCustomId)(
        NewCharacterProcess.name,
        "selectClassMenu"
      );
      const selectClassMenu = new discord_js_1.StringSelectMenuBuilder()
        .setCustomId(menuCustomId)
        .setPlaceholder("Select a class.")
        .setMinValues(1)
        .setMaxValues(1)
        .addOptions(
          ...constants_1.ROTMG_CLASSES.map((c) =>
            new discord_js_1.StringSelectMenuOptionBuilder().setLabel(c).setValue(c)
          )
        );
      const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();
      yield this.message.edit({
        content: "Choose your new character's class:",
        components: [
          new discord_js_1.ActionRowBuilder().addComponents(selectClassMenu),
          new discord_js_1.ActionRowBuilder().addComponents(cancelButton),
        ],
      });
      let response;
      try {
        response = yield this.message.awaitMessageComponent({
          filter: (i) =>
            (i.customId === menuCustomId || i.customId === cancelButtonCustomId) &&
            i.user.id === this.user.id,
          time: constants_1.DEFAULT_TIMEOUT_MS,
        });
        if (response.customId === cancelButtonCustomId) {
          return yield this.cancel();
        }
        yield response.deferUpdate();
      } catch (e) {
        return yield this.cancel();
      }
      this.state = Object.assign(Object.assign({}, this.state), {
        selectedClass: response.values[0],
      });
      return yield this.doSelectModiferMenu();
    });
  }
  doSelectModiferMenu() {
    var _a;
    return __awaiter(this, void 0, void 0, function* () {
      const menuCustomId = (0, util_1.buildProcessCustomId)(
        NewCharacterProcess.name,
        "selectModfierMenu"
      );
      const selectModiferMenu = new discord_js_1.StringSelectMenuBuilder()
        .setCustomId(menuCustomId)
        .setPlaceholder("Select modifiers (optional).")
        .setMinValues(0)
        .setMaxValues(constants_1.CHARACTER_MODIFIERS.length)
        .addOptions(
          ...constants_1.CHARACTER_MODIFIERS.map((m) =>
            new discord_js_1.StringSelectMenuOptionBuilder().setLabel(m).setValue(m)
          )
        );
      const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();
      yield this.message.edit({
        content: `Choose modifiers for your new ${this.state.selectedClass}. These are **OPTIONAL**:`,
        components: [
          new discord_js_1.ActionRowBuilder().addComponents(selectModiferMenu),
          new discord_js_1.ActionRowBuilder().addComponents(cancelButton),
        ],
      });
      let response;
      try {
        response = yield this.message.awaitMessageComponent({
          filter: (i) =>
            (i.customId === menuCustomId || i.customId === cancelButtonCustomId) &&
            i.user.id === this.user.id,
          time: constants_1.DEFAULT_TIMEOUT_MS,
        });
        if (response.customId === cancelButtonCustomId) {
          return yield this.cancel();
        }
        yield response.deferUpdate();
      } catch (e) {
        return yield this.cancel();
      }
      this.state = Object.assign(Object.assign({}, this.state), {
        selectedModifiers: (_a = response.values) !== null && _a !== void 0 ? _a : [],
      });
      return this.doConfirm();
    });
  }
  doConfirm() {
    return __awaiter(this, void 0, void 0, function* () {
      if (this.state.selectedClass === undefined || this.state.selectedModifiers === undefined) {
        return yield this.cancel("unknown");
      }
      const confirmButtonCustomId = (0, util_1.buildProcessCustomId)(
        NewCharacterProcess.name,
        "confirmButton"
      );
      const confirmButton = new discord_js_1.ButtonBuilder()
        .setCustomId(confirmButtonCustomId)
        .setLabel("Confirm")
        .setStyle(discord_js_1.ButtonStyle.Success);
      const { cancelButton, cancelButtonCustomId } = this.buildCancelButton();
      yield this.message.edit({
        content: `Creating character:\n**Class:** ${this.state.selectedClass}\n**Modifiers:** ${this.state.selectedModifiers}`,
        components: [
          new discord_js_1.ActionRowBuilder().addComponents(confirmButton, cancelButton),
        ],
      });
      let response;
      try {
        response = yield this.message.awaitMessageComponent({
          filter: (i) =>
            (i.customId === confirmButtonCustomId || i.customId === cancelButtonCustomId) &&
            i.user.id === this.user.id,
          time: constants_1.DEFAULT_TIMEOUT_MS,
        });
        if (response.customId === cancelButtonCustomId) {
          return yield this.cancel();
        }
        yield response.deferUpdate();
      } catch (e) {
        return yield this.cancel("timeout");
      }
      // TODO: create character
      return yield this.message.edit({
        content: `Created character:\n**Class:** ${this.state.selectedClass}\n**Modifiers:** ${this.state.selectedModifiers}`,
        components: [],
      });
    });
  }
  cancel(reason) {
    return __awaiter(this, void 0, void 0, function* () {
      let reasonMessage = "Cancelled.";
      switch (reason) {
        case "button":
          reasonMessage = "Cancelled.";
          break;
        case "timeout":
          reasonMessage = "Cancelled due to timeout.";
          break;
        case "unknown":
          reasonMessage = "Cancelled because something went wrong.";
          break;
      }
      yield this.message.edit({
        content: reasonMessage,
        components: [],
      });
    });
  }
  buildCancelButton() {
    const cancelButtonCustomId = (0, util_1.buildProcessCustomId)(
      NewCharacterProcess.name,
      "cancelButton"
    );
    const cancelButton = new discord_js_1.ButtonBuilder()
      .setCustomId(cancelButtonCustomId)
      .setLabel("Cancel")
      .setStyle(discord_js_1.ButtonStyle.Danger);
    return {
      cancelButton,
      cancelButtonCustomId,
    };
  }
}
exports.NewCharacterProcess = NewCharacterProcess;
