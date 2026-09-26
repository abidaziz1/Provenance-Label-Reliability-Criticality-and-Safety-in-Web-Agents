# Annotations

Human labels for tasks 2.1 and 3.1. Claude builds the annotation guide and the self-contained annotation page here in task 1.7.

- `raw/<annotator>_<date>.json`: one file per annotator per session. Annotators email their file to Alam, who commits it; annotators get no access to this repo, which holds unpublished work. Never edited after commit.
- Annotators are identified by a short code, not by name, in every committed file.
- Adjudicated labels and agreement statistics are produced by a script and written to the experiment folder of the task that uses them.
