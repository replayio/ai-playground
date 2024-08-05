import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

interface ImportResult {
    success: boolean;
    message: string;
}

async function addImport(filePath: string, importStatement: string): Promise<ImportResult> {
    try {
        const absolutePath = path.resolve(filePath);
        let fileContent = await readFile(absolutePath, 'utf8');

        // Check if the import already exists
        if (fileContent.includes(importStatement)) {
            return {
                success: false,
                message: 'Import already exists in the file.',
            };
        }

        // Add the import statement at the beginning of the file
        fileContent = importStatement + '\n' + fileContent;

        await writeFile(absolutePath, fileContent, 'utf8');
        return {
            success: true,
            message: 'Import added successfully.',
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
        };
    }
}

export { addImport, ImportResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: node ca_imports_tool.js <file_path> <import_statement>');
            process.exit(1);
        }

        const [, , filePath, importStatement] = process.argv;
        const result = await addImport(filePath, importStatement);
        console.log(result.message);
        process.exit(result.success ? 0 : 1);
    })();
}
