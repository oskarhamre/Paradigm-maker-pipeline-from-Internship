## Pipeline for creating story-listening paradigms
*Oskar Hamre*

 This project automates the creation of audio listening fMRI paradigms.

---
### How to use:
- Open main-file
- Fill in **language**, **story_name**, and **story_theme**
- `language` has to be supported
- `story_name` cannot contain spaces and will appear in the name of the paradigm
    - any spaced is automatically removed in the pipeline
- `story_theme` is optional
    - if left blank, the story will be native to the language chosen
    - Note: is blank, the variable must point to an empty string
---
### Additional steps
- After the main-function is ran, the paradigm will appear in its own folder
- This folder is **missing the *pictures* folder**
    - Fix: copy the pictures folder in `PARADIGMMAKER` and paste in the created paradigm folder
- Copy the ready paradigm folder to nordicActiva -> assets -> json and import in the nordicActiva-application

