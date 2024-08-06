"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CATool = void 0;
const tools_1 = require("@langchain/core/tools");
const deps_1 = require("../deps");
class CATool extends tools_1.BaseTool {
    constructor(options = {}) {
        super();
        this.parser = options.parser || new deps_1.ASTParser();
    }
}
exports.CATool = CATool;
