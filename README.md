# DISEASE SPREAD

Python project to visualize a virus dissemination. Work In Progress.


## Insallation

Run `pip install -r requirements.txt`.

## How to

Run `python3 program.py` to start the visualization.

To use other databases, make sure:
- the table name match the file name,
- two databases are involved: `vertices` and `edges`,
- the vertices db use at least columns `id` and `name`, and `status` if needed,
- the edges db use at least columns `fiedl1` and `field2`.

## Screenshot

![screenshot with got db](https://github.com/4l3x4ndre/disease-spread/blob/main/screenshot.png)

## Credits

Databases are based on the repository [sample-social-network-datasets](https://github.com/melaniewalsh/sample-social-network-datasets) from Melanie Walsh.
