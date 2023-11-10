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

## Running the App

### Running Locally with Python

To run this app on your local machine using Python:

1. Create a new Slack app using the `manifest-dev.yml` file.
2. Install the app into your Slack workspace.
3. Enable Socket Mode in your Slack app. This allows the app to communicate with Slack without needing a public URL.
4. Retrieve your OpenAI API key at https://platform.openai.com/account/api-keys.
5. Copy the `.env-example` file to `.env` and fill in the necessary environment variables.
6. Activate a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

7. Start the app:

   ```bash
   python main.py
   ```

### Running with Docker Compose

To run the app using Docker Compose:

1. Ensure Docker and Docker Compose are installed on your machine.
2. Follow steps 1 to 5 from the Python instructions to set up your environment.
3. Run the app:

   ```bash
   docker-compose up
   ```

This will build the Docker image and start the app according to the configuration in `docker-compose.yml` and your `.env` file.


## Deployment for Company Workspaces
For deploying in a company workspace, consider the security and confidentiality of information. You can fork this open-sourced app and deploy it on your managed infrastructure. The provided Dockerfile and docker-compose.yml can be used as a starting point for your deployment.


## Contributions

You're always welcome to contribute! :raised_hands:
When you make changes to the code in this project, please keep these points in mind:
- When making changes to the app, please avoid anything that could cause breaking behavior. If such changes are absolutely necessary due to critical reasons, like security issues, please start a discussion in GitHub Issues before making significant alterations.
- When you have the chance, please write some unit tests. Especially when you touch internal utility modules (e.g., `app/markdown.py` etc.) and add/edit the code that do not call any web APIs, writing tests should be relatively easy.
- Before committing your changes, be sure to run `./validate.sh`. The script runs black (code formatter), flake8 and pytype (static code analyzers).

## The License

The MIT License
