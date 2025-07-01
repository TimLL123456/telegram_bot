# Setup Ngrok webhook and expose localhost server to internet

1. **Download Ngrok**

    1. Install Chocolatey
    
        * Run `Get-ExecutionPolicy`. If it returns Restricted, then run Set-ExecutionPolicy AllSigned or Set-ExecutionPolicy Bypass -Scope Process

        * [Chocolatey Download Link](https://chocolatey.org/install)

    2. Run command

        ```
        Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        ```

    3. Install ngrok

        ```
        choco install ngrok
        ```

        * [Ngrok Download Link](https://dashboard.ngrok.com/get-started/setup/windows)

    4. Run command

        ```
        ngrok config add-authtoken [Your Authtoken]
        ```

2. Run ngrok

    1. Run python script (e.g., flask)

    2. Run ngrok to expose localhost to web server to the internet

        * example

            ```
            ngrok http [your localhost url]
            ngrok http http://127.0.0.1:5000
            ```

3. Set Webhook for telegram

    ```text
    https://api.telegram.org/bot[telegram bot token]/setWebhook?url=[your public url from Ngrok]
    ```

    setup_url = https://api.telegram.org/bot7879762613:AAFLGGOSyXpaGJWWnzTjt7A6lz0JYX4p7EY/setWebhook?url=https://84b98161c0dc999ef1c8a8aee9342f53.serveo.net/

    * copy the setup_url to the browser

