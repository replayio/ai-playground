import { Database } from 'sqlite3';
import { promisify } from 'util';

export class AsyncSqliteSaver {
    private db: Database;

    constructor(dbPath = ':memory:') {
        this.db = new Database(dbPath);
    }

    async save(threadId: string, content: string): Promise<void> {
        const stmt = this.db.prepare('INSERT INTO threads (thread_id, content) VALUES (?, ?)');
        const run = promisify<string, string, void>(stmt.run.bind(stmt));

        try {
            await run(threadId, content);
        } catch (error) {
            console.error('Error saving to database:', error);
            throw error;
        } finally {
            stmt.finalize();
        }
    }

    async close(): Promise<void> {
        return new Promise((resolve, reject) => {
            this.db.close((err: Error | null) => {
                if (err) {
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }
}
