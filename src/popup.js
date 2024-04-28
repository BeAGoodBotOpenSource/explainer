document.getElementById('autofill-button').addEventListener('click', function() {
  const spinner = document.getElementById('loading-spinner');
  const errorMessage = document.getElementById('error-message');
  const resultContainer = document.getElementById('result');
  const button = document.getElementById('autofill-button');

  // Display spinner and hide error message when starting the process
  spinner.style.display = 'inline-block';
  errorMessage.style.display = 'none';
  resultContainer.innerHTML = '';
  button.disabled = true;  // Disabling the button

  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    var tab = tabs[0];
    
    chrome.scripting.executeScript({
      target: {tabId: tab.id},
      func: getOuterHTML,
    }).then(result => {
      const htmlText = result[0].result;

      const isProduction = true;
      const server_url = isProduction ? 'https://explainer-backend.onrender.com/explain_news' : 'http://localhost:4000/explain_news'; 

      const formData = new FormData();
      formData.append('html_string', htmlText);

      fetch(server_url, {
        method: 'POST',
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          html_string: htmlText
        }),
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        spinner.style.display = 'none'; // Hide spinner when data is received
        button.disabled = false; // Enable the button again
        const resultContainer = document.getElementById('result');
        resultContainer.innerHTML = data.explanation;
        document.body.classList.add('expanded');
      })
      .catch(error => {
        console.error('Error:', error);
        spinner.style.display = 'none'; // Hide spinner on error
        errorMessage.style.display = 'block'; // Display error message
        button.disabled = false; // Enable the button again
      });
    });
  });
});

function getOuterHTML() {
  return document.documentElement.outerHTML;
}

function setValue(id, value) {
  document.getElementById(id).value = value;
}
