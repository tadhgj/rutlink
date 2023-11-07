// get course information from id and display

// Path: web/rutlink-web/src/app/classes/course/page.js
"use client";
import { useParams } from 'next/navigation';
import { stringify } from 'postcss';
import React from 'react';
import useSWR from 'swr'

const fetcher = (...args) => fetch(...args).then((res) => res.json())

function fetchCourse(id) {

  const { data, error, isLoading } = useSWR(`/api/course/id/${id}`, fetcher)

  return {
    course: data,
    isLoading,
    isError: error
  }
}

// do network request in this function:
export default function CoursePage() {
  // get id from url
  const { id } = useParams();

  // fetch data from api
  const { course, isLoading, isError } = fetchCourse(id);
 
   
  if (isLoading) return (
      <main className="flex min-h-screen flex-col items-center justify-between p-24">
        <h1>Loading...</h1>
      </main>
    )
  if (isError) return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1>Error...</h1>
    </main>
  )
  // there should be data at this point...
  if (course.length === 0) {
    return <h1>Course not found</h1>
  }

  const coursezero = course[0];
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">

      <h1>{coursezero.fullname}</h1>
      <p>{coursezero.coursecode}</p>

      <div className="flex flex-col items-center justify-center">
        {/* all sections here... */}



      </div>
    </main>
  )

}