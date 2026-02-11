FROM ghcr.io/open-webui/open-webui:main

# Copy WSB Merito favicon to multiple locations for compatibility
COPY custom/favicon.ico /app/build/static/favicon.ico
COPY custom/favicon.ico /app/build/favicon.ico
COPY custom/favicon.ico /app/favicon.ico
COPY custom/favicon.ico /app/build/static/favicon.png
COPY custom/favicon.ico /app/build/static/favicon-32x32.png
COPY custom/favicon.ico /app/build/static/favicon-16x16.png
COPY custom/favicon.ico /app/build/static/apple-touch-icon.png

# Copy WSB Merito logo for sidebar
COPY custom/logo.png /app/build/static/logo.png

# Copy custom CSS file for theming
COPY custom/custom.css /app/build/static/custom.css

# Copy custom JavaScript for title enforcement
COPY custom/custom.js /app/build/static/custom.js

# Change page title, inject custom JS, and update all favicon references
RUN sed -i 's/<title>[^<]*<\/title>/<title>Chatbot dla Studentów WSB Merito<\/title>/g' /app/build/index.html && \
    sed -i 's/Open WebUI/Chatbot dla Studentów WSB Merito/g' /app/build/index.html && \
    sed -i 's/<\/head>/<link rel="stylesheet" href="\/static\/custom.css"><script src="\/static\/custom.js"><\/script><\/head>/g' /app/build/index.html && \
    # Remove ALL favicon references from entire document \
    sed -i '/<link[^>]*rel="icon"[^>]*>/d' /app/build/index.html && \
    sed -i '/<link[^>]*rel="shortcut icon"[^>]*>/d' /app/build/index.html && \
    sed -i '/<link[^>]*rel="apple-touch-icon"[^>]*>/d' /app/build/index.html && \
    sed -i '/rel="icon"/d' /app/build/index.html && \
    sed -i '/favicon/Id' /app/build/index.html && \
    # Add new favicon links at the beginning of <head> \
    sed -i 's/<head>/<head>\n  <link rel="icon" type="image\/x-icon" href="\/static\/favicon.ico?v=3">\n  <link rel="shortcut icon" type="image\/x-icon" href="\/static\/favicon.ico?v=3">\n  <link rel="icon" type="image\/png" sizes="32x32" href="\/static\/favicon-32x32.png?v=3">\n  <link rel="icon" type="image\/png" sizes="16x16" href="\/static\/favicon-16x16.png?v=3">\n  <link rel="apple-touch-icon" href="\/static\/apple-touch-icon.png?v=3">/g' /app/build/index.html && \
    # Remove old Open WebUI favicons \
    rm -f /app/build/static/favicon.svg /app/build/static/favicon-96x96.png /app/build/static/favicon-dark.png
