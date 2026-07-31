// ExpenseFlow main JS

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

document.addEventListener('DOMContentLoaded', function () {
  // Sidebar toggle (mobile)
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('appSidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('show'));
    document.addEventListener('click', (e) => {
      if (window.innerWidth < 992 && sidebar.classList.contains('show') &&
          !sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('show');
      }
    });
  }

  // Dark mode toggle
  const darkToggle = document.getElementById('darkModeToggle');
  if (darkToggle) {
    darkToggle.addEventListener('click', function () {
      document.body.classList.toggle('dark-mode');
      const isDark = document.body.classList.contains('dark-mode');
      this.querySelector('i').className = isDark ? 'bi bi-sun' : 'bi bi-moon-stars';

      fetch('/settings/toggle-dark-mode/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken, 'Content-Type': 'application/json' },
        body: JSON.stringify({ dark_mode: isDark }),
      }).catch(() => {});
    });
  }

  // Delete confirmation modals
  document.querySelectorAll('[data-confirm-delete]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const form = document.getElementById(btn.dataset.confirmDelete);
      const modalEl = document.getElementById('deleteConfirmModal');
      if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modalEl.querySelector('#confirmDeleteBtn').onclick = function () {
          if (form) form.submit();
        };
        modal.show();
      } else if (form && confirm('Are you sure you want to delete this?')) {
        form.submit();
      }
    });
  });

  // Auto-submit filter selects on the expense list page
  document.querySelectorAll('.auto-filter').forEach(function (el) {
    el.addEventListener('change', function () {
      el.closest('form').submit();
    });
  });

  // Toggle custom date range fields
  const dateFilterSelect = document.getElementById('date_filter');
  const customDateFields = document.getElementById('customDateFields');
  if (dateFilterSelect && customDateFields) {
    const toggleCustom = () => {
      customDateFields.style.display = dateFilterSelect.value === 'custom' ? 'flex' : 'none';
    };
    dateFilterSelect.addEventListener('change', toggleCustom);
    toggleCustom();
  }
});
