# create_canvas_groups

Assigns students to a [Canvas](https://canvas.instructure.com) `course`'s groups according to `assignments` (csv).

**Note:** Defaults to a _DRY RUN_, only printing the changes that will occur if you add the `--wet_run` flag.

    usage: group_em.py [-h] [--canvas_key CANVAS_KEY] [--canvas_url CANVAS_URL]
                   [--wet_run]
                   assignments course