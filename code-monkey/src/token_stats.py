import time
from collections import deque, Counter
from constants import CLAUDE_RATE_LIMIT
from anthropic.types import ContentBlock
from typing import List
from instrumentation import tracer

TOP_N = 5

class TokenStats:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.token_history = deque()
        self.message_type_histogram = Counter()

    def update(
        self,
        input_tokens: int,
        output_tokens: int,
        message_contents: List[ContentBlock],
    ):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        current_time = time.time()
        self.token_history.append((current_time, input_tokens + output_tokens))

        # Remove entries older than 1 minute
        while self.token_history and current_time - self.token_history[0][0] > 60:
            self.token_history.popleft()

        # Update histograms
        type_label = "+".join(sorted(
            [f"{m.type}.{m.name}" if hasattr(m, 'name') and m.name else m.type 
             for m in message_contents]
        ))
        self.message_type_histogram[type_label] += input_tokens + output_tokens

    def check_rate_limit(self):
        if not self.token_history:
            return

        current_time = time.time()
        tokens_in_last_minute = sum(tokens for _, tokens in self.token_history)

        if tokens_in_last_minute >= CLAUDE_RATE_LIMIT:
            oldest_time = self.token_history[0][0]
            sleep_time = 60 - (current_time - oldest_time)
            if sleep_time > 0:
                print(
                    f"💤 Rate limit reached ({tokens_in_last_minute}/min). Sleeping for {sleep_time:.2f} seconds..."
                )
                with tracer().start_as_current_span("rate_limit_avoidance") as span:
                    span.set_attribute("tokens_in_last_minute", tokens_in_last_minute)
                    time.sleep(sleep_time)

    def print_stats(self):
        print("\nToken Statistics:")
        print(f"Total input tokens: {self.total_input_tokens}")
        print(f"Total output tokens: {self.total_output_tokens}")
        print(
            f"Tokens in last minute: {sum(tokens for _, tokens in self.token_history)}"
        )

        total_tokens = self.total_input_tokens + self.total_output_tokens

        print(f"\nTop {TOP_N} Contributors by Type:")
        for msg_type, tokens in self.message_type_histogram.most_common(TOP_N):
            percentage = (tokens / total_tokens) * 100
            print(f"{msg_type}: {tokens} tokens ({percentage:.2f}%)")
