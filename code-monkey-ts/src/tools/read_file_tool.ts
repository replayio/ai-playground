import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

const readFile = promisify(fs.readFile);

interface ReadFileResult {
    success: boolean;
    content?: string;
    message?: string;
}

async function readFileContent(filePath: string): Promise<ReadFileResult> {
    try {
        const absolutePath = path.resolve(filePath);
        const fileContent = await readFile(absolutePath, 'utf8');
        return {
            success: true,
            content: fileContent,
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

export { readFileContent, ReadFileResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 3) {
            console.error('Usage: node read_file_tool.js <file_path>');
            process.exit(1);
        }

        const [, , filePath] = process.argv;
        const result = await readFileContent(filePath);
        if (result.success) {
            console.log(result.content);
        } else {
            console.error(result.message);
        }
        process.exit(result.success ? 0 : 1);
    })();
}
