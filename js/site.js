  function toggleMenu() {
    document.getElementById('mobileMenu').classList.toggle('open');
  }

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('in');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  // Email buttons: keep native mailto, but always give visible feedback by
  // copying the address to the clipboard (handles machines with no mail client).
  (function () {
    let toast;
    let hideTimer;
    function showToast(msg) {
      if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast';
        document.body.appendChild(toast);
      }
      toast.textContent = msg;
      void toast.offsetWidth; // force reflow so the transition plays
      toast.classList.add('show');
      clearTimeout(hideTimer);
      hideTimer = setTimeout(() => toast.classList.remove('show'), 2600);
    }
    document.querySelectorAll('a[href^="mailto:"]').forEach(link => {
      link.addEventListener('click', () => {
        const addr = link.getAttribute('href').replace('mailto:', '').split('?')[0];
        // Always give feedback (surfaces the address even if nothing else works).
        showToast(addr);
        // Upgrade the message if we can copy to the clipboard.
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(addr)
            .then(() => showToast('Copied to clipboard: ' + addr))
            .catch(() => {});
        }
        // Native mailto still fires for anyone with a mail client set up.
      });
    });
  })();
