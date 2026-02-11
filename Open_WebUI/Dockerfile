FROM ghcr.io/open-webui/open-webui:main

# Replace favicon with WSB Merito favicon
COPY custom/favicon.ico /app/build/static/favicon.ico
COPY custom/favicon.ico /app/build/favicon.ico
COPY custom/logo.png /app/build/static/favicon.png

# Copy WSB Merito logo for sidebar
COPY custom/logo.png /app/build/static/logo.png

# Copy custom CSS file for theming
COPY custom/custom.css /app/build/static/custom.css

# Copy custom JavaScript for title enforcement
COPY custom/custom.js /app/build/static/custom.js

# Change page title, inject custom JS, and update favicon links
RUN sed -i 's/<title>[^<]*<\/title>/<title>Chatbot dla Studentów WSB Merito<\/title>/g' /app/build/index.html && \
    sed -i 's/Open WebUI/Chatbot dla Studentów WSB Merito/g' /app/build/index.html && \
    sed -i 's/<\/head>/<script src="\/static\/custom.js"><\/script><\/head>/g' /app/build/index.html && \
    sed -i 's/href="[^"]*favicon[^"]*"/href="\/static\/favicon.ico"/g' /app/build/index.html && \
    sed -i 's/<head>/<head><link rel="icon" type="image\/x-icon" href="\/static\/favicon.ico">/g' /app/build/index.html
