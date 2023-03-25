const { Pool } = require("pg");

const pool = new Pool({
  user: "postgres",
  host: "127.0.0.1",
  database: "ncsc",
  password: "postgres",
  port: 5432,
});

function getDateTime() {
  var today = new Date();
  var date =
    today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + today.getDate();
  var time =
    today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
  var dateTime = date + " " + time;
  return dateTime;
}

const query =
  "INSERT INTO test(timestamps, url, ip, tags, confident_level, verified, online, data_source, created_at, last_updated) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) ON CONFLICT (url) DO UPDATE SET timestamps=$1";
values = [
  getDateTime(),
  "clmm7s.win",
  "172.67.136.59",
  "[ 'scam' ]",
  "high",
  "true",
  "true",
  "Chong lua dao",
  "09-02-2023 01:18:29",
  "09-02-2023 01:18:29",
];

pool
  .query(query, values)
  .then((res) => console.log("1", res.rows[0]))
  .catch((e) => console.error(e.stack));

pool.query("SELECT * from test limit 20", (err, res) => {
  console.log(err, res["rows"]);
});

console.log(getDateTime());

console.log(getDateTime());

pool.end().then(() => console.log("pool has ended"));
