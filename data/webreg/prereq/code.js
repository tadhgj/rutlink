$(document).ready(function() {

    console.log("working")

    let courseList = [];
    // populate from ../rel_debug.json
    $.getJSON("../rel_debug.json", function(data) {
        courseList = data;

        console.log(courseList);

        displaySearch("");
    });
    
    function displaySearch(queryString) {
        // for each course in courseList, check for partial match on:
        // id
        // name

        // lower querystring
        queryString = queryString.toLowerCase();

        // clear #courseList
        $("#courseList").empty();

        // if queryString empty, return everything
        if (queryString == "") {
            for (var i = 0; i < courseList.length; i++) {
                var course = courseList[i];
                var courseElem = createCourseElem(course);
                $("#courseList").append(courseElem);
            }
            return;
        }

        else {
            console.log("searching for " + queryString + "...")
        }

        // if match, createCourseElem(course) and append to #courseList
        for (var i = 0; i < courseList.length; i++) {
            var course = courseList[i];
            // console.log("checking " + course.id + " " + course.name);
            if (course.id.includes(queryString) || course.name.toLowerCase().includes(queryString)) {
                console.log("found match: ", course);
                var courseElem = createCourseElem(course);
                $("#courseList").append(courseElem);
            }
        }
    }

    function createCourseElem(info) {

        // form clickables...
        // prereqListClickable
        let prereqListClickable = []
        for (var i = 0; i < info.prereqs.length; i++) {
            let prereq = info.prereqs[i];
            prereqListClickable.push(
                $("<a>").attr("href", "#"+prereq).text(prereq)
            )

            if (i != info.prereqs.length-1) {
                prereqListClickable.push(", ")
            }
        }

        // prereqForListClickable
        let prereqForListClickable = []
        for (var i = 0; i < info.isPrereqFor.length; i++) {
            let prereqFor = info.isPrereqFor[i];
            prereqForListClickable.push(
                $("<a>").attr("href", "#"+prereqFor).text(prereqFor)
            )
            if (i != info.isPrereqFor.length-1) {
                prereqForListClickable.push(", ")
            }
        }
        
        let isThisSemester = null;

        // check if "2024", "01" in info.semesters
        if (['2024','01'] in info.semesterList) {
            isThisSemester = $("<div class='course-isThisSemester'></div>").text("This semester!");
        }

        // return jquery obj
        return $('<div class="course" id="'+info.id+'"></div>').append(
            $('<div class="course-id"></div>').text(info.id),
            $('<div class="course-name"></div>').text(info.name),
            // $('<div class="course-prereqListClickable"></div>').text(info.prereqs),
            // $('<div class="course-prereqForListClickable"></div>').text(info.isPrereqFor),

            $('<div class="course-prereqListClickable"></div>').append(prereqListClickable),
            $('<div class="course-prereqStr"></div>').html(info.prereq_string),

            $('<div class="course-prereqForListClickable"></div>').append(prereqForListClickable),

            isThisSemester

        )
    }


    // when search button is clicked
    $("#searchButton").click(function() {
        var queryString = $("#search").val();
        displaySearch(queryString);
    });

    // when enter pressed on search
    $("#search").keypress(function(e) {
        if (e.which == 13) {
            var queryString = $("#search").val();
            displaySearch(queryString);
        }
    });

    // to start:
});