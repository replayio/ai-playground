"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getLogger = getLogger;
exports.setupLogging = setupLogging;
const winston = __importStar(require("winston"));
require("winston-daily-rotate-file");
const MAX_LENGTH = 200; // Set to 0 to disable truncation
function getTruncatedMessage(message) {
    if (MAX_LENGTH > 0 && message.length > MAX_LENGTH) {
        return message.substring(0, MAX_LENGTH - 3) + '...';
    }
    return message;
}
function getLogger(name) {
    return winston.loggers.get(`codemonkey:${name}`);
}
function setupLogging(debug) {
    const transports = [];
    if (debug) {
        transports.push(new winston.transports.Console({
            format: winston.format.combine(winston.format.colorize(), winston.format.printf(info => {
                let message = `${info.level}: ${info.message}`;
                message = getTruncatedMessage(message);
                return message;
            })),
            level: 'debug',
        }));
        getLogger('logging').debug('Debug logging enabled');
    }
    else {
        transports.push(new winston.transports.Console({
            format: winston.format.combine(winston.format.timestamp(), winston.format.printf(info => {
                let message = `${info.timestamp} - ${info.level}: ${info.message}`;
                message = getTruncatedMessage(message);
                return message;
            })),
            level: 'info',
        }));
    }
    winston.loggers.options.transports = transports;
}
