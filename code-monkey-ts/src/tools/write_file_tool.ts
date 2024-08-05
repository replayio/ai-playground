import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

const writeFile = promisify(fs.writeFile);

interface WriteFileResult {
    success: boolean;
    message: string;
}

async function writeFileTool(filePath: string, content: string): Promise<WriteFileResult> {
    try {
        const absolutePath = path.resolve(filePath);
        await writeFile(absolutePath, content, 'utf8');
        return {
            success: true,
            message: 'File written successfully.',
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

export { writeFileTool, WriteFileResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: node write_file_tool.js <file_path> <content>');
            process.exit(1);
        }

        const [, , filePath, content] = process.argv;
        const result = await writeFileTool(filePath, content);
        console.log(result.message);
        process.exit(result.success ? 0 : 1);
    })();
}
