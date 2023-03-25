let base64 = require("base-64");
const { Pool } = require("pg");

const pool = new Pool({
  user: "postgres",
  host: "127.0.0.1",
  database: "ncsc",
  password: "postgres",
  port: 5432,
});

async function request_ncsc(day, page) {
  let url =
    "https://openapi.ncsc.gov.vn/phishing/query?api_key=mboz8Q3FioCoE6RjoD8t&page=" +
    page +
    "&delta_day=" +
    day;
  let username = "scs_openapi";
  let password = "yqTd7HbBhkryzMAP";

  let headers = new Headers();

  headers.set(
    "Authorization",
    "Basic " + base64.encode(username + ":" + password)
  );
  let respone = await fetch(url, { method: "GET", headers: headers });
  let data = await respone.json();

  return data;
}

function getDateTime() {
  var today = new Date();
  var date =
    today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + today.getDate();
  var time =
    today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
  var dateTime = date + " " + time;
  return dateTime;
}

function process_data_and_upsert(records) {
  records.forEach((record) => {
    url = record["url"];
    if (url == undefined) {
      url = record["domain"];
    }

    url = url.replace("https://", "").replace("www.", "").replace("http://");

    substrings = url.split("/");
    substrings = substrings.filter((element) => element !== "");
    if (substrings.length == 1) {
      url = url.replace("/", "");

      //   insert to postgres
      const query =
        "INSERT INTO data(timestamps, url, ip, tags, confident_level, verified, online, data_source, created_at, last_updated) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) ON CONFLICT (url) DO NOTHING";
      const values = [
        getDateTime(),
        url,
        record["ip"],
        String(record["tags"]),
        record["confident_level"],
        record["verified"],
        record["online"],
        record["data_source"],
        record["created_at"],
        record["last_updated"],
      ];
      pool.query(query, values).catch((e) => console.error(e.stack));
    }
  });
}

async function main() {
  for (let day = 451; day < 460; day++) {
    // request first page
    let initial_page = 1;
    let data = await request_ncsc(day, initial_page);
    if (data != undefined && data != "Cannot found page 1") {
      console.log(`${getDateTime()}: Requested day ${day}, page 1`);
      let records = data["records"];
      let total_pages = data["meta"]["total_pages"];

      //process_data_and_upsert for first page
      process_data_and_upsert(records);

      //process next page of the same day
      for (let page = initial_page + 1; page < total_pages; page++) {
        let next_data = await request_ncsc(day, page);
        console.log(`${getDateTime()}: Requested day ${day}, page ${page}`);
        let next_records = next_data["records"];

        // process_and_upsert
        process_data_and_upsert(next_records);
      }
    }
  }

  pool.end().then(() => console.log("pool has ended"));
}

main();
