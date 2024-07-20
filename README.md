- [Start coding for the day](#start-coding-for-the-day)
- [Setup](#setup)
- [Google Cloud Credentials Setup](#google-cloud-credentials-setup)
- [Notes](#notes)
  - [TODO Ideas](#todo-ideas)
  - [High-level Problems](#high-level-problems)

# Start coding for the day

* Just make sure `rye` is activated and sync'ed!


# Setup

* Just install [rye](https://rye.astral.sh/guide/basics/) and put it in your startup script.


# Google Cloud Credentials Setup

To use the Google Cloud Speech-to-Text API for audio transcription, you need to set up credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the Speech-to-Text API for your project.
4. Create a service account key:
   - Go to "IAM & Admin" > "Service Accounts".
   - Click "Create Service Account".
   - Give it a name and grant it the "Speech-to-Text User" role.
   - Create a JSON key for this service account.
5. Download the JSON key file.
6. In the project root, create a file named `.env.secret` if it doesn't exist.
7. Add the following line to `.env.secret`, replacing `/path/to/your/keyfile.json` with the actual path to your downloaded JSON key file:

   ```
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/keyfile.json
   ```

8. Make sure `.env.secret` is added to your `.gitignore` file to prevent accidentally committing sensitive information.

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
