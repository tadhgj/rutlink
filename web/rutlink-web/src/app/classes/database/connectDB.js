const sqlite3 = require("sqlite3").verbose();


const db_file_path = "../../../../../../data/webreg/webreg.db";

const db = new sqlite3.Database(
    db_file_path,
    sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE,
    (err) => {
        if (err) {
            return console.error(err.message);
        }
        console.log("Connected to the SQlite database.");
    }
);

db.serialize(() => {
    // list tables:
    console.log("Tables:");
    db.each(`SELECT name FROM sqlite_master WHERE type='table'`, (err, row) => {
        if (err) {
            console.error(err.message);
        }
        console.log(row);
    });


    db.each(`SELECT * FROM Teachers`, (err, row) => {
        if (err) {
            console.error(err.message);
        }
        // console.log(row);
    });
});