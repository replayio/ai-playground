import { BaseTool } from '@langchain/core/tools';
import { ASTParser } from '../deps';

interface CAToolOptions {
    parser?: ASTParser;
}

export class CATool extends BaseTool {
    parser: ASTParser;

    constructor(options: CAToolOptions = {}) {
        super();
        this.parser = options.parser || new ASTParser();
    }
}
