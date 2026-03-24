#!/usr/bin/env node
/* Export one or more SVG files to PNG using sharp. */

const fs = require("fs");
const path = require("path");

let sharp;
try {
  sharp = require("sharp");
} catch (error) {
  console.error("sharp is required. Install it before running this script.");
  process.exit(1);
}

function printHelp() {
  console.log(`Usage:
  node export_svg_to_png.js <input.svg> [output.png] [--width 3200] [--density 200]
  node export_svg_to_png.js <input1.svg> <input2.svg> ... [--width 3200] [--density 200]`);
}

function parseArgs(argv) {
  const positional = [];
  let width = 3200;
  let density = 200;

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") {
      printHelp();
      process.exit(0);
    }
    if (token === "--width") {
      width = Number(argv[index + 1]);
      index += 1;
      continue;
    }
    if (token === "--density") {
      density = Number(argv[index + 1]);
      index += 1;
      continue;
    }
    positional.push(token);
  }

  return { positional, width, density };
}

async function exportPair(input, output, width, density) {
  await sharp(input, { density }).resize(width).png().toFile(output);
  console.log(`OK ${path.basename(input)} -> ${output}`);
}

async function main() {
  const { positional, width, density } = parseArgs(process.argv.slice(2));
  if (positional.length === 0) {
    printHelp();
    process.exit(1);
  }

  if (positional.length === 2 && positional[0].endsWith(".svg") && positional[1].endsWith(".png")) {
    await exportPair(positional[0], positional[1], width, density);
    return;
  }

  for (const input of positional) {
    if (!input.endsWith(".svg")) {
      console.error(`Expected an .svg file, got: ${input}`);
      process.exit(1);
    }
    if (!fs.existsSync(input)) {
      console.error(`File does not exist: ${input}`);
      process.exit(1);
    }
    const output = input.replace(/\.svg$/i, ".png");
    await exportPair(input, output, width, density);
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
