import sqlite3 from "sqlite3";
import { open, Database } from "sqlite";

// Let's initialize it as null initially, and we will assign the actual database instance later.
let db = null;

let db_file_path = "../../data/webreg/webreg.db";

// GET teacher with fuzzy search "LIKE %?%"
// api/teacher/mike
export async function GET(req, res) {
    // Check if the database instance has been initialized
    if (!db) {
      // If the database instance is not initialized, open the database connection
      try {
        db = await open({
            filename: db_file_path, // Specify the database file path
            driver: sqlite3.Database, // Specify the database driver (sqlite3 in this case)
        });
      }
      catch (e) {
        console.log("no db!")
        console.log(e);
      }

      // handle failure
    }

    // get current time
    // in HHMM format (24h)

    let now = new Date();
    let hour = now.getHours();
    let minute = now.getMinutes();
    let time = hour.toString().padStart(2, '0') + minute.toString().padStart(2, '0');


    // Perform a database query to retrieve all items from the "items" table
    const teachers = await db.all("SELECT * FROM Meetings WHERE meetingstart < ? AND meetingend > ?", time, time);
  
    // Return the items as a JSON response with status 200
    return new Response(JSON.stringify(teachers), {
      headers: { "Content-Type": "application/json" },
      status: 200,
    });
  }