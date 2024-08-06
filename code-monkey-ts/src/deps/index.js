"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getModuleName = exports.resolveModulePath = exports.resolveFilePath = exports.ASTParser = void 0;
var ast_parser_1 = require("./ast_parser");
Object.defineProperty(exports, "ASTParser", { enumerable: true, get: function () { return ast_parser_1.ASTParser; } });
var deps_utils_1 = require("./deps_utils");
Object.defineProperty(exports, "resolveFilePath", { enumerable: true, get: function () { return deps_utils_1.resolveFilePath; } });
Object.defineProperty(exports, "resolveModulePath", { enumerable: true, get: function () { return deps_utils_1.resolveModulePath; } });
Object.defineProperty(exports, "getModuleName", { enumerable: true, get: function () { return deps_utils_1.getModuleName; } });
