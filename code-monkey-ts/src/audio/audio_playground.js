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
exports.playAudio = playAudio;
exports.recordAndTranscribe = recordAndTranscribe;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const util_1 = require("util");
const child_process_1 = require("child_process");
const audio_recording_1 = require("./audio_recording");
const audio_transcriber_1 = require("./audio_transcriber");
const readFile = (0, util_1.promisify)(fs.readFile);
const writeFile = (0, util_1.promisify)(fs.writeFile);
const execAsync = (0, util_1.promisify)(child_process_1.exec);
function playAudio(filePath) {
    return __awaiter(this, void 0, void 0, function* () {
        const absolutePath = path.resolve(filePath);
        const command = `aplay ${absolutePath}`;
        yield execAsync(command);
    });
}
function recordAndTranscribe(duration, outputPath) {
    return __awaiter(this, void 0, void 0, function* () {
        const recordingResult = yield (0, audio_recording_1.recordAudio)(duration, outputPath);
        if (!recordingResult.success || !recordingResult.filePath) {
            throw new Error(`Recording failed: ${recordingResult.error}`);
        }
        const transcriptionResult = yield (0, audio_transcriber_1.transcribeAudio)(recordingResult.filePath);
        if (!transcriptionResult.success || !transcriptionResult.transcription) {
            throw new Error(`Transcription failed: ${transcriptionResult.error}`);
        }
        return transcriptionResult.transcription;
    });
}
// Main execution
if (require.main === module) {
    (() => __awaiter(void 0, void 0, void 0, function* () {
        if (process.argv.length !== 4) {
            console.error('Usage: node audio_playground.js <duration_in_seconds> <output_file_path>');
            process.exit(1);
        }
        const [, , durationStr, outputPath] = process.argv;
        const duration = parseInt(durationStr, 10);
        if (isNaN(duration) || duration <= 0) {
            console.error('Error: Duration must be a positive integer.');
            process.exit(1);
        }
        try {
            console.log('Recording audio...');
            const transcription = yield recordAndTranscribe(duration, outputPath);
            console.log('Transcription:', transcription);
            console.log('Playing back the recorded audio...');
            yield playAudio(outputPath);
            console.log('Audio playground demo completed successfully.');
        }
        catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    }))();
}
