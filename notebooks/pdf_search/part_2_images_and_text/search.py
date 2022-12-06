from http import client, server
from inspect import classify_class_attrs
from docarray import Document
from jina import Client, Flow
import os
#search_format = "text" # text or image
### Using a text search term
# if search_format == "text":
#   search_term = "trilobite diagram"
#   query_doc = Document(text=search_term)
### Using an image search term
# if search_format == "image":

query_doc = Document(uri="/home/aswin/Documents/workshops/notebooks/pdf_search/part_2_images_and_text/image.png")
### Applying search filter

# [AnnLiteIndexer](https://hub.jina.ai/executor/7yypg8qk?utm_source=notebook-pdf-search-tables) allows you to apply MongoDB-style filters. Check the [Executor's README](https://hub.jina.ai/executor/7yypg8qk) to learn more.
# you can use any combination of text/table/image

element_type = [
    "text", 
    "image" 
    "table"
    ]
filter = {
    "element_type": {
        "$in": element_type,
    }
}
### Performing the search
client = Client(host="grpc://0.0.0.0:60787")
results = client.post(
    "/search",
    query_doc,
    request_size=1,
    parameters={
        "filter": filter
    },
    show_progress=True, 
    target_executor="(search_*|all_*)"
    )
### Show results

# If the results are text or table, just print it out. Otherwise we can plot the image matches in the notebook.

# Note: Due to the content of the PDFs, *most* results will be text results. You can change the `filter` above to select instead for tables and/or images.

# The `render()` function below is needed to render the search results in a notebook. In the real world you'd probably want to do something different, but this quick, hacky code (specifically tailored for notebooks, not real world) will serve for now.
import pandas as pd
import matplotlib.pyplot as plt

def render(docarray):
  for idx, doc in enumerate(docarray):
    if doc.tags["element_type"] == "image":
      os.makedirs("images", exist_ok=True)
      filename = f"images/{idx}-{doc.id}.png"
      doc.set_image_tensor_inv_normalization(channel_axis=0)
      doc.save_image_tensor_to_file(filename, channel_axis=0)
      image=plt.imread(filename)
      fig=plt.figure()
      plt.axis('off')
      plt.imshow(image)

    elif doc.tags["element_type"] == "table":
      os.makedirs("csvs", exist_ok=True)
      filename = f"csvs/{idx}-{doc.id}.csv" 
      with open(filename, "w") as file:
        file.write(doc.tags["table_content"])
      df = pd.read_csv(filename)
      print(df)
      
    else:
      print(doc.text)
print(results[0].uri)