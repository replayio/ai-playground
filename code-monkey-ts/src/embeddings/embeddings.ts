import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { Chunker, Chunk } from './chunker';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

interface Embedding {
    vector: number[];
    text: string;
    metadata: {
        start: number;
        end: number;
    };
}

class Embedder {
    private model: any; // Replace 'any' with the actual type of the embedding model

    constructor(model: any) {
        this.model = model;
    }

    async embedFile(filePath: string, chunkSize: number): Promise<Embedding[]> {
        const chunker = new Chunker(chunkSize);
        const chunks = await chunker.chunkFile(filePath);
        return this.embedChunks(chunks);
    }

    async embedText(text: string, chunkSize: number): Promise<Embedding[]> {
        const chunker = new Chunker(chunkSize);
        const chunks = chunker.chunkText(text);
        return this.embedChunks(chunks);
    }

    private async embedChunks(chunks: Chunk[]): Promise<Embedding[]> {
        const embeddings: Embedding[] = [];

        for (const chunk of chunks) {
            const vector = await this.model.embed(chunk.text);
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
    }

    async saveEmbeddings(embeddings: Embedding[], outputPath: string): Promise<void> {
        await writeFile(outputPath, JSON.stringify(embeddings, null, 2), 'utf-8');
    }

    async loadEmbeddings(inputPath: string): Promise<Embedding[]> {
        const content = await readFile(inputPath, 'utf-8');
        return JSON.parse(content) as Embedding[];
    }
}

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 5) {
            console.error('Usage: node embeddings.js <file_path> <chunk_size> <output_path>');
            process.exit(1);
        }

        const [, , filePath, chunkSizeStr, outputPath] = process.argv;
        const chunkSize = parseInt(chunkSizeStr, 10);

        if (isNaN(chunkSize) || chunkSize <= 0) {
            console.error('Error: Chunk size must be a positive integer.');
            process.exit(1);
        }

        try {
            // Note: You need to implement or import the actual embedding model
            const model = null; // Replace with actual model initialization
            const embedder = new Embedder(model);
            const embeddings = await embedder.embedFile(filePath, chunkSize);
            await embedder.saveEmbeddings(embeddings, outputPath);
            console.log('Embeddings saved successfully.');
        } catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    })();
}

export { Embedder, Embedding };
