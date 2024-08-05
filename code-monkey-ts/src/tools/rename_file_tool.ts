import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

const renameFile = promisify(fs.rename);

interface RenameFileResult {
    success: boolean;
    message: string;
}

async function renameFileTool(oldPath: string, newPath: string): Promise<RenameFileResult> {
    try {
        const absoluteOldPath = path.resolve(oldPath);
        const absoluteNewPath = path.resolve(newPath);

        await renameFile(absoluteOldPath, absoluteNewPath);
        return {
            success: true,
            message: 'File renamed successfully.',
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

export { renameFileTool, RenameFileResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: node rename_file_tool.js <old_path> <new_path>');
            process.exit(1);
        }

        const [, , oldPath, newPath] = process.argv;
        const result = await renameFileTool(oldPath, newPath);
        console.log(result.message);
        process.exit(result.success ? 0 : 1);
    })();
}
