---
name: Feature
about: Create a pull request for a new feature.
title: 'feat: '
labels: enhancement
---

Thanks for contributing to scratchattach!

### What issue does this solve?
<!-- 
Example: Please provide a link to the issue that this solves, in [here](https://github.com/TimMcCool/scratchattach/issues?q=sort%3Aupdated-desc+is%3Aissue+is%3Aopen), if applicable.
https://github.com/TimMcCool/scratchattach/issues/XXX
-->

### How does your PR solve this issue?
<!-- 
Example: Please give details about your PR, e.g. names of functions you added, and/or a brief overview of how it internally works:
This pull requests introduces the User.loves() and User.loves_count() functions that parse this page and return a list of project objects and the number of loved projects respectively, using https://scratch.mit.edu/projects/all/<user>/loves/
-->

### Any other notes of interest:
<!--
Example: Give any other context for your PR, e.g. minor unrelated changes
Since the webpage only provides some of the detail for the projects compared to the detail provided by the API for projects, so the Project objects that are instantiated contain less detail. The parameter get_full_project can be set to True to make a web request for each project to fully instantiate it, using the Project.update() method.
-->
