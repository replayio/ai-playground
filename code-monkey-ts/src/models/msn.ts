import { BaseChatModel } from '@langchain/core/language_models/chat_models';
import { ChatAnthropic } from '@langchain/anthropic';
import { ChatOpenAI } from '@langchain/openai';
import { ChatOllama } from '@langchain/community/chat_models/ollama';
import { ChatFireworks } from '@langchain/community/chat_models/fireworks';

type ChatModelConstructor = (modelName: string, extraFlags: Record<string, string | boolean> | null) => BaseChatModel;

function constructAnthropic(modelName: string, extraFlags: Record<string, string | boolean> | null): BaseChatModel {
    if (!modelName) {
        modelName = "claude-3-sonnet-20240229";
    }
    return new ChatAnthropic({ modelName, ...(extraFlags && { defaultHeaders: extraFlags }) });
}

function constructOpenAI(modelName: string, extraFlags: Record<string, string | boolean> | null): BaseChatModel {
    if (!modelName) {
        modelName = "gpt-4-turbo-preview";
    }
    return new ChatOpenAI({ modelName, ...(extraFlags && { defaultHeaders: extraFlags }) });
}

function constructOllama(modelName: string, extraFlags: Record<string, string | boolean> | null): BaseChatModel {
    return new ChatOllama({ model: modelName });
}

function constructFireworks(modelName: string, extraFlags: Record<string, string | boolean> | null): BaseChatModel {
    return new ChatFireworks({ modelName, ...(extraFlags && { defaultHeaders: extraFlags }) });
}

const registry: Record<string, ChatModelConstructor> = {
    "anthropic": constructAnthropic,
    "openai": constructOpenAI,
    "ollama": constructOllama,
    "fireworks": constructFireworks,
};

function getModelServiceCtor(modelService: string): ChatModelConstructor {
    const constructor = registry[modelService];
    if (!constructor) {
        throw new Error(`Unknown model service: ${modelService}`);
    }
    return constructor;
}

class MSN {
    static fromString(msnStr: string): ChatModelConstructor {
        return getModelServiceCtor(msnStr);
    }
}

export { getModelServiceCtor, ChatModelConstructor, MSN };
