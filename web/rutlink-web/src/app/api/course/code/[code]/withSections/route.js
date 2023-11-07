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
    const coursecode = req.url.split("/code/")[1].split("/withSections")[0];
    console.log(`coursecode: ${coursecode}`)

  
    // Perform a database query to retrieve all items from the "items" table
    const course = await db.all("SELECT * FROM Courses WHERE coursecode = ? LIMIT 1", coursecode);

    console.log(`course: `,course)

    let courseid = course[0].courseid;

    // if course.length === 0, return []
    if (course.length === 0) {
        return new Response(JSON.stringify([]), {
            headers: { "Content-Type": "application/json" },
            status: 200,
        });
    }

    // now get all section IDs for this course
    const sectionList = await db.all("SELECT sectionid FROM CourseSection WHERE courseid = ?", courseid);

    console.log("rawSectionList: ", sectionList)

    const newSectionList = sectionList.map((section) => section.sectionid);

    console.log(`section list: `, newSectionList)

    // console.log(sectionListStr)

    // now get all section objects for this course
    // let query = "SELECT * FROM Sections WHERE sectionid IN (" + sectionListStr + ")";
    // console.log("query: "+query)
    try {
      const query = "SELECT * FROM Sections WHERE sectionid IN (?)";
      // const args = [newSectionList.join(",")];
      const args = newSectionList[0]+","+newSectionList[1];

      const res2 = await db.all(query, args);
      console.log("res2: ",res2)

      const sectionObjList = res2;

      // return course with "sections" key added
      course[0].sections = sectionObjList;

      // Return the items as a JSON response with status 200
      return new Response(JSON.stringify(course), {
        headers: { "Content-Type": "application/json" },
        status: 200,
      });
    }
    catch(err) {
      console.log(err);
    }
    // const sectionObjList = await db.all("SELECT * FROM Sections WHERE sectionid IN (?)", newSectionList.join(","));



  }