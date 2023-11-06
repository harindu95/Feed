function addStyle(css) {
    const linkElement = document.createElement('link');

    linkElement.setAttribute('rel', 'stylesheet');
    linkElement.setAttribute('type', 'text/css');
    linkElement.setAttribute('href', 'data:text/css;charset=UTF-8,' + encodeURIComponent(css));
    // linkElement.innerText = css;
    document.head.appendChild(linkElement);
};




const style = `
            .readable {
                font-family: Helvetica, Arial, sans-serif;
                font-size: 16px;
                background-color: #242424;
                color:white;
                position: fixed;
                z-index: 3;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                padding: 30px;
              }

            .readable h1{
                font-size:40px;
            }

            .readable p1{
                padding: 20px;
            }
              `;

window.onload = function () {
    var documentClone = document.cloneNode(true);
    var article = new Readability(documentClone).parse();
    var page = `
                <h1>${article.title}</h1>
                ${article.content}
            `
    console.error("Article: ", article.title, article.content);
    const readable = document.createElement('div');
    readable.classList.add('readable')
    readable.innerHTML = page;
    document.body.append(readable);
    var styleSheet = document.createElement("style");
    styleSheet.innerText = style;
     document.head.appendChild(styleSheet);
     addStyle(style);
};