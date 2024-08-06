declare module 'pathspec' {
  export class GitIgnoreSpec {
    constructor(patterns: string[]);
    static from_lines(lines: string[]): GitIgnoreSpec;
    match_files(files: string[]): string[];
  }
}
