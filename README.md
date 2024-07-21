- [Start coding for the day](#start-coding-for-the-day)
- [Setup](#setup)
- [Google Cloud Credentials Setup](#google-cloud-credentials-setup)
  - [First Time](#first-time)
  - [Once you have setup the API:](#once-you-have-setup-the-api)
- [Notes](#notes)
  - [TODO Ideas](#todo-ideas)
  - [High-level Problems](#high-level-problems)

# Start coding for the day

* `rye sync`
* `./setup.sh` (if necessary)


# Setup

* Install [rye](https://rye.astral.sh/guide/basics/), make sure its activated and sync'ed and put in your startup script.
* Create a new .env.secret file and add your secrets, especially:
  * `ANTHROPIC_API_KEY` (for Claude)
  * `OPENAI_API_KEY` (optional, for GPT-4)
* Google Cloud setup (for speech-to-text support)
  * -> See below
* Run `./setup.sh` to get started.


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

The `setup.sh` script will automatically load the credentials from `.env.secret` when setting up the project.


# Notes

## TODO Ideas

* Try some local/offline models:
  * e.g. `ollama run codellama:70b`
* NOTE: RAG (Retrieval-Augmented Generation) or any proper local/offline models will need a GPU and/or a powerful setup. We'll have to investigate that.


## High-level Problems

* How can we make sure that the agent can learn and stops repeating rather specific types of mistakes?
  * For example, when adding a tool, it always wants to return things, and convert exceptions into return values. Terrible pattern.
  * Usually, the SYSTEM_PROMPT should help with this, but sometimes the mistakes are too context-sensitive.
