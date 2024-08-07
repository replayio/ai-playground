import { BaseChatModel } from "@langchain/core/language_models/chat_models";

// Assuming ChatModelConstructor is defined elsewhere
import { ChatModelConstructor, getModelServiceCtor } from './registry';

// MSN is similar to a DSN ("Data Source Name" used to identify databases) to specify a model api service,
// a model name/variant, and any extra flags.
//
// syntax is: service[/model[/flags]]
//
// where flags is a comma separated list of key=value pairs
class MSN {
    constructor(
        public chatModelCtor: ChatModelConstructor,
        public modelName: string,
        public flags: Record<string, string>
    ) {}

    static fromString(msnStr: string): MSN {
        const splitMsn = msnStr.split("/", 3);
        const splitLen = splitMsn.length;

        if (splitLen < 2) {
            throw new Error(`MSN must have at least a service and model name: ${msnStr}`);
        }

        const chatModelCtor = getModelServiceCtor(splitMsn[0]);
        const modelName = splitMsn[1];
        const flags = splitLen >= 3 ? parseFlags(splitMsn[2], msnStr) : {};

        return new MSN(chatModelCtor, modelName, flags);
    }

    constructModel(): BaseChatModel {
        return this.chatModelCtor(this.modelName, this.flags);
    }
}

function parseFlags(flags: string, sourceMsnStr: string): Record<string, string> {
    // parse the flags into a dict based on k=v pairs (split on the first `=`).
    const flagsDict: Record<string, string> = {};
    for (const flag of flags.split(",")) {
        const [k, v] = flag.split("=", 2);
        if (v === undefined) {
            throw new Error(`MSN flag ${k} must have a value: ${sourceMsnStr}`);
        }
        flagsDict[k] = v;
    }
    return flagsDict;
}

export { MSN, parseFlags };