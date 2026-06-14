const fs = require('fs');
const files = process.argv.slice(2);
for (const file of files) JSON.parse(fs.readFileSync(file, 'utf8'));
console.log(`validated ${files.length} JSON file(s)`);
