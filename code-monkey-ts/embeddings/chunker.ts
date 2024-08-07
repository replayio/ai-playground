import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { isError, getErrorMessage } from '../utils/error_handling';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

interface Chunk {
    start: number;
    end: number;
    text: string;
}

class Chunker {
    private chunkSize: number;

    constructor(chunkSize: number) {
        this.chunkSize = chunkSize;
    }

    async chunkFile(filePath: string): Promise<Chunk[]> {
        const content = await readFile(filePath, 'utf-8');
        return this.chunkText(content);
    }

    chunkText(text: string): Chunk[] {
        const chunks: Chunk[] = [];
        let start = 0;

        while (start < text.length) {
            const end = Math.min(start + this.chunkSize, text.length);
            const chunkText = text.slice(start, end);
            chunks.push({ start, end, text: chunkText });
            start = end;
        }

        return chunks;
    }

    async saveChunks(chunks: Chunk[], outputDir: string): Promise<void> {
        await fs.promises.mkdir(outputDir, { recursive: true });

        for (const chunk of chunks) {
            const chunkPath = path.join(outputDir, `chunk_${chunk.start}_${chunk.end}.txt`);
            await writeFile(chunkPath, chunk.text, 'utf-8');
        }
    }
}

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 5) {
            console.error('Usage: ts-node chunker.ts <file_path> <chunk_size> <output_dir>');
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
            const chunks = await chunker.chunkFile(filePath);
            await chunker.saveChunks(chunks, outputDir);
            console.log('Chunks saved successfully.');
        } catch (error) {
            console.error('Error:', getErrorMessage(error));
            process.exit(1);
        }
    })();
}

export { Chunker, Chunk };
