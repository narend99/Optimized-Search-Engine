from flask import Flask, request, jsonify
from search import search
from filter import Filter
from storage import DBStorage
import html
import subprocess

app = Flask(__name__)

styles = """
<style>
    .site {
  font-size: 1rem; /* Slightly increased font size */
  color: #2ecc71; /* Green color */
  font-weight: bold; /* Added bold font weight for emphasis */
  text-decoration: none; /* Remove underline by default */
  transition: color 0.3s ease-in-out; /* Smooth color transition */
}

.site:hover {
  color: #27ae60; /* Darker green on hover */
}

   .snippet {
  font-size: 1rem;
  color: #333;
  background-color: #e6f7ff; /* Light blue background */
  padding: 15px;
  border-radius: 5px;
  border: 1px solid #99c2ff; /* Slightly darker blue border */
  margin-bottom: 30px;
}

    .rel-button {
        cursor: pointer;
        color: blue;
    }
    
   .search-form {
    margin-bottom: 30px;
    text-align: center;
  }

  .search-input {
    padding: 10px;
    font-size: 16px;
    border: 1px solid #ddd;
    border-radius: 5px;
    width: 60%;
    margin-right: 10px;
  }

  .search-button,
  .block-button {
    background-color: #3498db;
    color: #fff;
    padding: 10px 15px;
    font-size: 16px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-left: 5px; /* Adjust the margin as needed */
  }

  .search-button:hover,
  .block-button:hover {
    background-color: #2980b9;
  }
</style>
<script>
const relevant = function(query, link){
    fetch("/relevant", {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
           "query": query,
           "link": link
          })
        });
}
</script>
"""

search_template = styles + """
<form action="/" method="post" class="search-form">
  <input type="text" name="query" class="search-input" placeholder="Enter your search...">
  <input type="submit" value="Search" class="search-button">
</form>

<button class="search-button block-button" onclick="executeBlockWebsite()">Block Website</button>
  <script>
function executeBlockWebsite() {
  fetch("/execute-block-website", {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  });
}
</script>

"""


result_template = """
<p class="site">{rank}: {link} <span class="rel-button" onclick='relevant("{query}", "{link}");'>Relevant</span></p>
<a href="{link}">{title}</a>
<p class="snippet">{snippet}</p>
"""


def show_search_form():
    return search_template


def run_search(query):
    results = search(query)
    fi = Filter(results)
    filtered = fi.filter()
    rendered = search_template
    filtered["snippet"] = filtered["snippet"].apply(lambda x: html.escape(x))
    for index, row in filtered.iterrows():
        rendered += result_template.format(**row)
    return rendered


@app.route("/", methods=['GET', 'POST'])
def search_form():
    if request.method == 'POST':
        query = request.form["query"]
        return run_search(query)
    else:
        return show_search_form()


@app.route("/relevant", methods=["POST"])
def mark_relevant():
    data = request.get_json()
    query = data["query"]
    link = data["link"]
    storage = DBStorage()
    storage.update_relevance(query, link, 10)
    return jsonify(success=True)

@app.route('/execute-block-website', methods=['POST'])
def execute_main_program():
    try:
        # Assuming website_blocker.py is in the same directory as this script
        subprocess.run(['python', 'website_blocker.py'])
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
