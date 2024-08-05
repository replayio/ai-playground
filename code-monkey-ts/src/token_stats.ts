import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

const readFile = promisify(fs.readFile);

interface TokenStats {
    totalTokens: number;
    uniqueTokens: number;
    tokenFrequencies: { [token: string]: number };
}

async function calculateTokenStats(filePath: string): Promise<TokenStats> {
    const content = await readFile(filePath, 'utf-8');
    const tokens = content.split(/\s+/);
    const tokenFrequencies: { [token: string]: number } = {};

    tokens.forEach(token => {
        tokenFrequencies[token] = (tokenFrequencies[token] || 0) + 1;
    });

    return {
        totalTokens: tokens.length,
        uniqueTokens: Object.keys(tokenFrequencies).length,
        tokenFrequencies,
    };
}

export { calculateTokenStats, TokenStats };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 3) {
            console.error('Usage: node token_stats.js <file_path>');
            process.exit(1);
        }

        const [, , filePath] = process.argv;
        try {
            const stats = await calculateTokenStats(filePath);
            console.log('Total Tokens:', stats.totalTokens);
            console.log('Unique Tokens:', stats.uniqueTokens);
            console.log('Token Frequencies:', stats.tokenFrequencies);
        } catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    })();
}
