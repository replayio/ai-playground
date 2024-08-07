/**
 * Formats the time difference between the current time and a start time into a string with seconds.
 * @param start The start time in seconds.
 * @returns A string representing the time difference in seconds, rounded to two decimal places.
 */
export function formatSecondsDelta(start: number): string {
    return `${(Date.now() / 1000 - start).toFixed(2)}s`;
}
