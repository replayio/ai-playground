import time
from constants import CLAUDE_RATE_LIMIT

class TokenStats:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.last_request_time = 0
        self.tokens_in_last_minute = 0

    def update(self, input_tokens: int, output_tokens: int):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        current_time = time.time()
        if current_time - self.last_request_time >= 60:
            self.tokens_in_last_minute = input_tokens + output_tokens
        else:
            self.tokens_in_last_minute += input_tokens + output_tokens

        self.last_request_time = current_time

    def check_rate_limit(self):
        if self.tokens_in_last_minute >= CLAUDE_RATE_LIMIT:
            sleep_time = 60 - (time.time() - self.last_request_time)
            if sleep_time > 0:
                print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
            self.tokens_in_last_minute = 0

    def print_stats(self):
        print("\nToken Statistics:")
        print(f"Total input tokens: {self.total_input_tokens}")
        print(f"Total output tokens: {self.total_output_tokens}")