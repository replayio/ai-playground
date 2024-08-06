"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getModelServiceCtor = getModelServiceCtor;
const @langchain/anthropic_1 = require("@langchain/anthropic");
const @langchain/ollama_1 = require("@langchain/ollama");
const @langchain/fireworks_1 = require("@langchain/fireworks");
function constructAnthropic(modelName, extraFlags) {
    if (!modelName) {
        modelName = "claude-3-5-sonnet-20240620";
    }
    return new @langchain/anthropic_1.ChatAnthropic({ modelName, defaultHeaders: extraFlags });
}
function constructOpenAI(modelName, extraFlags) {
    throw new Error("TODO: add model");
    // return new ChatOpenAI({ modelName, defaultHeaders: extraFlags });
}
function constructOllama(modelName, extraFlags) {
    return new @langchain/ollama_1.ChatOllama({ model: modelName });
}
function constructFireworks(modelName, extraFlags) {
    return new @langchain/fireworks_1.ChatFireworks({ model: modelName, defaultHeaders: extraFlags });
}
const registry = {
    "anthropic": constructAnthropic,
    "openai": constructOpenAI,
    "ollama": constructOllama,
    "fireworks": constructFireworks,
};
function getModelServiceCtor(modelService) {
    if (!(modelService in registry)) {
        throw new Error(`Unknown model service: ${modelService}`);
    }
    return registry[modelService];
}
