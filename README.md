1. [How to?](#how-to)
2. [Start coding for the day](#start-coding-for-the-day)
3. [Setup](#setup)
4. [Notes](#notes)
   1. [TODO Ideas](#todo-ideas)
   2. [High-level Problems](#high-level-problems)


# How to?

1. Make sure you have setup the project and `rye sync`ed.
2. Modify `.prompt.md` to provide instructions to the LLM.
   * Example prompt:
     ```md
     Rename `AskUserTool` in `ask_user_tool.py` to `AskUserTool2`.
     ```
3. Run `main_coder.py` or `main_manager.py` to fulfill that prompt.


# Start coding for the day

* `rye sync`
* `./setup.sh` for system dependencies (if necessary)


# Setup

* Install [rye](https://rye.astral.sh/guide/basics/), make sure its activated and sync'ed and put in your startup script.
* Create a new `.env.secret` file and add your secrets, especially:
  * `ANTHROPIC_API_KEY` (for Claude)
  * `OPENAI_API_KEY` (optional, for GPT-4)
  <!-- * `AI_MSN` (optional - chooses a different AI service+model+additional flags)
    * There is `.env.secret.example` with an example of `AI_MSN` for use with claude. -->
<!-- * Google Cloud setup (for speech-to-text support)
  * -> See below -->
* Run `./setup.sh` to get started.

<!-- 
# Google Cloud Credentials Setup

To use the Google Cloud Speech-to-Text API for audio transcription, you need to set up credentials:

## First Time
  1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
  2. Create a new project or select an existing one.
  3. Enable the Speech-to-Text API for your project.
  4. Create a service account key:
     - Go to "IAM & Admin" > "Service Accounts".
     - Click "Create Service Account".
     - Give it a name and grant it the "Speech-to-Text User" role.

## Once you have setup the API:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Go to "IAM & Admin" > "Service Accounts".
2. Create a JSON key for the service account.
3. Download the JSON key file.
4. Store the key in `.secret/google_application_credentials.json`.

The `setup.sh` script will automatically load the credentials from `.env.secret` when setting up the project. -->


# Notes

## TODO Ideas

* Try some local/offline models:
  * e.g. `ollama run codellama:70b`
* NOTE: RAG (Retrieval-Augmented Generation) or any proper local/offline models will need a GPU and/or a powerful setup. We'll have to investigate that.


## High-level Problems

* How can we make sure that the agent can learn and stops repeating rather specific types of mistakes?
  * For example, when adding a tool, it always wants to return things, and convert exceptions into return values. Terrible pattern.
  * Usually, the SYSTEM_PROMPT should help with this, but sometimes the mistakes are too context-sensitive.
