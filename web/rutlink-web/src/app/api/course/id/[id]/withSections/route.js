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

    // console.log(req)

    // url looks like: /api/course/id/.../withSections
    // get ...
    console.log(req.url)
    const courseid = req.url.split("/id/")[1].split("/withSections")[0];
    console.log(courseid)

  
    // Perform a database query to retrieve all items from the "items" table
    const course = await db.all("SELECT * FROM Courses WHERE courseid = ? LIMIT 1", courseid);

    console.log(course)

    // now get all section IDs for this course
    const sectionList = await db.all("SELECT sectionid FROM CourseSection WHERE courseid = ?", courseid);

    console.log(sectionList)

    // now get all section objects for this course
    const sectionObjList = await db.all("SELECT * FROM Sections WHERE sectionid IN (?)", sectionList.map((section) => section.sectionid).join(","));

    // return course with "sections" key added
    course[0].sections = sectionObjList;

    // Return the items as a JSON response with status 200
    return new Response(JSON.stringify(course), {
      headers: { "Content-Type": "application/json" },
      status: 200,
    });
  }