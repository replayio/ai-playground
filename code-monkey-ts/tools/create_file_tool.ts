import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);

interface CreateFileResult {
    success: boolean;
    message: string;
}

async function createFileTool(filePath: string, content: string): Promise<CreateFileResult> {
    try {
        const absolutePath = path.resolve(filePath);
        const dirPath = path.dirname(absolutePath);

        // Create directory if it doesn't exist
        await mkdir(dirPath, { recursive: true });

        // Write file content
        await writeFile(absolutePath, content, 'utf8');

        return {
            success: true,
            message: 'File created successfully.',
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

export { createFileTool, CreateFileResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: node create_file_tool.js <file_path> <content>');
            process.exit(1);
        }

        const [, , filePath, content] = process.argv;
        const result = await createFileTool(filePath, content);
        console.log(result.message);
        process.exit(result.success ? 0 : 1);
    })();
}
