import {f} from "./f"

function g(x: any, y: any) {
  return x + y;
}

function main() {
  return f(g, parseInt(process.argv[2]), parseInt(process.argv[3]));
}
