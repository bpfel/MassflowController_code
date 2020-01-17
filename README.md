# Air Massflow Sensor Setup

## Contents of this Repository

The setup files of this lab are hosted on the IDSC NAS:
\\d.ethz.ch\groups\mavt\idsc\chris\Lectures\LaboratoryTraining\03_Computer_Backups\Luftmassenstromsensor

## Contributing to this Repository:

1. Clone the repository to your local machine.
For this purpose, you need to install Git.
We recommend using the graphical user interface "SourceTree" (https://www.sourcetreeapp.com/), which can be automatically installed including Git.
Open the application and clone the repository via File -> Clone / New, and copy the link to the repository (https://gitlab.com/eth-laboratory-practice/experiment-setups/air-mass-flow-setup.git) into the field for the source URL.
The destination path is the local directory of where you want to have the project and the corresponding files on your hard drive.
The name of the folder is irrelevant and can be chosen arbitrarily.

2. We follow the Gitflow workflow for branching (https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow).
You can automatically initialize SourceTree to use this scheme by clicking Repository -> Git-flow -> initialize.
This will check out the branch `develop`, which always contains the latest approved version of the code and documents.
The branch `master` contains the "released" version which is available to the students.

3. As no one can directly modify the content of the `develop` branch, you have to start a new feature branch, e.g. `feature/script_improvements`.
You can do this in SourceTree using Repository -> Git-flow -> Start new Feature.
You can commit and push your changes to this branch as many times as you like.

4. When you're done with the changes in your feature branch, you can create a "merge request", i.e., a request to merge your feature branch into the develop branch.
You can directly select your supervisor as "assignee" for the merge request, in which case he/she will be notified via e-mail.
