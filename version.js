const config = require('./config/tresorio/config.json');

const { major, minor, patch } = config.version;
console.log(`${major}.${minor}.${patch}`);