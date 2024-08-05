import { BaseAgent } from './base_agent';
import { BaseChatModel } from '../models/chat_model';
import { MSN } from '../models/msn';
import { createReactAgent } from '../utils/agent_utils';
import { AsyncSqliteSaver } from '../utils/sqlite_saver';
import { SystemMessage, HumanMessage } from '../utils/message_types';
import { instrument } from '../instrumentation/instrument';
import { getRootDir, getArtifactsDir } from '../constants';
import { showDiff, askUser } from '../tools/user_interaction_tools';
import { logger } from '../utils/logger';
import { EventType } from '../types/event_types';

export class Agent extends BaseAgent {
  model: BaseChatModel;

  @instrument('Agent.init')
  constructor(msnStr: string | null) {
    super();
    const msn = MSN.fromString(msnStr);
    const memory = new AsyncSqliteSaver(':memory:');
    this.model = createReactAgent(
      msn.constructModel(),
      this.tools,
      memory,
    );
    this.initialize();
  }

  @instrument('Agent.runPrompt')
  async runPrompt(prompt: string): Promise<void> {
    console.log(`Running prompt: ${prompt}`);
    const system = new SystemMessage(this.getSystemPrompt());
    const msg = new HumanMessage(this.preparePrompt(prompt));
    const modifiedFiles: Set<string> = new Set();

    for await (const event of this.model.streamEvents(
      { messages: [system, msg] },
      this.config,
      'v2',
    )) {
      const kind: EventType = event.event;
      logger.debug(`Agent received event: ${kind}`);
      // Handle events here
      // ...
    }

    this.handleCompletion(modifiedFiles);
  }

  @instrument('Agent.handleCompletion')
  handleCompletion(modifiedFiles: Set<string>): void {
    // Handle completion, show diffs, ask user to apply changes
    // ...
  }

  @instrument('Agent.handleModifiedFile')
  handleModifiedFile(file: string): void {
    // Handle modified file, show diff, ask user to apply changes
    // ...
  }
}
