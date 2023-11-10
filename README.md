# ChatGPT in Slack

Introducing a transformative app for Slack users, specifically designed to enhance your communication with [ChatGPT](https://openai.com/blog/chatgpt)!
This app enables seamless interaction with ChatGPT via Slack channels, optimizing your planning and writing processes by leveraging AI technology.

Discover the app's functionality by installing the live demo from https://bit.ly/chat-gpt-in-slack. 
Keep in mind that the live demo is personally hosted by [@seratch](https://github.com/seratch).
For corporate Slack workspaces, we strongly advise deploying the app on your own infrastructure using the guidelines provided below.

If you're looking for a sample app operating on [Slack's next-generation hosted platform](https://api.slack.com/future), check out https://github.com/seratch/chatgpt-on-deno 🙌

## How It Works

You can interact with ChatGPT like you do in the website. In the same thread, the bot remember what you already said.

<img src="https://user-images.githubusercontent.com/19658/222405498-867f5002-c8ba-4dc9-bd86-fddc5192070c.gif" width=450 />

Consider this realistic scenario: ask the bot to generate a business email for communication with your manager.

<img width="700" src="https://user-images.githubusercontent.com/19658/222609940-eb581361-eeea-441a-a300-96ecdbc23d0b.png">

With ChatGPT, you don't need to ask a perfectly formulated question at first. Adjusting the details after receiving the bot's initial response is a great approach.

<img width="700" src="https://user-images.githubusercontent.com/19658/222609947-b99ace0d-4c90-4265-940d-3fc373429b80.png">

Doesn't that sound cool? 😎

## Running the App on Your Local Machine

To run this app on your local machine, you only need to follow these simple steps:

* Create a new Slack app using the manifest-dev.yml file
* Install the app into your Slack workspace
* Retrieve your OpenAI API key at https://platform.openai.com/account/api-keys
* Copy the `.env-example` file to `.env` and fill in the necessary environment variables.
* Start the app

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Running the App for Company Workspaces

Confidentiality of information is top priority for businesses.

This app is open-sourced! so please feel free to fork it and deploy the app onto the infrastructure that you manage.
After going through the above local development process, you can deploy the app using `Dockerfile`, which is placed at the root directory.

The `Dockerfile` is designed to establish a WebSocket connection with Slack via Socket Mode.
This means that there's no need to provide a public URL for communication with Slack.

## Contributions

You're always welcome to contribute! :raised_hands:
When you make changes to the code in this project, please keep these points in mind:
- When making changes to the app, please avoid anything that could cause breaking behavior. If such changes are absolutely necessary due to critical reasons, like security issues, please start a discussion in GitHub Issues before making significant alterations.
- When you have the chance, please write some unit tests. Especially when you touch internal utility modules (e.g., `app/markdown.py` etc.) and add/edit the code that do not call any web APIs, writing tests should be relatively easy.
- Before committing your changes, be sure to run `./validate.sh`. The script runs black (code formatter), flake8 and pytype (static code analyzers).

## The License

The MIT License
