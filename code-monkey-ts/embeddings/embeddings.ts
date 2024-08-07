import * as fs from 'fs/promises';
import * as path from 'path';
import { Chunker, Chunk } from './chunker';

interface Embedding {
    vector: number[];
    text: string;
    metadata: {
        start: number;
        end: number;
    };
}

interface EmbeddingModel {
    embed(text: string): Promise<number[]>;
}

class Embedder {
    private model: EmbeddingModel;

    constructor(model: EmbeddingModel) {
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
        await fs.writeFile(outputPath, JSON.stringify(embeddings, null, 2), 'utf-8');
    }

    async loadEmbeddings(inputPath: string): Promise<Embedding[]> {
        const content = await fs.readFile(inputPath, 'utf-8');
        return JSON.parse(content) as Embedding[];
    }
}

export { Embedder, Embedding, EmbeddingModel };

// Main execution
if (typeof require !== 'undefined' && require.main === module) {
    (async () => {
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
            const model: EmbeddingModel = {
                embed: async (text: string) => {
                    // Placeholder implementation
                    return new Array(128).fill(0);
                }
            };
            const embedder = new Embedder(model);
            const embeddings = await embedder.embedFile(filePath, chunkSize);
            await embedder.saveEmbeddings(embeddings, outputPath);
            console.log('Embeddings saved successfully.');
        } catch (error) {
            console.error('Error:', (error as Error).message);
            process.exit(1);
        }
    })();
}
