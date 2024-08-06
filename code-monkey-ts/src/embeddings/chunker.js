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
exports.Chunker = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const util_1 = require("util");
const readFile = (0, util_1.promisify)(fs.readFile);
const writeFile = (0, util_1.promisify)(fs.writeFile);
class Chunker {
    constructor(chunkSize) {
        this.chunkSize = chunkSize;
    }
    chunkFile(filePath) {
        return __awaiter(this, void 0, void 0, function* () {
            const content = yield readFile(filePath, 'utf-8');
            return this.chunkText(content);
        });
    }
    chunkText(text) {
        const chunks = [];
        let start = 0;
        while (start < text.length) {
            const end = Math.min(start + this.chunkSize, text.length);
            const chunkText = text.slice(start, end);
            chunks.push({ start, end, text: chunkText });
            start = end;
        }
        return chunks;
    }
    saveChunks(chunks, outputDir) {
        return __awaiter(this, void 0, void 0, function* () {
            yield fs.promises.mkdir(outputDir, { recursive: true });
            for (const chunk of chunks) {
                const chunkPath = path.join(outputDir, `chunk_${chunk.start}_${chunk.end}.txt`);
                yield writeFile(chunkPath, chunk.text, 'utf-8');
            }
        });
    }
}
exports.Chunker = Chunker;
// Main execution
if (require.main === module) {
    (() => __awaiter(void 0, void 0, void 0, function* () {
        if (process.argv.length !== 5) {
            console.error('Usage: node chunker.js <file_path> <chunk_size> <output_dir>');
            process.exit(1);
        }
        const [, , filePath, chunkSizeStr, outputDir] = process.argv;
        const chunkSize = parseInt(chunkSizeStr, 10);
        if (isNaN(chunkSize) || chunkSize <= 0) {
            console.error('Error: Chunk size must be a positive integer.');
            process.exit(1);
        }
        try {
            const chunker = new Chunker(chunkSize);
            const chunks = yield chunker.chunkFile(filePath);
            yield chunker.saveChunks(chunks, outputDir);
            console.log('Chunks saved successfully.');
        }
        catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    }))();
}
