import { BaseChatModel } from "@langchain/core/language_models/chat_models";
import { ChatAnthropic } from "@langchain/anthropic";
import { ChatOpenAI } from "@langchain/openai";
// import { ChatOllama } from "@langchain/ollama";
// import { ChatFireworks } from "@langchain/fireworks";

export type ChatModelConstructor = (
  modelName: string,
  extraFlags: Record<string, string>,
) => BaseChatModel;

function constructAnthropic(
  modelName: string,
  extra_flags: Record<string, string>,
): BaseChatModel {
  return new ChatAnthropic({
    model: modelName,
    clientOptions: extra_flags, // unclear if this is clientOptions or if we should splat extra_flags into the object
  });
}

function constructOpenai(
  modelName: string,
  extra_flags: Record<string, string>,
): BaseChatModel {
  return new ChatOpenAI({ model: modelName, modelKwargs: extra_flags });
}

function constructOllama(
  modelName: string,
  extra_flags: Record<string, string>,
): BaseChatModel {
  // return new ChatOllama(modelName);
  throw new Error("Not implemented");
}

function constructFireworks(
  modelName: string,
  extra_flags: Record<string, string>,
): BaseChatModel {
  // return new ChatFireworks(modelName);
  throw new Error("Not implemented");
}

const registry: Record<string, ChatModelConstructor> = {
  anthropic: constructAnthropic,
  openai: constructOpenai,
  ollama: constructOllama,
  fireworks: constructFireworks,
};

export function get_model_service_ctor(
  modelService: string,
): ChatModelConstructor {
  if (!(modelService in registry)) {
    throw new Error(`Unknown model service: ${modelService}`);
  }
  return registry[modelService];
}
