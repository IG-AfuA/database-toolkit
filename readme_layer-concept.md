# Layer concept (draft)

## Concept and goal (draft)

Structure of the work steps into clearly defined sections. Separate py-modules for each section.

Clear division into sections that
- apply to all question pools (import sources) or apply to all export versions.
-  must be solved individually for each import source.
- must be solved individually for each export version.

The aim is to make it easier to integrate new question pools or new export versions thanks to the improved structure described above.

## Layers (proposal,  tbd)

Separate python modules for the following steps:

Step 1 = general: evaluating the command line parameters
         (or GUI where you can set the parameters)

Step 2 = source-dependent modules: import data
         (different question data sets, lichtblicke, ...)

Step 3 = general: filtering the questions
         (according to command line parameters)

The following steps therefore only contain the data that is actually wanted.

Step 4 = source-dependent modules: source-dependent parsing
         using a submodule for general parsing (e.g. german-sz)

Step 5 = general: quality checks
         (e.g. check presence of linked pictures)

Step 6 = Special: category name reassignment
         (can be source-dependent and target-dependent)
         using a submodule for import new category names

Step 7 = target-dependent modules: convert data to the needed
         export format - using a submodule for tile images

Step 8 = target-dependent modules: file writing

and one main python module stearing through the steps

Submodules for:
- debug tools
- general parsing tools
- import new category names
- tile images tools 
