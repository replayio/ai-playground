import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

interface ReplaceInFileResult {
    success: boolean;
    message: string;
}

async function replaceInFile(filePath: string, oldText: string, newText: string): Promise<ReplaceInFileResult> {
    try {
        const absolutePath = path.resolve(filePath);
        const fileContent = await readFile(absolutePath, 'utf8');
        const updatedContent = fileContent.replace(new RegExp(oldText, 'g'), newText);
        
        if (fileContent === updatedContent) {
            return {
                success: false,
                message: 'No changes were made to the file.',
            };
        }

        await writeFile(absolutePath, updatedContent, 'utf8');
        return {
            success: true,
            message: 'File updated successfully.',
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

export { replaceInFile, ReplaceInFileResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 5) {
            console.error('Usage: node replace_in_file_tool.js <file_path> <old_text> <new_text>');
            process.exit(1);
        }

        const [, , filePath, oldText, newText] = process.argv;
        const result = await replaceInFile(filePath, oldText, newText);
        console.log(result.message);
        process.exit(result.success ? 0 : 1);
    })();
}
