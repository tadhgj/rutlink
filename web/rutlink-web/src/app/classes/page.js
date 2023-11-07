"use client";
import { useState } from 'react';
// make similar to src/app/page.js


export default function Classes() {

    // init vars
    // search results
    const [searchResults, setSearchResults] = useState([]);

    return (
        <main className="flex min-h-screen flex-col items-center justify-between p-24">
            <h1>Classes</h1>

            {/* search bar */}
            <div className="flex flex-col items-center justify-center">
                <input type="text" placeholder="Search..." />
            </div>

            {/* list of results */}
            <div className="flex flex-col items-center justify-center">
                <ul>
                    {searchResults.map((result) => (
                        <li key={result.id}>
                            <Link href={`/classes/${result.id}`}>
                                <a>{result.name}</a>
                            </Link>
                        </li>
                    ))}
                </ul>
            </div>

        </main>
        

    )
}
