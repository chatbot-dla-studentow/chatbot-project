// Wymuszenie tytułu strony - WSB Merito
(function() {
    const customTitle = 'Chatbot dla Studentów WSB Merito';
    
    // Ustaw tytuł natychmiast
    document.title = customTitle;
    
    // Monitoruj zmiany i wymuszaj nasz tytuł
    const observer = new MutationObserver(function(mutations) {
        if (document.title !== customTitle) {
            document.title = customTitle;
        }
    });
    
    // Obserwuj element title
    const titleElement = document.querySelector('title');
    if (titleElement) {
        observer.observe(titleElement, { 
            childList: true,
            characterData: true,
            subtree: true 
        });
    }
    
    // Dodatkowe wymuszenie co 100ms przez pierwsze 5 sekund
    let counter = 0;
    const interval = setInterval(function() {
        document.title = customTitle;
        counter++;
        if (counter > 50) {
            clearInterval(interval);
        }
    }, 100);
})();
