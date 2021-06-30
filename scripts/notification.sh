#!/bin/sh

# Get the token from Travis environment vars and build the bot URL:
BOT_URL="https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage"

# Set formatting for the message. Can be either "Markdown" or "HTML"
PARSE_MODE="Markdown"

# Define send message function. parse_mode can be changed to
# HTML, depending on how you want to format your message:
send_msg () {
    curl -s -X POST ${BOT_URL} \
        -d chat_id=$TELEGRAM_CHAT_ID \
        -d text="$1" \
        -d parse_mode=${PARSE_MODE}
}

# Send message to the bot with some pertinent details about the job
# Note that for Markdown, you need to escape any backtick (inline-code)
# characters, since they're reserved in bash
send_msg "
----------------------------------------------------
GitHub Actions build *${GITHUB_JOB_STATUS}!*
\`Repository:    ${GITHUB_REPOSITORY}\`
\`Branch:        ${GITHUB_REF}\`
\`Environment:   ${TOXENV}\`
\`Run Number/Run ID:    ${GITHUB_RUN_NUMBER}/${GITHUB_RUN_ID}\`
*Commit Msg:*
${GITHUB_COMMIT_MESSAGE}

[See complete job log here](${GITHUB_RUN_URL})
-----------------------------------------------------
"