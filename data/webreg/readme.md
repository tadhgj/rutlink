# setup
run

webreg_relationship.py

while under the /data/webreg directory

which will fetch webreg data for New Brunswick

specifically, semesters Spring 2024 back to Spring 2022

which will create

- d3_webreg.json
- rel_debug.json
- temp.json (temporary file)

# view the data

then run a python server under the /data/webreg directory to view 2d_webreg_rel.html for a 3d visualization of coures prerequisites

using

```python3 -m http.server 8000```

or

```python -m SimpleHTTPServer 8000```
(but I have not tested this with python2)

and under /data/webreg/prereq/prereqList.html

you can search a more usable interface for course prerequisites
(filtering by course code / course name)