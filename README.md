# Rich Audio Presence (alpha)
## Description
This is a small Python app that sets your Discord activity to the title and artist of whatever you're listening to.
## Requirements
Please make sure that you have Python 3.7, 3.8, or 3.9 installed, as one of the dependencies only works on those 3 versions.\
This app only works on Windows 10/11.
## Using the app
I will be making an executable in the future, but for now, you'll need to clone this repository and follow these steps.
- Clone the repository `git clone https://github.com/franklinmoy3/RichAudioPresence.git rich-audio`
- Change into the newly-cloned `rich-audio` directory (`cd rich-audio`)
- Then, install the pip dependencies using `pip install -r requirements.txt`
- Create a `secrets.py` file in the `app` folder with the following contents:
```python
# Fill in the <> fields after creating a new application on Discord's Developer Portal
app_id = int(<DISCORD_APPLICATION_ID>)
large_image_key = str("<LARGE_IMAGE_KEY>")
small_image_key = str("<SMALL_IMAGE_KEY>")
```
- Launch Discord before running the app
- Run the app by running the app/app.py file. For example, with Python 3.9: `python3.9 app.py`
