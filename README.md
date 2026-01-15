*****************
**Learning Logs**
*****************




**Project Breakdown** 
*********************
This project was initially born from a book on an intro to python web development with Django, I thought of the idea 
to keep track of your learning by keeping a log and initially though it would be nice to pair this with quizlet 
style concepts and questions. I personally find it annoying when a read something that is definetly important but
it only appears once. I also have been trying to learn new languages but find that again they are only showing me
something new then moving on to something else without giving me the proper time and repetition to say that I actually
learned a new word or phrase. With this in mind I began work during winter break on a web app I can use to both 
improve my learning and learn through creating. Thus Learning Logs was born and even during production I have been
using it to help studying Japanese. I am very proud and happy for how far I have come in creating this project as well
as how much I have learned throughout the past few weeks.

***********************
**Project Description**
***********************
This project allows users to create different learning boards for any topic you may desire. You can write logs to track
your learning journey, as well as being able to add concepts to learn and begin a study session for said concepts. Each 
concept has any given tags which can be used to filter questions for studying. You can set questions to have specific
question types like true or false or multiple choice, as well as just standard inputs like inputting the answer given
a definition or input the definition given the answer. Questions without question types will be available for sesions
with whatever default question types are set for that board. Sessions are tracked and you can see how many correct or
incorrect answers you had during a session. Session settings can be saved and loaded at a later date if you find 
yourself wanting to study certain specific material multiple times. You can also upload a CSV file full of concepts 
in the form of _Answer : str, Definition : str, Hint : str, Tags : list, Questions : list_. All concepts will be created
and added to the board with all of these details, if a tag doesnt exist for any of the tags in a concepts tag list that tag
will be created. 

**************
**How To Use**
**************
I currently plan to host the project with Vercel and continue using my Neon serverless database for hosting upon full completion.
You can also download the files and connect to your own personal DB by either setting your database to be a local PSQL database,
or your own serverless hosted database. In development I am using redis through docker which will be set to a production version
upon completion and hosting. 

****************
**Future Plans**
****************
As of writing the project is nearly finished with only UI changes to be made to make the UI respond to different screen sizes.
I will continue to update if I find any bugs or am notified by a user of any bugs but currently do not have an big ambitions for
this project.

********************
**Whats The Point?**
********************
I made this project as my first every dive into web development, I have tried to follow tutorials either through youtube or 
any book I may be reading but it never let me use my own creativity so this is the first idea I had that I thought would be
useful to me, fun to do, and work well as a personal project. I am currently looking for an internship in software engineering
and I honestly have no clue where I am at, if I am way ahead of my peers or way behind and I think after a few interviews
and people reviewing hopefully this project or another one I plan to make I will be given a decent idea of where I am. If I 
am way behind I will more than likely come back to this project and make the improvements it needs, and if I have freetime
and am told this is a good project just might need some more love I would happily come back to this project. The real problem
I face now is time, it is the middle of January 2026 and I am already pretty late to the internship window for Summer 2026 so
I need to push 1 or two full-stack web apps to give myself a good shot at an internship in my mind. I can't spend the extra
weeks I may want to continue to implement new things as I endlessly think of new things to add. This app is in a good state
in my opinion and does everything I need it to, and more than what I had originally planned it to do. I hope if someone reads
this far they can either gain motivation to start a similair product, tell me the whole project is shit and never show it to 
anyone, or be impressed by my work and give me ideas on what I could've done different to keep improving my skills and knowledge
