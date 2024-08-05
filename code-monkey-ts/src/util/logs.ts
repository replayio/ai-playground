import * as winston from 'winston';
import 'winston-daily-rotate-file';

const MAX_LENGTH = 200; // Set to 0 to disable truncation

function getTruncatedMessage(message: string): string {
  if (MAX_LENGTH > 0 && message.length > MAX_LENGTH) {
    return message.substring(0, MAX_LENGTH - 3) + '...';
  }
  return message;
}

function getLogger(name: string): winston.Logger {
  return winston.loggers.get(`codemonkey:${name}`);
}

function setupLogging(debug: boolean): void {
  const transports: winston.transport[] = [];

  if (debug) {
    transports.push(
      new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.printf(info => {
            let message = `${info.level}: ${info.message}`;
            message = getTruncatedMessage(message);
            return message;
          })
        ),
        level: 'debug',
      })
    );
    getLogger('logging').debug('Debug logging enabled');
  } else {
    transports.push(
      new winston.transports.Console({
        format: winston.format.combine(
          winston.format.timestamp(),
          winston.format.printf(info => {
            let message = `${info.timestamp} - ${info.level}: ${info.message}`;
            message = getTruncatedMessage(message);
            return message;
          })
        ),
        level: 'info',
      })
    );
  }

  winston.loggers.options.transports = transports;
}

export { getLogger, setupLogging };
