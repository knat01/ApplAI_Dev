function extractJobDetails() {
  const jobTitle = document.querySelector('.jobs-unified-top-card__job-title')?.textContent.trim();
  const company = document.querySelector('.jobs-unified-top-card__company-name')?.textContent.trim();
  const location = document.querySelector('.jobs-unified-top-card__bullet')?.textContent.trim();
  const description = document.querySelector('.jobs-description-content__text')?.textContent.trim();

  return {
    jobTitle,
    company,
    location,
    description
  };
}

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === "getJobDetails") {
    sendResponse(extractJobDetails());
  }
});

// Add "Apply with AI" button
const applyButton = document.querySelector('.jobs-apply-button');
if (applyButton) {
  const aiApplyButton = document.createElement('button');
  aiApplyButton.textContent = 'Apply with AI';
  aiApplyButton.classList.add('ai-apply-button');
  aiApplyButton.addEventListener('click', function() {
    const jobDetails = extractJobDetails();
    chrome.runtime.sendMessage({action: "applyWithAI", jobDetails: jobDetails});
  });
  applyButton.parentNode.insertBefore(aiApplyButton, applyButton.nextSibling);
}
