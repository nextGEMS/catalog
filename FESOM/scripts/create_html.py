import intake
import sys
import os

# cat = intake.open_catalog("./combined_catalog.yaml")

if len(sys.argv) < 2:
    print("You have to provide path to the catalog as an argument")
    sys.exit(1)

catalog_path = sys.argv[1]

base = os.path.basename(catalog_path)
filename_without_ext = os.path.splitext(base)[0]

# If a second argument is provided, use it. Otherwise, set to None
title = sys.argv[2] if len(sys.argv) > 2 else f"Intake catalog: {filename_without_ext}"

cat = intake.open_catalog(catalog_path)
sources = list(cat)

variables = {}
for source in sources:
    print(source)
    if source == "data_inventory":
        continue
    try:
        ds = cat[source].to_dask()
    except:
        print(f"Can't open {source}")
        continue
    all_vars = set(ds.variables)
    coord_vars = set(ds.coords)
    non_coord_vars = all_vars - coord_vars
    for varr in non_coord_vars:
        if varr in variables:
            variables[varr]["sources"].append(source)
        else:
            variables[varr] = {}
            if "long_name" in ds[varr].attrs:
                variables[varr]["long_name"] = ds[varr].attrs["long_name"]
            elif "name" in ds[varr].attrs:
                variables[varr]["long_name"] = ds[varr].attrs["name"]
            else:
                variables[varr]["long_name"] = "undefined"
            variables[varr]["sources"] = []
            variables[varr]["sources"].append(source)

sorted_variables = dict(sorted(variables.items()))

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Interactive DataFrame</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            background: #f3f3f3;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 50px 0;
        }
        h1, h2 {
            text-align: center;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-bottom: 50px;
        }
        .container {
            border: 1px solid #ccc;
            padding: 15px;
            cursor: pointer;
            background: #fff;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
            border-radius: 5px;
            transition: box-shadow 0.3s ease;
            width: 200px;  /* Set a specific width */
            height: auto; /* Allow height to adjust automatically */
        }
        .container:hover {
            box-shadow: 0px 0px 15px rgba(0,0,0,0.2);
        }
        .header {
            margin: 0 0 10px 0;
        }
        ul.hidden {
            display: none;
            width: 100%;  /* Make list take up full width of the container */
        }
    </style>
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
</head>
"""
html += "<body>\n"
html += f"<h1>{title}</h1>\n"
html += "<h2>Variables</h2>\n"
html += '<div class="grid">\n'


for variable, data in sorted_variables.items():
    html += '<div class="container">\n'
    html += f'<h3 class="header">{variable}</h3>\n'
    html += '<ul class="hidden">\n'
    html += f'<li><strong>{data["long_name"]}</strong> </li>\n'
    for source in data["sources"]:
        html += f"<li>{source}</li>\n"
    html += "</ul>\n"
    html += "</div>\n"

# Aggregate variables by sources
from collections import defaultdict

source_dict = defaultdict(list)
for variable, data in sorted_variables.items():
    for source in data["sources"]:
        source_dict[source].append(variable)

html += """
</div>
<h2>Sources</h2>
<div class="grid">
"""

for source, variables in source_dict.items():
    html += '<div class="container">\n'
    html += f'<h3 class="header">{source}</h3>\n'
    html += '<ul class="hidden">\n'
    for variable in variables:
        html += f"<li>{variable}</li>\n"
    html += "</ul>\n"
    html += "</div>\n"

html += """
</div>
<script>
    $(document).ready(function() {
        $('.container').click(function() {
            $(this).find('.hidden').slideToggle();
        });
    });
</script>
</body>
</html>
"""

# Write the string to an HTML file
with open(f"{filename_without_ext}.html", "w") as f:
    f.write(html)
