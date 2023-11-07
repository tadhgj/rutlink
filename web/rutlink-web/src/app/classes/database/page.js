// make similar to src/app/page.js
// set as "use client"

"use client";

import { useState, useEffect } from 'react';

function ListClassObject(props) {
    return (
        <div className="border rounded px-2 py-1 my-2">
            <div>
                <h2 className="text-lg">
                    {props.classname}
                </h2>
                <p className="text-slate-600 text-sm">
                    {props.teacher}
                </p>
            </div>

            <div className="flex">
                <div>
                    <p>
                        {props.startTime} - {props.endTime}
                    </p>
                </div>

                <div className="flex ml-auto">
                    <p className="pr-2">
                        <span className="font-mono">
                            {props.campusID}
                        </span>
                        
                        <span className="text-red-500">
                        {props.buildingCode}
                        </span>
                        
                    </p>
                        <p className="">
                            {props.roomNumber}
                        </p>

                    {/* make the campus ID monospaceed, the building code red, and the room numebr upside down */}
                </div>

                </div>

        </div>
    )
}

function ClassList(props) {
    if (props.isloading) {
        return (
            <div>
                <p>
                    Loading...
                </p>
            </div>
        )
    } else {
        return (
            <div>
                {
                    props.classList.map((classObj) => (
                        <ListClassObject key={classObj.classname}
                            classname={classObj.classname}
                            teacher={classObj.teacher}
                            startTime={classObj.startTime}
                            endTime={classObj.endTime}
                            campusID={classObj.campusID}
                            buildingCode={classObj.buildingCode}
                            roomNumber={classObj.roomNumber}
                        />
                    ))
                }
            </div>
        )
    }
}

export default function ClassesDatabase() {

    // {
    //     classname: "CS 118",
    //     teacher: "Dr. Brian Russell",
    //     startTime: "1020",
    //     endTime: "1140",
    //     campusID: "Busch",
    //     buildingCode: "Hill Center",
    //     roomNumber: "114"
    // }

    const [isLoading, setIsLoading] = useState(false);

    const [classes, setClasses] = useState([])

    async function updateClasses() {
        if (isLoading) {
            console.log("previous updateClasses still running")
            return
        }
        let dbClasses = []
        console.log("updateClasses")
        setIsLoading(true)

        try {
            const res = await fetch("http://localhost:3000/api/meetings/nowextend")
            const data = await res.json()
    
            for (let i = 0; i < data.length; i++) {

                // for each meeting:

                // get course
                // const rescourse = await fetch("http://localhost:3000/api/course/id/" + data[i].courseid)
                // const coursedata = await rescourse.json()
                // get sections
                // const sections = await fetch("http://localhost:3000/api/section/meetingid/" + data[i].meetingid)
                // const sectiondata = await sections.json()
                // // for each section:
                // for (let j = 0; j < sectiondata.length; j++) {
                //     // get teachers
                //     const teachers = await fetch("http://localhost:3000/api/teacher/section/" + sectiondata[j].sectionid)
                //     const teacherdata = await teachers.json()
                //     // for each teacher:
                //     for (let k = 0; k < teacherdata.length; k++) {
                //         // get teacher name
                //         const teachername = await fetch("http://localhost:3000/api/teacher/id/" + teacherdata[k].teacherid)
                //         const teachernameData = await teachername.json()
                //         // add to list
                //         let newClass = {
                //             classname: coursedata[0].fullname.trim(),
                //             teacher: teachernameData[0].teachername,
                //             startTime: data[i].meetingstart,
                //             endTime: data[i].meetingend,
                //             campusID: data[i].meetingcampusid,
                //             buildingCode: data[i].meetingbuilding,
                //             roomNumber: data[i].meetingroom
                //         }
                //         dbClasses.push(newClass)
                //     }
                // }
                let newClass = {
                    // classname: coursedata[0].fullname.trim(),
                    classname: data[i].courseobj.fullname.trim(),
                    teacher: data[i].teacherList.map((teacher) => teacher.teachername).join(", "),
                    startTime: data[i].meetingstart,
                    endTime: data[i].meetingend,
                    campusID: data[i].meetingcampusid,
                    buildingCode: data[i].meetingbuilding,
                    roomNumber: data[i].meetingroom
                }
                dbClasses.push(newClass)
                setClasses(dbClasses)
                
                

                // const res2 = await fetch("http://localhost:3000/api/section/meetingid/" + data[i].meetingid)
                // const data2 = await res2.json()
    
                // for (let j = 0; j < data2.length; j++) {
                //     const res3 = await fetch("http://localhost:3000/api/teacher/section/" + data2[j].sectionid)
                //     const data3 = await res3.json()
    
                //     for (let k = 0; k < data3.length; k++) {
                //         const res4 = await fetch("http://localhost:3000/api/teacher/id/" + data3[k].teacherid)
                //         const data4 = await res4.json()
    
                //         const res5 = await fetch("http://localhost:3000/api/course/sectionid/" + data2[j].sectionid)
                //         const coursedata = await res5.json()
    
                //         let newClass = {
                //             classname: coursedata[0].fullname.trim(),
                //             teacher: data4[0].teachername,
                //             startTime: data[i].meetingstart,
                //             endTime: data[i].meetingend,
                //             campusID: data[i].meetingcampusid,
                //             buildingCode: data[i].meetingbuilding,
                //             roomNumber: data[i].meetingroom
                //         }
    
                //         dbClasses.push(newClass)
                //     }
                // }
            }
            console.log("new classes", dbClasses)
            setClasses(dbClasses)
            setIsLoading(false)
        } catch (err) {
            console.error(err)
            setIsLoading(false)
        }


        // fetch classes from database

        // for all meetingTimes in database where the current time is between the start and end time...
        // find section for that meeting time
        // find teacher for that section

        // load api/meetings/now
        // for each: get section ... get teacher
        // add to list
        // fetch("http://localhost:3000/api/meetings/now")
        // .then(res => res.json())
        // .then((data) => {
        //     for (let i = 0; i < data.length; i++) {
        //         // console.log("meetingid:",data[i])
        //         fetch("http://localhost:3000/api/section/meetingid/" + data[i].meetingid)
        //         .then(res => res.json())
        //         .then((data2) => {
        //             for (let j = 0; j < data2.length; j++) {
        //                 // console.log('section:',data2[j])

        //                 // fetch api/course/sectionid/:sectionid
        //                 // fetch api/teacher/id/:id
        //                 fetch("http://localhost:3000/api/teacher/section/" + data2[j].sectionid)
        //                 .then(res => res.json())
        //                 .then((data3) => {
        //                     // for each teacher...
        //                     for (let k = 0; k < data3.length; k++) {
        //                         // console.log("teacherid: ",data3[k])
        //                         // get teacher name
        //                         fetch("http://localhost:3000/api/teacher/id/" + data3[k].teacherid)
        //                         .then(res => res.json())
        //                         .then((data4) => {
        //                             // console.log("teacher name: ",data4[0].teachername)
        //                             fetch("http://localhost:3000/api/course/sectionid/" + data2[j].sectionid)
        //                             .then(res => res.json())
        //                             .then((coursedata) => {
        //                                 // there can ONLY be 1 course for a given section
        //                                 // console.log("course data: ",coursedata[0])
        //                                 // add to list
        //                                 let newClass = {
        //                                     classname: coursedata[0].fullname.trim(),
        //                                     teacher: data4[0].teachername,
        //                                     startTime: data[i].meetingstart,
        //                                     endTime: data[i].meetingend,
        //                                     campusID: data[i].meetingcampusid,
        //                                     buildingCode: data[i].meetingbuilding,
        //                                     roomNumber: data[i].meetingroom
        //                                 }
        //                                 console.log("newClass",newClass)
        //                                 dbClasses.push(newClass)
        //                                 console.log("dbClasses",dbClasses)
        //                             })
        //                         })
        //                     }
        //                 })
        //             }
        //         })
        //     }
        // })


        // setClasses to the fetched classes
        // setClasses(dbClasses)
        // setIsLoading(false)
    }

    // updateClasses()

    const MINUTE_MS = 60000;

    useEffect(() => {
        console.log("first log")
        updateClasses()

        // const interval = setInterval(() => {
        //     console.log('Logs every minute');
        //     updateClasses()
        // }, MINUTE_MS);

        // return () => clearInterval(interval); // This represents the unmount function, in which you need to clear your interval to prevent memory leaks.
    }, [])

    return (
        <main className="flex min-h-screen flex-col items-center justify-between p-24">
            <h1>What classes are on right now?</h1>
            {/* <button onClick={updateClasses}>Update</button> */}

            {/* do a list here */}

            <p>
                {(classes.length)} class{classes.length == 1 ? "" : "es"} on right now
            </p>

            <ClassList
                isloading = {isLoading}
                classList = {classes}
                />

            {/* {classList.map((classObj) => (
                <ListClassObject key={classObj.classname}
                    classname={classObj.classname}
                    teacher={classObj.teacher}
                    startTime={classObj.startTime}
                    endTime={classObj.endTime}
                    campusID={classObj.campusID}
                    buildingCode={classObj.buildingCode}
                    roomNumber={classObj.roomNumber}
                />
            ))}
 */}
            {/* <ListClassObject 
                classname="CS 111" 
                teacher="Dr. Brian Russell"
                startTime="1020"
                endTime="1140"
                campusID="Busch"
                buildingCode="Hill Center"
                roomNumber="114"
                /> */}
        </main>
    )
}
