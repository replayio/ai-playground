import { BaseChatModel } from '@langchain/core/language_models/chat_models';
import { ChatAnthropic } from '@langchain/anthropic';
import { ChatOpenAI } from '@langchain/openai';
// import { ChatOllama } from '@langchain/ollama';
// import { ChatFireworks } from '@langchain/fireworks';

type ChatModelConstructor = (modelName: string, extraFlags: { [key: string]: string | boolean } | null) => BaseChatModel;

function constructAnthropic(modelName: string, extraFlags: { [key: string]: string | boolean } | null): BaseChatModel {
    if (!modelName) {
        modelName = "claude-3-5-sonnet-20240620";
    }
    return new ChatAnthropic({ modelName, ...(extraFlags || {}) });
}

function constructOpenAI(modelName: string, extraFlags: { [key: string]: string | boolean } | null): BaseChatModel {
    throw new Error("TODO: add model");
    // return new ChatOpenAI({ modelName, defaultHeaders: extraFlags });
}

// function constructOllama(modelName: string, extraFlags: { [key: string]: string | boolean } | null): BaseChatModel {
//     return new ChatOllama({ model: modelName });
// }

// function constructFireworks(modelName: string, extraFlags: { [key: string]: string | boolean } | null): BaseChatModel {
//     return new ChatFireworks({ model: modelName, defaultHeaders: extraFlags });
// }

const registry: { [key: string]: ChatModelConstructor } = {
    "anthropic": constructAnthropic,
    "openai": constructOpenAI,
    // "ollama": constructOllama,
    // "fireworks": constructFireworks,
};

function getModelServiceCtor(modelService: string): ChatModelConstructor {
    if (!(modelService in registry)) {
        throw new Error(`Unknown model service: ${modelService}`);
    }
    return registry[modelService];
}

export { getModelServiceCtor, ChatModelConstructor };
