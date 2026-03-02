# Dependancy-TASK aka dtask
*Massive WIP*

A simple CLI application for managing tasks you need to do that also incorporates dependancy. Tasks can depend on other tasks, for example: 
- I have two tasks: MakeTea and PutKettleOn
- In order to MakeTea I must first PutKettleOn
- However I don't need to MakeTea in order to PutKettleOn
- Therefore I can say MakeTea depends on PutKettleOn.
- (In formal logic we can denote this as MakeTea -> PutKettleOn)

  `dtask` aims to implement this simple intuition as a cli application to manage your 'todo' lists.
  Rather than storing tasks as a simple ordered list, tasks are stored in a [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph).
  Tasks also have due-times, and thus the program *will* be able to generate linear, ordered, deadline sheets for completing a given task.

  # Help Card
  ```
  +==================D-Task help-card======================+
  .                                            Quit program
  h                                    Open this helpscreen
  n [A]                  Create new task with reference [A]
  d [A] [B]            Create dependancy '[A] requires [B]'
  rn [A]                                   Removes task [A]
  rd [A] [B]          Removes dependancy '[A] requires [B]'
  v                           Display all dependancy graphs
  v [A]                     Display dependancy graph of [A]
  ? [A] [B]                    Checks if '[A] requires [B]'
  tm [A] <mm>            Sets due month of task [A] to <mm>
  td [A] <dd>              Sets due day of task [A] to <dd>
  ty [A] <yyyy>         Sets due year of task [A] to <yyyy>
  tt [A] <hh>:<mn>   Sets due time of task [A] to <hh>:<mn>
 ```
