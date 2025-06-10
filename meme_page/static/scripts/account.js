function confirmLogout() {
    if (confirm("Are you sure you want to logout?")) {
      window.location.pathname = '/logout'
    };
  }
