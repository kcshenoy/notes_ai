# notes_ai - IHateReading Chat Bot
IHateReading is a Chat Bot that allows you to query and ask questions on your own data. It allows you to sign in as your own user and query your own data.

## How it works:
There are a few components to the website that are all integrated together to provide a more seamless user experience.

### File Upload Area:
In the sidebar of the website, there is an area to upload your file(s) to be processed. Under it, you can tag your data to allow for an easier and more accurate search for later.
You may also see what tags you have previously added, so if you are adding more files to a specific subject, those would all have the same tag associated with it

<img width="337" alt="Screen Shot 2023-10-04 at 2 36 36 PM" src="https://github.com/kcshenoy/notes_ai/assets/59003979/02b2f100-dc96-4e6b-8ee9-6835f9f93516">

Once you have uploaded and tagged your data, you click the Process button. The text from your files will then be read and embedded using OpenAi's text-embedding-ada-002 model, and pushed
to a Qdrant vector database as a vector form of the chunks of text, along with metadata such as the filename, username, and tags.

### Query Details Area:
The center of the page consists of our main search portion. In this section, there are 3 inputs that you can fill out. The first is any tags that you would like to search. If you
want to find what tags you currently have in the database, simply open the sidebar and select "See all your tags". Secondly, you may also see what files you have saved under specific 
tags by clicking the "See files" button. From here, you can paste a filename which you would like to search through for your final query

<img width="1440" alt="Screen Shot 2023-10-04 at 2 43 50 PM" src="https://github.com/kcshenoy/notes_ai/assets/59003979/b3257e57-a142-4364-8a16-7db8a8f86d5a">


### Query Area:
All you have to do here is type out your query. All the specifications to your search have already been added above. Once the input is received and the "Query" button is clicked, 
the Qdrant data is filtered for your specific files, which match the specifications you inputted above.

<img width="1440" alt="Screen Shot 2023-10-04 at 2 45 42 PM" src="https://github.com/kcshenoy/notes_ai/assets/59003979/045de039-d930-44db-8eeb-a258fbcfc6c0">


### Demo Video:
https://youtu.be/23ogE4bXWek


