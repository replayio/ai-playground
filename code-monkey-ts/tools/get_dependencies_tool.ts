import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { exec } from 'child_process';

const readFile = promisify(fs.readFile);
const execAsync = promisify(exec);

interface DependencyResult {
    success: boolean;
    dependencies?: string[];
    error?: string;
}

async function getDependencies(filePath: string): Promise<DependencyResult> {
    try {
        const absolutePath = path.resolve(filePath);
        const fileContent = await readFile(absolutePath, 'utf8');

        // Use a simple regex to find import statements
        const importRegex = /import\s+.*?from\s+['"](.+?)['"]/g;
        const dependencies: string[] = [];
        let match;

        while ((match = importRegex.exec(fileContent)) !== null) {
            dependencies.push(match[1]);
        }

        // Use pipreqs to get Python dependencies
        const { stdout } = await execAsync(`pipreqs --print ${path.dirname(absolutePath)}`);
        const pipDependencies = stdout.trim().split('\n');

        return {
            success: true,
            dependencies: [...dependencies, ...pipDependencies],
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
        };
    }
}

export { getDependencies, DependencyResult };

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 3) {
            console.error('Usage: node get_dependencies_tool.js <file_path>');
            process.exit(1);
        }

        const [, , filePath] = process.argv;
        const result = await getDependencies(filePath);

        if (result.success) {
            console.log('Dependencies:');
            result.dependencies?.forEach(dep => console.log(dep));
        } else {
            console.error('Error:', result.error);
        }

        process.exit(result.success ? 0 : 1);
    })();
}
