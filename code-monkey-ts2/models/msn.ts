import { BaseChatModel } from "@langchain/core/language_models/chat_models";
import { ChatModelConstructor, get_model_service_ctor } from "./registry";


// MSN is simile to a DSN ("Data Source Name" used to identify databases) to specify a model api service,
// a model name/variant, and any extra flags.
//
// syntax is: service[/model[/flags]]
//
// where flags is a comma separated list of key=value pairs
export class MSN {
    private constructor(
        public chat_model_ctor: ChatModelConstructor,
        public modelName: string,
        public flags: Record<string, string>,
    ) {}

    static from_string(msn_str: string): MSN {
        const split_msn = msn_str.split("/", 2)
        const split_len = split_msn.length

        if (split_len < 2) {
            throw new Error(
                `MSN must have at least a service and model name: ${msn_str}`
            );
        }

        const chat_model_ctor = get_model_service_ctor(split_msn[0]);
        const model_name = split_msn[1];
        const flags = split_len >= 3 ? parseFlags(split_msn[2], msn_str) : {}

        return new MSN(chat_model_ctor, model_name, flags)
    }

    constructModel(): BaseChatModel {
        return this.chat_model_ctor(this.modelName, this.flags)
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