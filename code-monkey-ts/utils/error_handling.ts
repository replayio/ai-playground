export function isError(error: unknown): error is Error {
    return error instanceof Error;
}

export function getErrorMessage(error: unknown): string {
    return isError(error) ? error.message : 'Unknown error';
}
