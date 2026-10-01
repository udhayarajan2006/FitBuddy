document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', () => {
      const button = form.querySelector('button[type="submit"], button:not([type])');
      if (!button || form.action.includes('admin-login')) return;
      button.disabled = true;
      button.dataset.originalText = button.textContent.trim();
      button.innerHTML = '<span class="spinner"></span> Building your plan…';
    });
  });

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) { event.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });
});
