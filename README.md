- [Start coding for the day](#start-coding-for-the-day)
- [Setup](#setup)
- [Notes](#notes)
  - [TODO Ideas](#todo-ideas)
  - [High-level Problems](#high-level-problems)

# Start coding for the day

* Just make sure `rye` is activated and sync'ed!


# Setup

* Just install [rye](https://rye.astral.sh/guide/basics/) and put it in your startup script.


# Notes

## TODO Ideas

* Try some local/offline models:
  * e.g. `ollama run codellama:70b`
* NOTE: RAG (Retrieval-Augmented Generation) or any proper local/offline models will need a GPU and/or a powerful setup. We'll have to investigate that.


## High-level Problems

* How can we make sure that the agent can learn and stops repeating rather specific types of mistakes?
  * For example, when adding a tool, it always wants to return things, and convert exceptions into return values. Terrible pattern.
  * Usually, the SYSTEM_PROMPT should help with this, but sometimes the mistakes are too context-sensitive.