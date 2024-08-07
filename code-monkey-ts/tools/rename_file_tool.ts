import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const renameFile = promisify(fs.rename);

const schema = z.object({
    oldPath: z.string().describe("The current path of the file to be renamed"),
    newPath: z.string().describe("The new path/name for the file"),
});

export const renameFileTool = tool(
    async ({ oldPath, newPath }: z.infer<typeof schema>) => {
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
                message: `Error: ${(error as Error).message}`,
            };
        }
    },
    {
        name: "rename_file",
        description: "Rename a file from old path to new path",
        schema: schema,
    }
);

// Main execution
if (require.main === module) {
    (async () => {
        if (process.argv.length !== 4) {
            console.error('Usage: node rename_file_tool.js <old_path> <new_path>');
            process.exit(1);
        }

        const [, , oldPath, newPath] = process.argv;
        const result = await renameFileTool.invoke({ oldPath, newPath });
        console.log(result.message);
        process.exit(result.success ? 0 : 1);
    })();
}