// this is a test file
function main(): void {
    console.log("Hello world!");
}

// Call the main function if this file is run directly
if (require.main === module) {
    main();
}

// Add a simple Jest test
describe('main function', () => {
    it('should log "Hello world!"', () => {
        const consoleSpy = jest.spyOn(console, 'log');
        main();
        expect(consoleSpy).toHaveBeenCalledWith("Hello world!");
        consoleSpy.mockRestore();
    });
});
