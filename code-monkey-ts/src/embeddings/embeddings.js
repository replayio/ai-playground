"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Embedder = void 0;
const fs = __importStar(require("fs/promises"));
const chunker_1 = require("./chunker");
class Embedder {
    constructor(model) {
        this.model = model;
    }
    embedFile(filePath, chunkSize) {
        return __awaiter(this, void 0, void 0, function* () {
            const chunker = new chunker_1.Chunker(chunkSize);
            const chunks = yield chunker.chunkFile(filePath);
            return this.embedChunks(chunks);
        });
    }
    embedText(text, chunkSize) {
        return __awaiter(this, void 0, void 0, function* () {
            const chunker = new chunker_1.Chunker(chunkSize);
            const chunks = chunker.chunkText(text);
            return this.embedChunks(chunks);
        });
    }
    embedChunks(chunks) {
        return __awaiter(this, void 0, void 0, function* () {
            const embeddings = [];
            for (const chunk of chunks) {
                const vector = yield this.model.embed(chunk.text);
                embeddings.push({
                    vector,
                    text: chunk.text,
                    metadata: {
                        start: chunk.start,
                        end: chunk.end,
                    },
                });
            }
            return embeddings;
        });
    }
    saveEmbeddings(embeddings, outputPath) {
        return __awaiter(this, void 0, void 0, function* () {
            yield fs.writeFile(outputPath, JSON.stringify(embeddings, null, 2), 'utf-8');
        });
    }
    loadEmbeddings(inputPath) {
        return __awaiter(this, void 0, void 0, function* () {
            const content = yield fs.readFile(inputPath, 'utf-8');
            return JSON.parse(content);
        });
    }
}
exports.Embedder = Embedder;
// Main execution
if (typeof require !== 'undefined' && require.main === module) {
    (() => __awaiter(void 0, void 0, void 0, function* () {
        const args = process.argv.slice(2);
        if (args.length !== 3) {
            console.error('Usage: ts-node embeddings.ts <file_path> <chunk_size> <output_path>');
            process.exit(1);
        }
        const [filePath, chunkSizeStr, outputPath] = args;
        const chunkSize = parseInt(chunkSizeStr, 10);
        if (isNaN(chunkSize) || chunkSize <= 0) {
            console.error('Error: Chunk size must be a positive integer.');
            process.exit(1);
        }
        try {
            // Note: You need to implement or import the actual embedding model
            const model = {
                embed: (text) => __awaiter(void 0, void 0, void 0, function* () {
                    // Placeholder implementation
                    return new Array(128).fill(0);
                })
            };
            const embedder = new Embedder(model);
            const embeddings = yield embedder.embedFile(filePath, chunkSize);
            yield embedder.saveEmbeddings(embeddings, outputPath);
            console.log('Embeddings saved successfully.');
        }
        catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    }))();
}
