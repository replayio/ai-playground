import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

const unlink = promisify(fs.unlink);

interface DeleteFileResult {
    success: boolean;
    message: string;
}

async function deleteFile(filePath: string): Promise<DeleteFileResult> {
    try {
        const absolutePath = path.resolve(filePath);
        await unlink(absolutePath);
        return {
            success: true,
            message: `File ${filePath} deleted successfully.`,
        };
    } catch (error) {
        return {
            success: false,
            message: `Error deleting file ${filePath}: ${error.message}`,
        };
    }
}

export { deleteFile, DeleteFileResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 3) {
            console.error('Usage: node delete_file_tool.js <file_path>');
            process.exit(1);
        }

        const [, , filePath] = process.argv;
        const result = await deleteFile(filePath);
        console.log(result.message);
        process.exit(result.success ? 0 : 1);
    })();
}
